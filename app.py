# app.py
#
# Servidor Flask que expõe as rotas da API e serve o dashboard.
# ATUALIZADO: Adicionada lógica para o gráfico de barras de Incidentes vs. Requisições por Mês.

from flask import Flask, jsonify, request, render_template, Response
from flask_cors import CORS
import config
from database import DatabaseConnection
import logging
from collections import defaultdict
from datetime import date
from typing import List, Dict, Any, Optional

app = Flask(__name__)
CORS(app) 

db = DatabaseConnection({'DB_TYPE': config.DB_TYPE, 'MYSQL_CONFIG': config.MYSQL_CONFIG})

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CONSTANTES GLOBAIS ---
GLPI_STATUS_MAP = {
    1: 'Novo', 2: 'Em Andamento (Atribuído)', 3: 'Pendente',
    4: 'Em Andamento (Planejado)', 5: 'Solucionado', 6: 'Fechado',
}
STATUS_NOVO = [1]
STATUS_EM_ATENDIMENTO = [2, 4]
STATUS_PENDENTE = [3]
STATUS_RESOLVIDO = [5, 6]

# --- FUNÇÕES AUXILIARES DE PROCESSAMENTO DE DADOS ---

# ... (as funções calculate_monthly_counts e calculate_counts continuam as mesmas) ...
def calculate_monthly_counts(data: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
    if not data: return {'labels': [], 'data': []}
    monthly_counts = defaultdict(int)
    for item in data:
        if ticket_date := item.get('date'):
            key = f"{ticket_date.year}-{ticket_date.month:02d}"
            monthly_counts[key] += 1
    sorted_keys = sorted(monthly_counts.keys())
    month_abbrs = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
    labels = [f"{month_abbrs.get(int(k.split('-')[1]), '?')}/{k.split('-')[0][-2:]}" for k in sorted_keys]
    data_values = [monthly_counts[k] for k in sorted_keys]
    return {'labels': labels, 'data': data_values}

def calculate_counts(data: List[Dict[str, Any]], field: str, top_n: Optional[int] = None, 
                     use_status_map: bool = False, include_others: bool = True, 
                     exclude_values: Optional[List[str]] = None) -> Dict[str, List[Any]]:
    counts = defaultdict(int)
    for item in data:
        value = item.get(field)
        if use_status_map: value = GLPI_STATUS_MAP.get(value, 'Desconhecido')
        counts[value or 'Desconhecido'] += 1
    if exclude_values:
        for value_to_exclude in exclude_values:
            if value_to_exclude in counts:
                del counts[value_to_exclude]
    sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    if top_n and len(sorted_counts) > top_n:
        top_items = sorted_counts[:top_n]
        labels = [name for name, _ in top_items]
        data_values = [count for _, count in top_items]
        if include_others:
            other_count = sum(count for _, count in sorted_counts[top_n:])
            if other_count > 0:
                labels.append('Outros')
                data_values.append(other_count)
    else:
        labels = [name for name, _ in sorted_counts]
        data_values = [count for _, count in sorted_counts]
    return {'labels': labels, 'data': data_values}


# NOVO: Função para o gráfico de barras Incidentes vs. Requisições por Mês
def get_incidents_vs_requests_by_month(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Agrupa os chamados por mês, separando as contagens de Incidentes e Requisições.
    """
    if not data:
        return {'labels': [], 'datasets': []}

    # Usando defaultdict para facilitar a contagem
    monthly_breakdown = defaultdict(lambda: {'Incidentes': 0, 'Requisições': 0})
    
    for item in data:
        # Supondo que o tipo do chamado está no campo 'type' (1=Incidente, 2=Requisição)
        # Ajuste o nome do campo e os valores conforme sua base de dados
        ticket_type = item.get('type') 
        ticket_date = item.get('date')

        if ticket_type and ticket_date:
            key = f"{ticket_date.year}-{ticket_date.month:02d}"
            if ticket_type == 1: # Incidente
                monthly_breakdown[key]['Incidentes'] += 1
            elif ticket_type == 2: # Requisição
                monthly_breakdown[key]['Requisições'] += 1

    if not monthly_breakdown:
        return {'labels': [], 'datasets': []}
        
    sorted_keys = sorted(monthly_breakdown.keys())
    month_abbrs = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
    labels = [f"{month_abbrs.get(int(k.split('-')[1]), '?')}/{k.split('-')[0][-2:]}" for k in sorted_keys]
    
    incident_data = [monthly_breakdown[k]['Incidentes'] for k in sorted_keys]
    request_data = [monthly_breakdown[k]['Requisições'] for k in sorted_keys]

    return {
        'labels': labels,
        'datasets': [
            {'label': 'Incidentes', 'data': incident_data},
            {'label': 'Requisições', 'data': request_data}
        ]
    }


# --- ROTAS FLASK ---
@app.route('/')
def dashboard() -> str:
    # ... (código da rota continua o mesmo) ...
    return render_template('index.html')

@app.route('/api/dashboard-data', methods=['GET'])
def get_dashboard_data() -> Response:
    logging.info("Recebida requisição para obter dados do dashboard.")
    args = request.args
    
    # MODIFICADO: Adicionado 'T.type' à consulta SQL para diferenciar Incidentes de Requisições
    sql_query = """
        SELECT T.id, T.status, T.date, T.type, U.name AS requisitante, MAX(Tech.name) AS tecnico,
               C.completename AS categoria, L.completename AS localizacao
        FROM glpi_tickets AS T
        LEFT JOIN glpi_users AS U ON U.id = T.users_id_recipient 
        LEFT JOIN glpi_itilcategories AS C ON C.id = T.itilcategories_id
        LEFT JOIN glpi_locations AS L ON L.id = T.locations_id
        LEFT JOIN glpi_tickets_users AS TU ON TU.tickets_id = T.id AND TU.type = 2
        LEFT JOIN glpi_users AS Tech ON Tech.id = TU.users_id
        WHERE T.is_deleted = 0
    """
    # ... (lógica de filtros continua a mesma) ...
    params, conditions = [], []
    if status := args.get('status'):
        if status_id := next((k for k, v in GLPI_STATUS_MAP.items() if v == status), None):
            conditions.append("T.status = %s"); params.append(status_id)
    if requisitante := args.get('requisitante'):
        conditions.append("U.name LIKE %s"); params.append(f"%{requisitante}%")
    if start_date := args.get('start_date'):
        conditions.append("T.date >= %s"); params.append(f"{start_date} 00:00:00")
    if end_date := args.get('end_date'):
        conditions.append("T.date <= %s"); params.append(f"{end_date} 23:59:59")
    if conditions: sql_query += " AND " + " AND ".join(conditions)
    sql_query += " GROUP BY T.id"
    if tecnico := args.get('tecnico'):
        sql_query += " HAVING tecnico LIKE %s"
        params.append(f"%{tecnico}%")

    raw_data = db.execute_query(sql_query, tuple(params))
    
    if raw_data is None:
        return jsonify({"error": "Falha ao buscar dados da base de dados."}), 500
    
    # --- Cálculo de Métricas ---
    metrics = { # ... (lógica de métricas continua a mesma) ...
        'total-chamados': len(raw_data), 'chamados-novos': 0, 'total-atribuido': 0,
        'total-pendente': 0, 'total-resolvido': 0, 'chamados-abertos-dia': 0
    }
    today = date.today()
    for ticket in raw_data:
        status_id = ticket.get('status')
        if status_id in STATUS_NOVO: metrics['chamados-novos'] += 1
        elif status_id in STATUS_EM_ATENDIMENTO: metrics['total-atribuido'] += 1
        elif status_id in STATUS_PENDENTE: metrics['total-pendente'] += 1
        elif status_id in STATUS_RESOLVIDO: metrics['total-resolvido'] += 1
        if ticket_date := ticket.get('date'):
            if ticket_date.date() == today:
                metrics['chamados-abertos-dia'] += 1
    
    # --- Montagem da Resposta Final ---
    response_data = {
        "metrics": metrics,
        "charts": {
            "requisitante": calculate_counts(raw_data, 'requisitante', top_n=5, include_others=False),
            "categoria": calculate_counts(raw_data, 'categoria', top_n=5),
            "localizacao": calculate_counts(raw_data, 'localizacao', top_n=5, include_others=False, exclude_values=['Desconhecido']),
            "tipos": calculate_counts(raw_data, 'status', use_status_map=True),
            "chamados_por_mes": calculate_monthly_counts(raw_data),
            # NOVO: Adicionando os dados do novo gráfico à resposta
            "incidents_requests_monthly": get_incidents_vs_requests_by_month(raw_data)
        }
    }
    return jsonify(response_data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)