# Configuração do Dashboard GLPI - MySQL
# Configure os dados de conexão com seu banco GLPI

# ==============================================
# CONFIGURAÇÕES DO BANCO DE DADOS MYSQL
# ==============================================

DB_TYPE = 'mysql'

# IMPORTANTE: Configure esses dados para conectar ao banco GLPI
# Dashboard requer configuração válida para funcionar
MYSQL_CONFIG = {
    'host': '10.26.0.19',        # ← IP do seu servidor MySQL
    'port': 3306,               # ← Porta do MySQL (normalmente 3306)
    'user': 'root',      # ← Usuário do banco GLPI
    'password': '3128*',    # ← Senha do banco GLPI  
    'database': 'glpi_db',   # ← Nome do banco GLPI (ex: glpi, glpidb)
    'charset': 'utf8mb4',
    'autocommit': True
}

# Configurações não utilizadas (manter para compatibilidade)
POSTGRESQL_CONFIG = {}
SQLITE_CONFIG = {}

# ==============================================
# CONFIGURAÇÕES DA APLICAÇÃO
# ==============================================

SECRET_KEY = 'dashboard-glpi-sesma-2025-chave-secreta-forte'
DEBUG = True

# ==============================================
# CONFIGURAÇÕES ESPECÍFICAS DO GLPI
# ==============================================

# Tabelas principais do GLPI
GLPI_TABLES = {
    'tickets': 'glpi_tickets',
    'users': 'glpi_users', 
    'categories': 'glpi_itilcategories',
    'locations': 'glpi_locations',
    'entities': 'glpi_entities',
    'groups': 'glpi_groups'
}

# Status de tickets GLPI
TICKET_STATUS = {
    1: 'Novo',
    2: 'Em Andamento (Atribuído)', 
    3: 'Planejado',
    4: 'Pendente',
    5: 'Solucionado',
    6: 'Fechado'
}

# Mapear status para dashboard
STATUS_MAPPING = {
    'novo': [1],
    'atribuido': [2, 3],
    'pendente': [4],
    'fechado': [5, 6]
}

DEFAULT_FILTERS = {
    'periodo_dias': 30,
    'limite_resultados': 100
}

# ==============================================
# COMO CONFIGURAR:
# ==============================================
"""
1. ENCONTRAR DADOS DE CONEXÃO DO GLPI:
   Procure o arquivo: config/config_db.php no seu servidor GLPI
   
   Exemplo do conteúdo:
   $CFG_GLPI["dbhost"] = "localhost";
   $CFG_GLPI["dbuser"] = "glpi";
   $CFG_GLPI["dbpassword"] = "sua_senha";
   $CFG_GLPI["dbdefault"] = "glpi";

2. CONFIGURE MYSQL_CONFIG ACIMA com esses dados

3. TESTE A CONEXÃO:
   python -c "from database import *; import config; db = DatabaseConnection({'DB_TYPE': config.DB_TYPE, 'MYSQL_CONFIG': config.MYSQL_CONFIG}); print(db.test_connection())"
"""