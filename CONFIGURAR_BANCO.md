#  COMO INTEGRAR COM SEU BANCO GLPI

##  PASSO A PASSO RÁPIDO

### 1. Encontrar os dados de conexão do GLPI

**No servidor onde está o GLPI, procure o arquivo:**
```
config/config_db.php
```

**O arquivo terá algo assim:**
```php
<?php
$CFG_GLPI["dbhost"] = "localhost";
$CFG_GLPI["dbuser"] = "glpi_user";
$CFG_GLPI["dbpassword"] = "minha_senha_forte";
$CFG_GLPI["dbdefault"] = "glpidb";
?>
```

### 2. Atualizar o arquivo config.py

**Edite o arquivo `config.py` e substitua:**

```python
MYSQL_CONFIG = {
    'host': 'localhost',           # ← Coloque o dbhost aqui
    'port': 3306,                  # ← Mantenha 3306 (padrão MySQL)
    'user': 'glpi_user',           # ← Coloque o dbuser aqui
    'password': 'minha_senha_forte', # ← Coloque o dbpassword aqui
    'database': 'glpidb',          # ← Coloque o dbdefault aqui
    'charset': 'utf8mb4',
    'autocommit': True
}
```

### 3. Testar a conexão

```powershell
# No PowerShell, dentro da pasta do dashboard:
python -c "from database import *; import config; db = DatabaseConnection({'DB_TYPE': config.DB_TYPE, 'MYSQL_CONFIG': config.MYSQL_CONFIG}); print(db.test_connection())"
```

### 4. Executar o dashboard

```powershell
python app.py
```

### 5. Verificar se funcionou

Acesse: `http://localhost:5000/api/test-db`

Se retornar `"success": true`, está funcionando! 🎉

## 🔧 TROUBLESHOOTING

### Erro de conexão recusada
- Verificar se o MySQL está rodando
- Verificar se o host/porta estão corretos
- Testar conexão: `mysql -h HOST -u USER -p DATABASE`

### Erro de acesso negado
- Verificar usuário e senha
- Verificar se o usuário tem permissão SELECT nas tabelas glpi_*

### Tabelas não encontradas
- Verificar se o banco é realmente do GLPI
- Executar: `SHOW TABLES LIKE 'glpi_%';`

### Dependências faltando
```powershell
pip install pymysql python-dotenv
```

## TABELAS QUE O DASHBOARD USA

- `glpi_tickets` - Chamados principais
- `glpi_users` - Usuários/requisitantes  
- `glpi_itilcategories` - Categorias
- `glpi_locations` - Localizações

## CONFIGURAÇÃO ATUAL

**Enquanto não tiver o banco, o dashboard funciona com:**
**Sistema aguardando configuração com banco de dados GLPI.**

**Quando conectar o banco, terá:**
**Após configuração correta:**
- Dados reais do GLPI
- Métricas atualizadas em tempo real
- Filtros aplicados aos dados reais
- Sistema de cache automático

## 🎯 EXEMPLO COMPLETO DE CONFIGURAÇÃO

```python
# config.py - Exemplo real
DB_TYPE = 'mysql'

MYSQL_CONFIG = {
    'host': '192.168.1.100',     # IP do servidor
    'port': 3306,
    'user': 'dashboard_user',
    'password': 'MinH@Senh@123',
    'database': 'glpi_producao',
    'charset': 'utf8mb4',
    'autocommit': True
}
```

---

**IMPORTANTE: Dashboard requer configuração com banco GLPI para funcionar.**