# Solução do Problema do Airflow

## 🔴 Problema Identificado

Erro ao inicializar o banco de dados do Airflow:
```
alembic.util.exc.CommandError: Can't locate revision identified by '5f2621c13b39'
```

Este erro ocorreu porque:
1. O banco de dados do Airflow foi parcialmente inicializado anteriormente
2. Houve uma tentativa de migração que deixou o banco em estado inconsistente
3. O Alembic (sistema de migração de banco do Airflow) não conseguiu encontrar uma revisão específica

## ✅ Solução Aplicada

### Passo 1: Parar os containers do Airflow
```powershell
docker-compose stop airflow-webserver airflow-scheduler airflow-initdb
docker-compose rm -f airflow-webserver airflow-scheduler airflow-initdb
```

### Passo 2: Limpar o banco de dados
```powershell
docker-compose stop postgres
Remove-Item -Path ".\datalake\postgres" -Recurse -Force
docker-compose rm -f postgres
```

### Passo 3: Recriar tudo do zero
```powershell
# Subir o Postgres
docker-compose up -d postgres

# Aguardar e inicializar o banco
Start-Sleep -Seconds 10
docker-compose up -d airflow-initdb

# Subir o webserver e scheduler
docker-compose up -d airflow-webserver airflow-scheduler
```

## 🎯 Resultado

O Airflow foi inicializado com sucesso:
- ✅ Banco de dados criado e migrado corretamente
- ✅ Usuário admin criado (usuário: `admin`, senha: `admin`)
- ✅ Webserver rodando em http://localhost:8082
- ✅ Scheduler ativo e processando DAGs

## 🔗 Acesso ao Airflow

- **URL**: http://localhost:8082
- **Usuário**: admin
- **Senha**: admin

## 📝 Notas Importantes

1. **Volume do Postgres**: Os dados ficam em `./datalake/postgres/`
2. **DAGs**: Coloque seus DAGs em `./airflow/dags/`
3. **Logs**: Os logs ficam em `./airflow/logs/`
4. **Plugins**: Plugins customizados vão em `./airflow/plugins/`

## 🚨 Se o problema ocorrer novamente

Execute estes comandos para limpar e reiniciar:

```powershell
# Parar tudo
docker-compose stop airflow-webserver airflow-scheduler airflow-initdb postgres

# Remover containers
docker-compose rm -f airflow-webserver airflow-scheduler airflow-initdb postgres

# Limpar volume do postgres
Remove-Item -Path ".\datalake\postgres" -Recurse -Force

# Recriar tudo
docker-compose up -d postgres
Start-Sleep -Seconds 10
docker-compose up -d airflow-initdb
Start-Sleep -Seconds 15
docker-compose up -d airflow-webserver airflow-scheduler
```

## 🔍 Verificação

Para verificar se está tudo OK:

```powershell
# Ver status dos containers
docker-compose ps

# Ver logs do webserver
docker logs airflow_webserver

# Ver logs do scheduler
docker logs airflow_scheduler
```

## 📊 Arquitetura Atual

```
┌─────────────────────────────────────────────┐
│         Airflow Architecture                │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐      ┌─────────────────┐ │
│  │   Webserver  │◄─────┤   PostgreSQL    │ │
│  │  (Port 8082) │      │  (Metadados)    │ │
│  └──────────────┘      └─────────────────┘ │
│         ▲                      ▲            │
│         │                      │            │
│         ▼                      ▼            │
│  ┌──────────────┐      ┌─────────────────┐ │
│  │  Scheduler   │◄─────┤    DAGs Folder  │ │
│  │  (Executor)  │      │  ./airflow/dags │ │
│  └──────────────┘      └─────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```

## 🎓 Conceitos

- **airflow-initdb**: Container temporário que inicializa o banco de dados e cria o usuário admin
- **airflow-webserver**: Interface web do Airflow
- **airflow-scheduler**: Responsável por agendar e executar os DAGs
- **postgres**: Banco de dados que armazena metadados do Airflow (DAGs, runs, logs, etc.)

## 🔧 Próximos Passos

Agora que o Airflow está funcionando, você pode:

1. Criar seus primeiros DAGs em `./airflow/dags/`
2. Acessar a interface web em http://localhost:8082
3. Integrar com o Spark para orquestrar jobs de processamento de dados
4. Conectar com o MinIO para gerenciar pipelines de dados no datalake
