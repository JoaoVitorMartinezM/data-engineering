# 🔧 Correção de Problemas de Migração do Airflow

## 📋 Problema Resolvido

Este documento explica as mudanças implementadas no `docker-compose.yaml` para **prevenir erros de migração do Airflow** que ocorriam ao executar `docker-compose up -d` múltiplas vezes.

### ⚠️ Sintomas do Problema Anterior
- Erro: `Target database is not up to date` ao reiniciar os containers
- Conflitos com revisões do Alembic (ex: `5f2621c13b39`)
- Necessidade de recriar o schema do banco manualmente
- Perda de dados de DAGs e configurações

---

## 🛠️ Alterações Implementadas

### 1️⃣ **PostgreSQL com Volume Nomeado**

**Antes:**
```yaml
volumes:
  - ./datalake/postgres:/var/lib/postgresql/data
```

**Depois:**
```yaml
volumes:
  - postgres-db-volume:/var/lib/postgresql/data  # Volume nomeado
```

**Por que?**
- ✅ Evita problemas de permissão no Windows/Linux
- ✅ Previne corrupção de dados em paradas bruscas
- ✅ Melhor isolamento e performance
- ✅ Facilita backups com `docker volume backup`

### 2️⃣ **Inicialização Inteligente do Banco (airflow-initdb)**

**Novo comando de inicialização:**
```bash
# Verifica se o banco já está inicializado
if airflow db check 2>/dev/null; then
  echo 'Banco já inicializado, pulando migração.'
else
  echo 'Inicializando banco de dados...'
  airflow db migrate
fi
```

**Benefícios:**
- ✅ **Idempotente**: Pode ser executado múltiplas vezes sem erros
- ✅ Detecta banco já inicializado e pula migração
- ✅ Cria usuário admin automaticamente (se não existir)
- ✅ Não tenta migrar banco já atualizado

### 3️⃣ **Configurações de Pool de Conexões**

Adicionadas variáveis para estabilidade:
```yaml
AIRFLOW__DATABASE__SQL_ALCHEMY_POOL_SIZE: 5
AIRFLOW__DATABASE__SQL_ALCHEMY_POOL_RECYCLE: 3600
AIRFLOW__DATABASE__SQL_ALCHEMY_POOL_ENABLED: "False"  # No init
```

**Por que?**
- ✅ Previne timeouts em conexões longas
- ✅ Recicla conexões a cada 1 hora (evita stale connections)
- ✅ Controla número de conexões simultâneas

### 4️⃣ **Políticas de Restart**

```yaml
airflow-webserver:
  restart: unless-stopped

airflow-scheduler:
  restart: unless-stopped

airflow-initdb:
  restart: "no"  # Nunca reinicia automaticamente
```

**Por que?**
- ✅ Webserver e scheduler reiniciam automaticamente se falharem
- ✅ Initdb NUNCA reinicia (executa apenas uma vez)
- ✅ Evita loops de reinicialização do banco

### 5️⃣ **Healthchecks Aprimorados**

**PostgreSQL:**
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U airflow_user -d airflow_db"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 10s
```

**Webserver:**
```yaml
healthcheck:
  test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
  interval: 30s
  start_period: 30s
```

**Scheduler:**
```yaml
healthcheck:
  test: ["CMD-SHELL", "airflow jobs check --job-type SchedulerJob"]
  interval: 30s
  start_period: 30s
```

**Por que?**
- ✅ Garante que serviços estejam realmente prontos antes de prosseguir
- ✅ `start_period` dá tempo para inicialização completa
- ✅ Previne dependências de serviços não prontos

### 6️⃣ **Configurações de Encoding e Autenticação**

```yaml
postgres:
  environment:
    POSTGRES_INITDB_ARGS: "-E UTF8"
    POSTGRES_HOST_AUTH_METHOD: md5
```

**Por que?**
- ✅ Garante encoding UTF-8 (evita problemas com caracteres especiais)
- ✅ Autenticação MD5 mais segura que `trust`

---

## 🚀 Como Usar (Workflow Correto)

### ⚙️ Primeira Inicialização (Banco Novo)

```powershell
# 1. Subir apenas o PostgreSQL primeiro
docker-compose up -d postgres

# 2. Aguardar o PostgreSQL ficar saudável (opcional, mas recomendado)
docker-compose ps postgres
# Deve mostrar "healthy" no status

# 3. Inicializar o banco do Airflow
docker-compose up airflow-initdb

# 4. Verificar os logs da inicialização
docker-compose logs airflow-initdb

# 5. Subir os demais serviços do Airflow
docker-compose up -d airflow-webserver airflow-scheduler
```

### 🔄 Reinicializações Subsequentes

```powershell
# Método 1: Subir tudo de uma vez (agora é seguro!)
docker-compose up -d

# Método 2: Reiniciar apenas Airflow (sem PostgreSQL)
docker-compose restart airflow-webserver airflow-scheduler
```

### 🛑 Parada Limpa

```powershell
# Parar todos os serviços
docker-compose stop

