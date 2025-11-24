# 🚀 Data Engineering Infrastructure - Guia Completo

## 📋 Visão Geral

Este projeto implementa uma infraestrutura completa de Data Engineering usando Docker Compose, incluindo:

- **Apache Spark** com Delta Lake para processamento de dados
- **Apache Airflow** para orquestração de pipelines
- **MinIO** como storage S3-compatible
- **Apache Kafka** para streaming de dados
- **OpenMetadata** para data governance
- **PostgreSQL** como backend do Airflow

## 🏗️ Arquitetura da Infraestrutura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Apache Spark  │    │ Apache Airflow  │    │     MinIO       │
│   (3.5.7)       │◄──►│   (2.8.1)       │◄──►│   (S3 Storage)  │
│                 │    │                 │    │                 │
│ • Master:8080   │    │ • UI:8082       │    │ • UI:9001       │
│ • Worker:8081   │    │ • API:8082      │    │ • API:9000      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Apache Kafka  │    │  OpenMetadata   │    │   PostgreSQL    │
│   (7.5.0)       │    │   (1.10.7)      │    │     (13)        │
│                 │    │                 │    │                 │
│ • Port:9093     │    │ • UI:8585       │    │ • Port:5432     │
│ • Zookeeper:2181│    │ • API:8586      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Pré-requisitos

### Requisitos de Sistema
- **Docker**: Versão 20.10+
- **Docker Compose**: Versão 2.0+
- **RAM**: Mínimo 8GB (Recomendado 16GB)
- **Disk Space**: Mínimo 10GB livres
- **CPU**: Mínimo 4 cores

### Verificar Instalação
```powershell
# Verificar Docker
docker --version
docker-compose --version

# Verificar recursos disponíveis
docker system info
```

## 📦 Preparação do Ambiente

### 1. Clonar ou Baixar o Projeto
```powershell
git clone <repository-url>
cd intro-de
```

### 2. Criar Estrutura de Diretórios
```powershell
# O docker-compose criará automaticamente, mas você pode criar manualmente:
mkdir -p airflow/dags, airflow/logs, airflow/plugins
mkdir -p datalake
mkdir -p docker-volume/db-data
```

### 3. Build da Imagem Spark Customizada
```powershell
# Construir imagem Spark com Delta Lake
docker build -t spark-delta:3.5.7 -f Dockerfile.spark-delta .
```

## 🚀 Subindo a Infraestrutura

### Opção 1: Subir Tudo de Uma Vez (Recomendado para Primeira Execução)
```powershell
docker-compose up -d
```

### Opção 2: Subir por Camadas (Para Debug)
```powershell
# 1. Camada de Storage
docker-compose up -d postgres mysql minio elasticsearch

# 2. Camada de Processamento
docker-compose up -d zookeeper kafka spark-master spark-worker

# 3. Camada de Orquestração
docker-compose up -d airflow-initdb
docker-compose up -d airflow-webserver airflow-scheduler

# 4. Camada de Governança
docker-compose up -d execute-migrate-all openmetadata-server ingestion
```

### Opção 3: Subir Serviços Específicos
```powershell
# Apenas Spark + MinIO
docker-compose up -d spark-master spark-worker minio

# Apenas Airflow + PostgreSQL
docker-compose up -d postgres airflow-initdb airflow-webserver airflow-scheduler

# Apenas Kafka
docker-compose up -d zookeeper kafka
```

## 📊 Verificação dos Serviços

### Comando de Status
```powershell
# Verificar todos os containers
docker-compose ps

# Verificar logs de um serviço específico
docker-compose logs -f spark-master
docker-compose logs -f airflow-webserver
```

### Health Checks Automáticos
```powershell
# Aguardar todos os serviços ficarem healthy
docker-compose ps | Select-String "healthy"

# Verificar serviços específicos
docker-compose exec spark-master curl -f http://localhost:8080
docker-compose exec airflow-webserver curl -f http://localhost:8080
```

## 🌐 Acessando as Interfaces

| Serviço | URL | Usuário | Senha |
|---------|-----|---------|--------|
| **Spark Master UI** | http://localhost:8080 | - | - |
| **Spark Worker UI** | http://localhost:8081 | - | - |
| **Airflow UI** | http://localhost:8082 | `admin` | `admin` |
| **MinIO Console** | http://localhost:9001 | `admin` | `password` |
| **OpenMetadata** | http://localhost:8585 | `admin` | `admin` |
| **Elasticsearch** | http://localhost:9200 | - | - |

## 🔧 Configuração Inicial

### 1. Configurar Buckets no MinIO
```powershell
# Acessar MinIO e criar buckets necessários:
# - bronze (para dados raw)
# - silver (para dados processados)
# - backup (para backups)
```

### 2. Verificar Airflow
```powershell
# Verificar se DAGs foram carregadas
curl http://localhost:8082/api/v1/dags

# Ou acessar a interface web em http://localhost:8082
```

### 3. Testar Spark
```powershell
# Executar script de teste Delta Lake
docker exec spark_master python3 /opt/spark/work-dir/delta_timetravel.py
```

## 📋 Scripts ETL Disponíveis

### Scripts Spark
```powershell
# Bronze Layer (Ingestão de dados)
docker exec spark_master python3 /opt/spark/work-dir/bronze_script.py

# Silver Layer (Transformações)
docker exec spark_master python3 /opt/spark/work-dir/silver_script.py

# Delta Lake Time Travel (Demonstração)
docker exec spark_master python3 /opt/spark/work-dir/delta_timetravel.py
```

