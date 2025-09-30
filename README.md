# Dashboard GLPI - SESMA

Dashboard web desenvolvido em Python/Flask baseado na interface GLPI, com gráficos interativos e integração com banco de dados MySQL.

## Funcionalidades

- **Métricas em tempo real**: Cards com totais de chamados por status
- **Gráficos interativos**: Visualização de dados por requisitante, categoria, localização e tipos
- **Sistema de filtros**: Filtragem por categoria, status, período e nome/requisitante
- **Interface responsiva**: Design adaptável para desktop, tablet e mobile
- **API RESTful**: Endpoints para dados e filtros
- **Exportação de dados**: Funcionalidade preparada para exportar em diferentes formatos

## Componentes do Dashboard

### Cards de Métricas
- Total de Chamados (laranja)
- Total Pendente (vermelho)
- Total Atribuído (azul)
- Total Fechado (preto)
- Chamados Novos (verde)

### Gráficos
1. **Gráfico de Barras**: Contagem de chamados por nome/requisitante
2. **Gráfico Horizontal**: Contagem por categoria
3. **Gráfico de Barras**: Contagem por localização
4. **Gráfico Pizza**: Distribuição por tipos de chamados

### Sistema de Filtros
- **Categoria**: Hardware, Software, Rede, Suporte
- **Status**: Aberto, Pendente, Atribuído, Fechado
- **Período**: 7, 30, 90 dias ou 1 ano
- **Nome/Requisitante**: Busca por texto livre

## Instalação e Execução

### Pré-requisitos
- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)
- Acesso ao banco de dados GLPI (MySQL/MariaDB recomendado)

### 1. Instalar dependências

```powershell
# No diretório do projeto
pip install -r requirements.txt
```

### 2. Configurar banco de dados

**OPÇÃO A - Configuração Automática (Recomendado):**
```powershell
python setup_database.py
```

**OPÇÃO B - Configuração Manual:**
```powershell
# Copiar arquivo de exemplo
copy config_example.py config.py
# Editar config.py com seus dados de conexão
```

### 3. Testar conexão

```powershell
# Verificar se a conexão está funcionando
python -c "from database import *; from config import *; db = DatabaseConnection({'DB_TYPE': DB_TYPE, 'MYSQL_CONFIG': MYSQL_CONFIG}); print(db.test_connection())"
```

### 4. Executar a aplicação

```powershell
python app.py
```

### 5. Acessar o dashboard
- **Interface principal**: `http://localhost:5000`
- **Teste de conexão**: `http://localhost:5000/api/test-db`
- **API de métricas**: `http://localhost:5000/api/metrics`

## Configuração do Banco de Dados

### Encontrar dados de conexão do GLPI

1. **No servidor GLPI**, localize o arquivo: `config/config_db.php`
2. **Exemplo do arquivo**:
```php
<?php
$CFG_GLPI["dbhost"] = "localhost";
$CFG_GLPI["dbuser"] = "glpi_user";
$CFG_GLPI["dbpassword"] = "sua_senha";
$CFG_GLPI["dbdefault"] = "glpidb";
?>
```

3. **Use esses dados** no script de configuração ou no arquivo `config.py`

### Tabelas GLPI utilizadas

O dashboard consulta as seguintes tabelas:
- `glpi_tickets` - Chamados principais
- `glpi_users` - Usuários e requisitantes
- `glpi_itilcategories` - Categorias de chamados
- `glpi_locations` - Localizações
- `glpi_entities` - Entidades

## Estrutura do Projeto

```
dashboard-glpi/
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── templates/
│   └── dashboard.html    # Template HTML principal
└── static/
    ├── css/
    │   └── style.css     # Estilos CSS
    └── js/
        └── dashboard.js  # JavaScript para gráficos e filtros
```

## APIs Disponíveis

### Métricas
- `GET /api/metrics?filters` - Retorna métricas principais

### Dados dos Gráficos
- `GET /api/chart-data/requisitante?filters` - Dados por requisitante
- `GET /api/chart-data/categoria?filters` - Dados por categoria
- `GET /api/chart-data/localizacao?filters` - Dados por localização
- `GET /api/chart-data/tipos?filters` - Dados por tipos

### Filtros
- `GET /api/filters/options` - Opções disponíveis para filtros

### Exportação
- `GET /api/export/{format}?filters` - Exportar dados (CSV, JSON, etc.)

## Personalização

### Cores dos Cards
As cores podem ser alteradas no arquivo `static/css/style.css`:

```css
.total-chamados { background: linear-gradient(135deg, #e67e22, #d35400); }
.total-pendente { background: linear-gradient(135deg, #e74c3c, #c0392b); }
.total-atribuido { background: linear-gradient(135deg, #3498db, #2980b9); }
.total-fechado { background: linear-gradient(135deg, #34495e, #2c3e50); }
.chamados-novos { background: linear-gradient(135deg, #27ae60, #229954); }
```

### Dados Personalizados
Para integrar com seus dados reais, modifique as funções em `app.py`:
- `get_metrics()`: Conecte com sua base de dados
- `get_chart_data()`: Implemente queries específicas
- Adicione autenticação se necessário

## Responsividade

O dashboard é totalmente responsivo e se adapta a:
- **Desktop**: Layout completo com gráficos lado a lado
- **Tablet**: Gráficos empilhados, filtros reorganizados
- **Mobile**: Layout vertical, filtros em coluna única

## Implementações Planejadas

- [x] Integração com banco de dados MySQL/GLPI
- [ ] Autenticação de usuários
- [ ] Notificações em tempo real
- [ ] Relatórios PDF
- [ ] Cache de dados
- [ ] Logs de auditoria

## Tecnologias Utilizadas

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Gráficos**: Chart.js
- **UI/UX**: CSS Grid, Flexbox
- **AJAX**: Fetch API para comunicação com backend

## Parâmetros de Filtro

Os filtros suportam os seguintes parâmetros via URL:

- `categoria`: hardware, software, rede, suporte
- `status`: aberto, pendente, atribuido, fechado
- `periodo`: 7, 30, 90, 365 (dias)
- `requisitante`: texto livre para busca

Exemplo: `http://localhost:5000/?status=pendente&categoria=hardware`

## Suporte

Para dúvidas ou problemas:
1. Verifique os logs no console do navegador (F12)
2. Verifique os logs do Flask no terminal
3. Certifique-se de que todas as dependências estão instaladas

---

**Desenvolvido para SESMA** - Dashboard GLPI Web Interface