from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import json
import os
from database import DatabaseConnection, GLPIDataService

app = Flask(__name__)

# Configuração da aplicação - prioriza variáveis de ambiente
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui')

# Configuração para produção
if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True

# Inicializar conexão com banco
db_connection = None
glpi_service = None

def init_database():
    """Inicializa a conexão com o banco de dados"""
    global db_connection, glpi_service
    
    # Priorizar variáveis de ambiente para produção
    db_config = None
    
    # Verificar se há configuração via variáveis de ambiente (para produção)
    if os.environ.get('DATABASE_URL'):
        # Parse da URL do banco (formato: mysql://user:pass@host:port/dbname)
        import urllib.parse as urlparse
        url = urlparse.urlparse(os.environ.get('DATABASE_URL'))
        
        db_config = {
            'DB_TYPE': 'mysql',
            'MYSQL_CONFIG': {
                'host': url.hostname,
                'port': url.port or 3306,
                'user': url.username,
                'password': url.password,
                'database': url.path[1:],  # Remove leading slash
                'charset': 'utf8mb4',
                'autocommit': True
            }
        }
    elif all(os.environ.get(key) for key in ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']):
        # Configuração individual via variáveis de ambiente
        db_config = {
            'DB_TYPE': 'mysql',
            'MYSQL_CONFIG': {
                'host': os.environ.get('DB_HOST'),
                'port': int(os.environ.get('DB_PORT', 3306)),
                'user': os.environ.get('DB_USER'),
                'password': os.environ.get('DB_PASSWORD'),
                'database': os.environ.get('DB_NAME'),
                'charset': 'utf8mb4',
                'autocommit': True
            }
        }
    
    # Fallback para arquivo config.py local
    if not db_config:
        try:
            if os.path.exists('config.py'):
                import config
                
                # Verificar se está configurado
                mysql_config = config.MYSQL_CONFIG
                if (mysql_config.get('user') in ['SEU_USUARIO', ''] or 
                    mysql_config.get('database') in ['NOME_BANCO', ''] or
                    mysql_config.get('password') in ['SUA_SENHA', '']):
                    
                    print("AVISO: Configuração encontrada, mas ainda com dados de exemplo")
                    print("Para usar dados reais, edite o arquivo config.py")
                    print("Veja instruções em: CONFIGURAR_BANCO.md")
                    print("Sistema aguardando configuração do banco de dados...")
                    return
                
                db_config = {
                    'DB_TYPE': config.DB_TYPE,
                    'MYSQL_CONFIG': config.MYSQL_CONFIG,
                    'POSTGRESQL_CONFIG': getattr(config, 'POSTGRESQL_CONFIG', {}),
                    'SQLITE_CONFIG': getattr(config, 'SQLITE_CONFIG', {})
                }
            else:
                print("Arquivo config.py não encontrado")
                print("Sistema aguardando configuração do banco de dados...")
                return
        except Exception as e:
            print(f"Erro ao carregar config.py: {str(e)}")
            print("Sistema aguardando configuração do banco de dados...")
            return
    
    # Tentar conectar com a configuração encontrada
    try:
        db_connection = DatabaseConnection(db_config)
        glpi_service = GLPIDataService(db_connection)
        
        # Testar conexão
        test_result = db_connection.test_connection()
        if test_result['success']:
            print("Conexão com banco de dados estabelecida com sucesso")
        else:
            print(f"Erro na conexão com banco: {test_result['error']}")
            print("Sistema aguardando configuração correta do banco...")
            db_connection = None
            glpi_service = None
            
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {str(e)}")
        print("Sistema aguardando configuração do banco de dados...")
        db_connection = None
        glpi_service = None

# Inicializar banco na inicialização da app
init_database()

@app.route('/')
def dashboard():
    """Rota principal do dashboard"""
    return render_template('dashboard.html')

@app.route('/api/metrics')
def get_metrics():
    """API para obter métricas principais"""
    filters = request.args.to_dict()
    
    if not glpi_service:
        return jsonify({
            'error': 'Database not configured',
            'message': 'Para usar o dashboard, configure a conexão com o banco de dados no arquivo config.py'
        }), 503
    
    try:
        metrics = glpi_service.get_metrics(filters)
        return jsonify(metrics)
    except Exception as e:
        print(f"Erro ao obter métricas do banco: {str(e)}")
        return jsonify({
            'error': 'Database connection failed',
            'message': 'Erro na conexão com o banco de dados'
        }), 500

@app.route('/api/chart-data/<chart_type>')
def get_chart_data(chart_type):
    """API para obter dados dos gráficos"""
    filters = request.args.to_dict()
    
    if not glpi_service:
        return jsonify({
            'error': 'Database not configured',
            'message': 'Para usar o dashboard, configure a conexão com o banco de dados no arquivo config.py'
        }), 503
    
    try:
        if chart_type == 'requisitante':
            data = glpi_service.get_tickets_by_requester(filters)
            return jsonify({
                'labels': [item['name'] for item in data],
                'data': [item['count'] for item in data],
                'backgroundColor': '#3498db'
            })
        
        elif chart_type == 'categoria':
            data = glpi_service.get_tickets_by_category(filters)
            return jsonify({
                'labels': [item['category'] for item in data],
                'data': [item['count'] for item in data],
                'backgroundColor': '#e67e22'
            })
        
        elif chart_type == 'localizacao':
            data = glpi_service.get_tickets_by_location(filters)
            return jsonify({
                'labels': [item['location'] for item in data],
                'data': [item['count'] for item in data],
                'backgroundColor': '#27ae60'
            })
        
        elif chart_type == 'tipos':
            data = glpi_service.get_tickets_by_type(filters)
            return jsonify({
                'labels': [item['type'] for item in data],
                'data': [item['count'] for item in data],
                'backgroundColor': [item['color'] for item in data]
            })
        
        return jsonify({'error': 'Chart type not found'}), 404
        
    except Exception as e:
        print(f"Erro ao obter dados do gráfico {chart_type}: {str(e)}")
        return jsonify({
            'error': 'Database connection failed',
            'message': 'Erro na conexão com o banco de dados'
        }), 500

@app.route('/api/filters/options')
def get_filter_options():
    """API para obter opções dos filtros"""
    if not glpi_service:
        return jsonify({
            'error': 'Database not configured',
            'message': 'Para usar filtros, configure a conexão com o banco de dados no arquivo config.py'
        }), 503
    
    try:
        # Buscar opções do banco de dados
        categorias = glpi_service.get_available_categories()
        requisitantes = glpi_service.get_available_requesters()
        
        return jsonify({
            'categorias': categorias,
            'status': [
                {'value': 'aberto', 'label': 'Aberto'},
                {'value': 'pendente', 'label': 'Pendente'},
                {'value': 'atribuido', 'label': 'Atribuído'},
                {'value': 'fechado', 'label': 'Fechado'}
            ],
            'requisitantes': requisitantes
        })
    except Exception as e:
        print(f"Erro ao obter opções de filtros: {str(e)}")
        return jsonify({
            'error': 'Database connection failed',
            'message': 'Erro na conexão com o banco de dados'
        }), 500

@app.route('/api/test-db')
def test_database():
    """API para testar conexão com banco de dados"""
    if db_connection and glpi_service:
        result = db_connection.test_connection()
        if result['success']:
            result['message'] = 'Dashboard conectado ao banco GLPI com sucesso'
            result['mode'] = 'production'
        return jsonify(result)
    else:
        return jsonify({
            'success': False,
            'mode': 'not_configured', 
            'message': 'Banco de dados não configurado',
            'instruction': 'Para usar o dashboard, configure a conexão com o banco no arquivo config.py',
            'help': 'Veja instruções em CONFIGURAR_BANCO.md'
        })

@app.route('/api/export/<format>')
def export_data(format):
    """API para exportar dados em diferentes formatos"""
    filters = request.args.to_dict()
    
    if not glpi_service:
        return jsonify({
            'error': 'Database not configured',
            'message': 'Para exportar dados, configure a conexão com o banco de dados'
        }), 503
    
    # Implementar lógica de exportação baseada no banco de dados
    return jsonify({
        'message': f'Dados exportados em formato {format}',
        'filters_applied': filters,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"Dashboard GLPI - SESMA disponível em:")
    print(f"   http://{host}:{port}")
    
    # Executar aplicação
    app.run(debug=app.config['DEBUG'], host=host, port=port)