### DAGs do Airflow Disponíveis
- `etl_cintilografia_pipeline` - Pipeline ETL original
- `etl_cintilografia_working_no_docker` - Pipeline sem dependência Docker
- `etl_spark_docker_real` - Pipeline com execução real via Docker socket
- `etl_spark_http_execution` - Pipeline via HTTP requests

## 🔍 Monitoramento e Debug

### Verificar Logs
```powershell
# Logs em tempo real
docker-compose logs -f [service-name]

# Logs dos últimos 100 linhas
docker-compose logs --tail=100 [service-name]

# Logs de todos os serviços
docker-compose logs
```

### Verificar Recursos
```powershell
# Uso de recursos por container
docker stats

# Espaço em disco usado
docker system df

# Informações detalhadas dos containers
docker-compose ps -a
```

### Resolver Problemas Comuns

#### Problema: Container não inicia
```powershell
# Verificar logs específicos
docker-compose logs [service-name]

# Reiniciar serviço específico
docker-compose restart [service-name]

# Recriar container
docker-compose up -d --force-recreate [service-name]
```

#### Problema: Portas ocupadas
```powershell
# Verificar portas em uso (Windows)
netstat -an | Select-String ":8080|:8082|:9000"

# Parar todos os containers
docker-compose down

# Limpar networks
docker network prune
```

#### Problema: Falta de memória
```powershell
# Verificar uso de memória
docker stats --no-stream

# Parar serviços não essenciais temporariamente
docker-compose stop openmetadata-server ingestion elasticsearch
```

## 🔄 Comandos de Manutenção

### Atualizar e Reiniciar
```powershell
# Baixar imagens atualizadas
docker-compose pull

# Parar tudo
docker-compose down

# Subir novamente
docker-compose up -d
```

### Limpeza do Sistema
```powershell
# Remover containers parados
docker-compose down --remove-orphans

# Limpeza completa (CUIDADO: Remove volumes)
docker-compose down -v
docker system prune -a

# Limpeza preservando dados
docker-compose down
docker container prune
docker image prune
```

### Backup dos Dados
```powershell
# Backup dos volumes importantes
docker run --rm -v intro-de_postgres-data:/data -v ${PWD}:/backup busybox tar czf /backup/postgres-backup.tar.gz -C /data .
docker run --rm -v intro-de_es-data:/data -v ${PWD}:/backup busybox tar czf /backup/elasticsearch-backup.tar.gz -C /data .
```

## 📁 Estrutura de Arquivos

```
intro-de/
├── 📄 docker-compose.yaml          # Configuração principal
├── 📄 Dockerfile.spark-delta       # Build Spark com Delta Lake
├── 📁 airflow/
│   ├── 📁 dags/                    # DAGs do Airflow
│   ├── 📁 logs/                    # Logs do Airflow
│   └── 📁 plugins/                 # Plugins personalizados
├── 📁 spark/
│   ├── 📄 bronze_script.py         # Script Bronze Layer
│   ├── 📄 silver_script.py         # Script Silver Layer
│   └── 📄 delta_timetravel.py      # Demo Delta Lake
├── 📁 datalake/                    # Dados persistentes
│   └── 📁 postgres/                # Dados PostgreSQL
├── 📁 docker-volume/               # Volumes Docker
│   └── 📁 db-data/                 # Dados MySQL OpenMetadata
└── 📁 data/                        # Dados de exemplo
    ├── 📄 dados_airbnb.parquet
    └── 📄 dados_cintilografia.csv
```

## 🎯 Casos de Uso

### 1. Desenvolvimento de ETL
```powershell
# Subir apenas Spark + MinIO + Airflow
docker-compose up -d postgres airflow-initdb airflow-webserver airflow-scheduler spark-master spark-worker minio
```

### 2. Demonstração Completa
```powershell
# Subir toda a infraestrutura
docker-compose up -d
```

### 3. Streaming de Dados
```powershell
# Subir Kafka + Spark
docker-compose up -d zookeeper kafka spark-master spark-worker minio
```

## ❗ Notas Importantes

1. **Primeira execução**: Pode demorar 5-10 minutos para baixar todas as imagens
2. **Recursos**: Monitore o uso de CPU e memória
3. **Dados persistentes**: Ficam salvos em volumes Docker
4. **Networks**: Todos os serviços estão na network `datalake-net`
5. **Security**: Esta configuração é para desenvolvimento/demonstração

## 📞 Suporte

### Comandos Úteis para Debug
```powershell
# Status detalhado
docker-compose ps --format table

# Inspecionar configuração
docker-compose config

# Verificar networks
docker network ls
docker network inspect intro-de_datalake-net

# Executar comandos dentro dos containers
docker exec -it spark_master bash
docker exec -it airflow_webserver bash
```

### Problemas Conhecidos
- **Windows**: Pode precisar habilitar virtualização no BIOS
- **WSL2**: Configurar recursos adequados no Docker Desktop
- **Firewall**: Pode bloquear algumas portas (8080, 8082, 9000, etc.)

---

## 🚀 Quick Start

```powershell
# 1. Build da imagem Spark
docker build -t spark-delta:3.5.7 -f Dockerfile.spark-delta .

# 2. Subir infraestrutura
docker-compose up -d

# 3. Aguardar containers (5-10 minutos)
docker-compose ps

# 4. Acessar interfaces
# Airflow: http://localhost:8082 (admin/admin)
# Spark: http://localhost:8080
# MinIO: http://localhost:9001 (admin/password)

# 5. Testar pipeline
docker exec spark_master python3 /opt/spark/work-dir/bronze_script.py
```

**🎉 Pronto! Sua infraestrutura de Data Engineering está funcionando!**