# Ou parar serviços específicos
docker-compose stop airflow-webserver airflow-scheduler
```

### 🗑️ Reset Completo (Em caso de emergência)

```powershell
# 1. Parar todos os containers
docker-compose down

# 2. Remover o volume do PostgreSQL
docker volume rm intro-de_postgres-db-volume

# 3. Subir novamente (vai criar banco novo)
docker-compose up -d postgres
docker-compose up airflow-initdb
docker-compose up -d airflow-webserver airflow-scheduler
```

---

## 📊 Monitoramento e Verificação

### ✅ Verificar Status dos Serviços

```powershell
# Ver status de todos os containers
docker-compose ps

# Ver se os healthchecks estão passando
docker inspect airflow_postgres | grep -A 10 "Health"
docker inspect airflow_webserver | grep -A 10 "Health"
```

### 📜 Ver Logs

```powershell
# Logs da inicialização do banco
docker-compose logs airflow-initdb

# Logs do PostgreSQL
docker-compose logs postgres --tail=50

# Logs do Webserver (últimas 100 linhas)
docker-compose logs airflow-webserver --tail=100

# Logs do Scheduler
docker-compose logs airflow-scheduler --tail=100

# Seguir logs em tempo real
docker-compose logs -f airflow-scheduler
```

### 🔍 Verificar Estado do Banco

```powershell
# Entrar no PostgreSQL
docker exec -it airflow_postgres psql -U airflow_user -d airflow_db

# Dentro do psql:
\dt  # Listar tabelas
SELECT * FROM alembic_version;  # Ver versão atual da migração
\q   # Sair
```

### 🧪 Testar Conexão com Airflow

```powershell
# Verificar se o webserver está respondendo
curl http://localhost:8082/health

# Acessar a UI
start http://localhost:8082
# Login: admin / admin
```

---

## 🔧 Troubleshooting

### ❌ Problema: "Target database is not up to date"

**Solução:**
```powershell
# 1. Parar os serviços do Airflow
docker-compose stop airflow-webserver airflow-scheduler

# 2. Executar a migração manualmente
docker-compose run --rm airflow-initdb airflow db migrate

# 3. Reiniciar os serviços
docker-compose up -d airflow-webserver airflow-scheduler
```

### ❌ Problema: "Could not find a suitable TLD for domain"

**Solução:**
```powershell
# Remover cache do Python dentro do container
docker-compose exec airflow-webserver rm -rf /home/airflow/.local/lib/python3.11/site-packages/__pycache__
docker-compose restart airflow-webserver
```

### ❌ Problema: Container airflow-initdb fica em loop

**Solução:**
```powershell
# Remover o container e volume
docker-compose down
docker volume rm intro-de_postgres-db-volume

# Recriar do zero
docker-compose up -d postgres
sleep 10
docker-compose up airflow-initdb
docker-compose up -d airflow-webserver airflow-scheduler
```

### ❌ Problema: Permissões negadas no Windows

**Solução:**
```powershell
# Dar permissões nas pastas locais
icacls ".\airflow\logs" /grant Everyone:F /T
icacls ".\airflow\dags" /grant Everyone:F /T
icacls ".\airflow\plugins" /grant Everyone:F /T
```

---

## 📚 Referências

- [Airflow Database Migrations](https://airflow.apache.org/docs/apache-airflow/stable/howto/set-up-database.html)
- [Docker Compose Healthchecks](https://docs.docker.com/compose/compose-file/compose-file-v3/#healthcheck)
- [PostgreSQL Docker Best Practices](https://hub.docker.com/_/postgres)
- [Alembic Migrations](https://alembic.sqlalchemy.org/en/latest/)

---

## ✅ Checklist Rápido

Antes de fazer `docker-compose up -d`:

- [ ] PostgreSQL está com healthcheck em `healthy`
- [ ] O serviço `airflow-initdb` foi executado pelo menos uma vez
- [ ] Logs do initdb não mostram erros críticos
- [ ] Volume `postgres-db-volume` existe (`docker volume ls`)
- [ ] Pastas `./airflow/dags`, `./airflow/logs`, `./airflow/plugins` existem

---

## 📈 Benefícios Finais

| Antes | Depois |
|-------|--------|
| ❌ Erros de migração frequentes | ✅ Migração idempotente |
| ❌ Perda de dados ao reiniciar | ✅ Dados persistidos em volume nomeado |
| ❌ Necessidade de limpar banco manualmente | ✅ Detecção automática de estado |
| ❌ Conflitos de revisão do Alembic | ✅ Verificação antes de migrar |
| ❌ Logs confusos | ✅ Mensagens claras de status |
| ❌ Permissões problemáticas | ✅ Isolamento com volumes nomeados |

---

**Última atualização:** 24 de novembro de 2025  
**Versão do Airflow:** 2.8.1  
**Versão do PostgreSQL:** 13-alpine
