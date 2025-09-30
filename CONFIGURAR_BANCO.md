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
$CFG_GLPI["dbhost"] = "10.26.0.19";
$CFG_GLPI["dbuser"] = "root";
$CFG_GLPI["dbpassword"] = "3128*";
$CFG_GLPI["dbdefault"] = "glpi_db";
?>
```

2. Atualizar o arquivo config.py

**Edite o arquivo `config.py` e substitua:**

```python
MYSQL_CONFIG = {
    'host': '10.26.0.19',           # ← Coloque o dbhost aqui
    'port': 3306,                  # ← Mantenha 3306 (padrão MySQL)
    'user': 'root',           # ← Coloque o dbuser aqui
    'password': '3128*', # ← Coloque o dbpassword aqui
    'database': 'glpi_db',          # ← Coloque o dbdefault aqui
    'charset': 'utf8mb4',
    'autocommit': True
}
```

### 3. Testar a conexão

```powershell
# No PowerShell, dentro da pasta do dashboard:
python -c "from database import *; import config; db = DatabaseConnection({'DB_TYPE': config.DB_TYPE, 'MYSQL_CONFIG': config.MYSQL_CONFIG}); print(db.test_connection())"
```

 4. Executar o dashboard

```powershell
python app.py
```

 5. Verificar se funcionou

Acesse: `http://localhost:5000/api/test-db`

Se retornar `"success": true`, está funcionando! 🎉

## 🔧 TROUBLESHOOTING

### Erro de conexão recusada
- Verificar se o MySQL está rodando
- Verificar se o host/porta estão corretos
- Testar conexão: `mysql -h HOST -u USER -p DATABASE`

Erro de acesso negado
- Verificar usuário e senha
- Verificar se o usuário tem permissão SELECT nas tabelas glpi_*

Tabelas não encontradas
- Verificar se o banco é realmente do GLPI
- Executar: `SHOW TABLES LIKE 'glpi_%';`

Dependências faltando
```powershell
pip install pymysql python-dotenv
```

TABELAS QUE O DASHBOARD USA

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

EXEMPLO COMPLETO DE CONFIGURAÇÃO

python
# config.py - Exemplo real
DB_TYPE = 'mysql'

MYSQL_CONFIG = {
    'host': '10.26.0.19',     # IP do servidor
    'port': 3306,
    'user': 'root',
    'password': '3128*',
    'database': 'glpi_db',
    'charset': 'utf8mb4',
    'autocommit': True
}
```

---

**IMPORTANTE: Dashboard requer configuração com banco GLPI para funcionar.**