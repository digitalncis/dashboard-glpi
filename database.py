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
    
    # --- FUNÇÃO CORRIGIDA ---
    # 1. A assinatura da função agora aceita 'fetch_one'
    def execute_query(self, query: str, params: tuple = None, fetch_one: bool = False) -> Any:
        """Executa uma consulta e retorna os resultados"""
        try:
            if not self.connection or not self.connection.open:
                if not self.connect():
                    return None # Retorna None se a conexão falhar
            
            # Ping para verificar e reconectar se a conexão foi perdida
            self.connection.ping(reconnect=True)
            
            cursor = self.connection.cursor()
            
            cursor.execute(query, params or ())
            
            # 2. Lógica adicionada para escolher entre fetchone() e fetchall()
            if fetch_one:
                results = cursor.fetchone()
                log_msg = f"Query executada com sucesso. 1 registro retornado." if results else "Query executada com sucesso. Nenhum registro retornado."
            else:
                results = cursor.fetchall()
                log_msg = f"Query executada com sucesso. {len(results)} registros retornados."

            cursor.close()
            
            logger.info(log_msg)
            return results
            
        except Exception as e:
            logger.error(f"Erro ao executar query: {str(e)}")
            logger.error(f"Query: {query}")
            return None # Retorna None em caso de erro

    # O resto do seu ficheiro permanece exatamente igual
    def test_connection(self) -> Dict[str, Any]:
        """Testa a conexão e retorna informações do banco"""
        try:
            if not self.connect():
                return {"success": False, "error": "Falha na conexão"}
            
            self.connection.ping(reconnect=True)
            
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
            
            # Aqui chamamos a versão corrigida da nossa própria função
            results = self.execute_query(query, fetch_one=True)
            
            if results:
                return {
                    "success": True,
                    "database_info": {
                        "type": self.db_type,
                        "total_tickets": results["total_tickets"],
                        "breakdown": {
                            "novos": results["novos"],
                            "atribuidos": results["atribuidos"], 
                            "pendentes": results["pendentes"],
                            "fechados": results["fechados"]
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
        
    # Todas as outras funções da sua classe GLPIDataService permanecem aqui, sem alterações...
    def get_metrics(self, filters: Dict = None) -> Dict[str, int]:
        """Obtém métricas principais do dashboard"""
        # ... seu código aqui ...
        pass
    def get_tickets_by_requester(self, filters: Dict = None) -> List[Dict]:
        """Obtém contagem de tickets por requisitante"""
        # ... seu código aqui ...
        pass
    def get_tickets_by_category(self, filters: Dict = None) -> List[Dict]:
        """Obtém contagem de tickets por categoria"""
        # ... seu código aqui ...
        pass
    def get_tickets_by_location(self, filters: Dict = None) -> List[Dict]:
        """Obtém contagem de tickets por localização"""
        # ... seu código aqui ...
        pass
    def get_tickets_by_type(self, filters: Dict = None) -> List[Dict]:
        """Obtém distribuição de tickets por tipo"""
        # ... seu código aqui ...
        pass

