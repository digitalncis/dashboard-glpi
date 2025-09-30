# Guia de Deploy - Dashboard GLPI

Este guia mostra como hospedar o Dashboard GLPI gratuitamente em diferentes plataformas na nuvem.

## Opções Gratuitas Recomendadas

### 1. **RENDER.COM** ⭐ (Mais Recomendado)
- **Gratuito**: 750 horas/mês (suficiente para uso contínuo)
- **Facilidade**: Deploy automático via GitHub
- **Banco**: Suporte a MySQL externo
- **SSL**: Certificado HTTPS automático

### 2. **RAILWAY.APP**
- **Gratuito**: $5 de crédito mensal
- **Facilidade**: Deploy muito simples
- **Banco**: Pode hospedar MySQL na própria plataforma
- **Performance**: Excelente velocidade

### 3. **HEROKU** 
- **Gratuito**: Limitado (não recomendado para produção)
- **Facilidade**: Deploy via Git
- **Banco**: Requer MySQL externo

---

## PREPARAÇÃO DO CÓDIGO

### 1. Subir código para GitHub
```bash
# Inicializar git (se ainda não foi feito)
git init
git add .
git commit -m "Dashboard GLPI - Deploy ready"

# Criar repositório no GitHub e fazer push
git remote add origin https://github.com/SEU_USUARIO/dashboard-glpi.git
git push -u origin main
```

---

## DEPLOY NO RENDER.COM (RECOMENDADO)

### Passo 1: Criar conta
1. Acesse: https://render.com
2. Faça signup com GitHub
3. Conecte seu repositório

### Passo 2: Criar Web Service
1. Click "New" → "Web Service"
2. Conecte seu repositório GitHub
3. Configure:
   - **Name**: `dashboard-glpi-sesma`
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 app:app`

### Passo 3: Configurar Variáveis de Ambiente
No dashboard do Render, adicione:
```
FLASK_ENV=production
SECRET_KEY=SUA_CHAVE_SECRETA_FORTE
DB_HOST=seu_servidor_mysql.com
DB_PORT=3306
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=nome_banco_glpi
```

### Passo 4: Deploy
- Click "Create Web Service"
- Aguarde o deploy (5-10 minutos)
- Sua URL será: `https://dashboard-glpi-sesma.onrender.com`

---

## DEPLOY NO RAILWAY.APP

### Passo 1: Criar conta
1. Acesse: https://railway.app
2. Faça login com GitHub
3. Click "New Project"

### Passo 2: Deploy from GitHub
1. Selecione "Deploy from GitHub repo"
2. Escolha seu repositório
3. Railway detecta automaticamente Python

### Passo 3: Configurar Variáveis
Na aba "Variables":
```
FLASK_ENV=production
SECRET_KEY=SUA_CHAVE_SECRETA_FORTE
DB_HOST=seu_servidor_mysql.com
DB_PORT=3306
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=nome_banco_glpi
```

### Passo 4: Gerar Domínio
1. Na aba "Settings"
2. Click "Generate Domain"
3. Sua URL será: `https://dashboard-glpi-production.up.railway.app`

---

## BANCO DE DADOS MYSQL GRATUITO

### Opção 1: PlanetScale (Recomendado)
1. Acesse: https://planetscale.com
2. Crie conta gratuita (10GB)
3. Crie database "glpi"
4. Use as credenciais no deploy

### Opção 2: Railway MySQL
1. No Railway, adicione MySQL ao projeto
2. Use as credenciais geradas
3. Importe dados do GLPI

### Opção 3: FreeSQLDatabase
1. Acesse: https://www.freesqldatabase.com
2. Crie MySQL gratuito (5MB)
3. Use para testes

---

## CONFIGURAÇÃO AUTOMÁTICA

### Usando arquivo .env local:
```bash
# Copie o exemplo
cp .env.example .env

# Configure suas variáveis
# Edite .env com dados reais

# Para desenvolvimento local
pip install python-dotenv
python app.py
```

---

## VANTAGENS DE CADA PLATAFORMA

### Render.com ⭐
- ✅ 750 horas gratuitas (24/7)
- ✅ SSL automático
- ✅ Deploy automático via GitHub
- ✅ Logs detalhados
- ✅ Health checks
- ❌ Pode hibernar após inatividade

### Railway.app
- ✅ $5 crédito mensal
- ✅ MySQL incluído
- ✅ Deploy muito rápido
- ✅ Interface moderna
- ❌ Limite de crédito pode acabar

### Heroku
- ✅ Plataforma conhecida
- ✅ Muita documentação
- ❌ Plano gratuito muito limitado
- ❌ Hiberna após 30 min

---

## RESOLUÇÃO DE PROBLEMAS

### Deploy falha:
```bash
# Verificar logs no dashboard da plataforma
# Verificar se requirements.txt está correto
# Verificar se Procfile existe
```

### Erro de conexão com banco:
```bash
# Verificar variáveis de ambiente
# Testar conexão manual:
mysql -h HOST -u USER -p DATABASE

# Verificar se IP da plataforma está liberado no MySQL
```

### Dashboard não carrega:
```bash
# Verificar logs da aplicação
# Acessar /api/test-db para ver status
# Verificar se PORT está configurado
```

---

## MONITORAMENTO

### URLs para verificar:
- **Dashboard**: `https://sua-url.com`
- **Health Check**: `https://sua-url.com/api/test-db`
- **API**: `https://sua-url.com/api/metrics`

### Logs:
- Render: Dashboard → Logs
- Railway: Project → Deployments → View Logs
- Heroku: `heroku logs --tail`

---

## SEGURANÇA

### Variáveis importantes:
- **SECRET_KEY**: Gere uma chave forte
- **DB_PASSWORD**: Use senha forte
- **FLASK_ENV**: `production` para produção

### Recomendações:
- Nunca commite senhas no código
- Use HTTPS sempre (automático nas plataformas)
- Configure backup do banco
- Monitor logs regularmente

---

## CUSTOS

### Render.com (Gratuito):
- 750 horas/mês
- 100GB bandwidth
- SSL incluído

### Railway.app (Gratuito):
- $5 crédito/mês
- Uso baseado em recursos

### PlanetScale (Gratuito):
- 10GB storage
- 1 billion reads/mês

**Total: 100% GRATUITO para uso normal!**

---

## PRÓXIMOS PASSOS

1. ✅ Escolha uma plataforma (recomendo Render)
2. ✅ Suba código para GitHub
3. ✅ Configure banco MySQL
4. ✅ Configure variáveis de ambiente
5. ✅ Faça deploy
6. ✅ Teste funcionamento
7. ✅ Configure domínio customizado (opcional)

Seu Dashboard GLPI estará disponível 24/7 na internet gratuitamente!