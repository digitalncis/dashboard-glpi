"""
Módulo de conexão com banco de dados GLPI
Suporta MySQL, PostgreSQL e SQLite
"""

import pymysql
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

# Configure o logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Gerenciador de conexão com banco de dados GLPI"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        self.db_type = config.get('DB_TYPE', 'mysql')
        
    def connect(self) -> bool:
        """Estabelece conexão com o banco de dados"""
        try:
            if self.db_type == 'mysql':
                return self._connect_mysql()
            elif self.db_type == 'postgresql':
                return self._connect_postgresql()
            elif self.db_type == 'sqlite':
                return self._connect_sqlite()
            else:
                logger.error(f"Tipo de banco não suportado: {self.db_type}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao conectar com o banco: {str(e)}")
            return False
    
    def _connect_mysql(self) -> bool:
        """Conecta com MySQL/MariaDB"""
        mysql_config = self.config['MYSQL_CONFIG']
        
        self.connection = pymysql.connect(
            host=mysql_config['host'],
            port=mysql_config['port'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            database=mysql_config['database'],
            charset=mysql_config.get('charset', 'utf8mb4'),
            autocommit=mysql_config.get('autocommit', True),
            cursorclass=pymysql.cursors.DictCursor
        )
        
        logger.info("Conectado com sucesso ao MySQL")
        return True
    
    def _connect_postgresql(self) -> bool:
        """Conecta com PostgreSQL"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            pg_config = self.config['POSTGRESQL_CONFIG']
            
            self.connection = psycopg2.connect(
                host=pg_config['host'],
                port=pg_config['port'],
                user=pg_config['user'],
                password=pg_config['password'],
                database=pg_config['database'],
                cursor_factory=RealDictCursor
            )
            
            logger.info("Conectado com sucesso ao PostgreSQL")
            return True
            
        except ImportError:
            logger.error("psycopg2 não instalado. Execute: pip install psycopg2-binary")
            return False
    
    def _connect_sqlite(self) -> bool:
        """Conecta com SQLite"""
        import sqlite3
        
        sqlite_config = self.config['SQLITE_CONFIG']
        
        self.connection = sqlite3.connect(sqlite_config['database'])
        self.connection.row_factory = sqlite3.Row
        
        logger.info("Conectado com sucesso ao SQLite")
        return True
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Executa uma consulta SELECT e retorna os resultados"""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Converter resultados para lista de dicionários
            if self.db_type == 'mysql':
                results = cursor.fetchall()
            elif self.db_type == 'postgresql':
                results = [dict(row) for row in cursor.fetchall()]
            else:  # sqlite
                results = [dict(row) for row in cursor.fetchall()]
            
            cursor.close()
            
            logger.info(f"Query executada com sucesso. {len(results)} registros retornados.")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao executar query: {str(e)}")
            logger.error(f"Query: {query}")
            return []
    
    def test_connection(self) -> Dict[str, Any]:
        """Testa a conexão e retorna informações do banco"""
        try:
            if not self.connect():
                return {"success": False, "error": "Falha na conexão"}
            
            # Teste básico - contar tickets
            query = """
            SELECT 
                COUNT(*) as total_tickets,
                COUNT(CASE WHEN status = 1 THEN 1 END) as novos,
                COUNT(CASE WHEN status IN (2,3) THEN 1 END) as atribuidos,
                COUNT(CASE WHEN status = 4 THEN 1 END) as pendentes,
                COUNT(CASE WHEN status IN (5,6) THEN 1 END) as fechados
            FROM glpi_tickets 
            WHERE is_deleted = 0
            """
            
            results = self.execute_query(query)
            
            if results:
                return {
                    "success": True,
                    "database_info": {
                        "type": self.db_type,
                        "total_tickets": results[0]["total_tickets"],
                        "breakdown": {
                            "novos": results[0]["novos"],
                            "atribuidos": results[0]["atribuidos"], 
                            "pendentes": results[0]["pendentes"],
                            "fechados": results[0]["fechados"]
                        }
                    }
                }
            else:
                return {"success": False, "error": "Não foi possível consultar dados"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def close(self):
        """Fecha a conexão com o banco"""
        if self.connection:
            self.connection.close()
            logger.info("Conexão fechada")


class GLPIDataService:
    """Serviço para consultas específicas do GLPI"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        
    def get_metrics(self, filters: Dict = None) -> Dict[str, int]:
        """Obtém métricas principais do dashboard"""
        
        # Query base
        base_query = """
        SELECT 
            COUNT(*) as total_chamados,
            COUNT(CASE WHEN status = 1 THEN 1 END) as chamados_novos,
            COUNT(CASE WHEN status IN (2,3) THEN 1 END) as total_atribuido,
            COUNT(CASE WHEN status = 4 THEN 1 END) as total_pendente,
            COUNT(CASE WHEN status IN (5,6) THEN 1 END) as total_fechado
        FROM glpi_tickets t
        WHERE t.is_deleted = 0
        """
        
        # Adicionar filtros
        where_conditions = []
        params = []
        
        if filters:
            if filters.get('status'):
                status_map = {
                    'novo': [1],
                    'atribuido': [2, 3],
                    'pendente': [4],
                    'fechado': [5, 6]
                }
                status_values = status_map.get(filters['status'], [])
                if status_values:
                    placeholders = ','.join(['%s'] * len(status_values))
                    where_conditions.append(f"t.status IN ({placeholders})")
                    params.extend(status_values)
            
            if filters.get('categoria'):
                where_conditions.append("t.itilcategories_id = %s")
                params.append(filters['categoria'])
            
            if filters.get('periodo'):
                dias = int(filters['periodo'])
                where_conditions.append("t.date >= %s")
                data_inicio = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
                params.append(data_inicio)
        
        # Montar query final
        if where_conditions:
            query = base_query + " AND " + " AND ".join(where_conditions)
        else:
            query = base_query
        
        results = self.db.execute_query(query, tuple(params) if params else None)
        
        if results:
            return results[0]
        else:
            return {
                'total_chamados': 0,
                'chamados_novos': 0,
                'total_atribuido': 0,
                'total_pendente': 0,
                'total_fechado': 0
            }
    
    def get_tickets_by_requester(self, filters: Dict = None) -> List[Dict]:
        """Obtém contagem de tickets por requisitante"""
        
        query = """
        SELECT 
            CONCAT(u.firstname, ' ', u.realname) as name,
            COUNT(t.id) as count
        FROM glpi_tickets t
        JOIN glpi_users u ON t.users_id_recipient = u.id
        WHERE t.is_deleted = 0
        """
        
        where_conditions = []
        params = []
        
        # Aplicar filtros
        if filters:
            if filters.get('requisitante'):
                where_conditions.append("(u.firstname LIKE %s OR u.realname LIKE %s)")
                search_term = f"%{filters['requisitante']}%"
                params.extend([search_term, search_term])
            
            if filters.get('periodo'):
                dias = int(filters['periodo'])
                where_conditions.append("t.date >= %s")
                data_inicio = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
                params.append(data_inicio)
        
        if where_conditions:
            query += " AND " + " AND ".join(where_conditions)
        
        query += """
        GROUP BY u.id, u.firstname, u.realname
        HAVING COUNT(t.id) > 0
        ORDER BY count DESC
        LIMIT 20
        """
        
        return self.db.execute_query(query, tuple(params) if params else None)
    
    def get_tickets_by_category(self, filters: Dict = None) -> List[Dict]:
        """Obtém contagem de tickets por categoria"""
        
        query = """
        SELECT 
            COALESCE(c.name, 'Sem Categoria') as category,
            COUNT(t.id) as count
        FROM glpi_tickets t
        LEFT JOIN glpi_itilcategories c ON t.itilcategories_id = c.id
        WHERE t.is_deleted = 0
        """
        
        where_conditions = []
        params = []
        
        if filters and filters.get('periodo'):
            dias = int(filters['periodo'])
            where_conditions.append("t.date >= %s")
            data_inicio = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
            params.append(data_inicio)
        
        if where_conditions:
            query += " AND " + " AND ".join(where_conditions)
        
        query += """
        GROUP BY c.id, c.name
        ORDER BY count DESC
        LIMIT 15
        """
        
        return self.db.execute_query(query, tuple(params) if params else None)
    
    def get_tickets_by_location(self, filters: Dict = None) -> List[Dict]:
        """Obtém contagem de tickets por localização"""
        
        query = """
        SELECT 
            COALESCE(l.name, 'Sem Localização') as location,
            COUNT(t.id) as count
        FROM glpi_tickets t
        LEFT JOIN glpi_users u ON t.users_id_recipient = u.id
        LEFT JOIN glpi_locations l ON u.locations_id = l.id
        WHERE t.is_deleted = 0
        """
        
        where_conditions = []
        params = []
        
        if filters and filters.get('periodo'):
            dias = int(filters['periodo'])
            where_conditions.append("t.date >= %s")
            data_inicio = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
            params.append(data_inicio)
        
        if where_conditions:
            query += " AND " + " AND ".join(where_conditions)
        
        query += """
        GROUP BY l.id, l.name
        ORDER BY count DESC
        LIMIT 15
        """
        
        return self.db.execute_query(query, tuple(params) if params else None)
    
    def get_tickets_by_type(self, filters: Dict = None) -> List[Dict]:
        """Obtém distribuição de tickets por tipo"""
        
        query = """
        SELECT 
            CASE 
                WHEN t.status IN (2,3) THEN 'Atribuidos'
                ELSE 'Requisitante'
            END as type,
            COUNT(t.id) as count
        FROM glpi_tickets t
        WHERE t.is_deleted = 0
        """
        
        where_conditions = []
        params = []
        
        if filters and filters.get('periodo'):
            dias = int(filters['periodo'])
            where_conditions.append("t.date >= %s")
            data_inicio = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
            params.append(data_inicio)
        
        if where_conditions:
            query += " AND " + " AND ".join(where_conditions)
        
        query += """
        GROUP BY CASE 
            WHEN t.status IN (2,3) THEN 'Atribuidos'
            ELSE 'Requisitante'
        END
        ORDER BY count DESC
        """
        
        results = self.db.execute_query(query, tuple(params) if params else None)
        
        # Adicionar cores
        for result in results:
            if result['type'] == 'Atribuidos':
                result['color'] = '#3498db'
            else:
                result['color'] = '#95a5a6'
        
        return results