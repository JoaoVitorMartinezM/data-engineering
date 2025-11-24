# DAGs do Airflow para Pipeline ETL de Cintilografia

## 📋 DAGs Criadas

### 1. **etl_simple_dag.py** - DAG Simples ⭐ (Recomendada para começar)
- **ID**: `etl_cintilografia_simple`
- **Execução**: Manual (sem agendamento)
- **Tasks**: 3 tasks básicas
- **Descrição**: Pipeline ETL simples e direto

**Fluxo:**
```
Bronze Script → Silver Script → Data Check
```

### 2. **etl_cintilografia_dag.py** - DAG Intermediária 
- **ID**: `etl_cintilografia_pipeline`
- **Execução**: Diária (@daily)
- **Tasks**: 5 tasks com verificação de qualidade
- **Descrição**: Pipeline com verificações básicas de qualidade

**Fluxo:**
```
Start → Bronze → Silver → Quality Check → End
```

### 3. **etl_cintilografia_advanced_dag.py** - DAG Avançada 🚀
- **ID**: `etl_cintilografia_pipeline_advanced`
- **Execução**: Diária às 2h da manhã (0 2 * * *)
- **Tasks**: 10+ tasks com funcionalidades avançadas
- **Descrição**: Pipeline completo com backup, relatórios e monitoramento

**Fluxo:**
```
Start → Prerequisites → Bronze → Silver → Backup → Quality → Report → End
```

## 🚀 Como Executar

### 1. Verificar se as DAGs estão no Airflow

Acesse o Airflow em: **http://localhost:8082**
- Usuário: `admin`
- Senha: `admin`

### 2. Copiar Scripts para o Spark

Certifique-se que os scripts estão no container:

```powershell
docker cp bronze_script.py spark_master:/opt/spark/work-dir/
docker cp silver_script.py spark_master:/opt/spark/work-dir/
```

### 3. Executar DAG Simples (Recomendado)

1. No Airflow Web UI, procure por: `etl_cintilografia_simple`
2. Ative a DAG clicando no toggle
3. Clique em "Trigger DAG" para executar manualmente

### 4. Monitorar Execução

- Clique na DAG para ver o gráfico de tasks
- Clique em cada task para ver logs
- Verde = Sucesso, Vermelho = Erro

## 🔧 Configuração dos Scripts

### Antes de executar, certifique-se que:

1. **MinIO está rodando**: `docker-compose ps minio`
2. **Spark está rodando**: `docker-compose ps spark-master`
3. **Scripts estão no container**: 
   ```bash
   docker exec spark_master ls -la /opt/spark/work-dir/
   ```

## 📊 O que cada Task faz

### Bronze Layer (`run_bronze_script`)
- Baixa dados do GitHub
- Limpa nomes de colunas
- Salva no formato Delta em `s3a://bronze/dados_cintilografia`

### Silver Layer (`run_silver_script`)
- Lê dados do Bronze
- Aplica transformações e limpezas
- Salva dados processados em `s3a://silver/dados_cintilografia`

### Data Check (`check_data`)
- Verifica se os dados foram salvos corretamente
- Conta registros em cada layer
- Valida integridade dos dados

## ⚠️ Troubleshooting

### Problema: DAG não aparece no Airflow
```bash
# Reiniciar o scheduler
docker-compose restart airflow-scheduler
```

### Problema: Task falha com "container not found"
```bash
# Verificar se containers estão rodando
docker-compose ps

# Reiniciar containers se necessário
docker-compose restart spark-master
```

### Problema: Erro de conexão S3
```bash
# Verificar se MinIO está acessível
curl http://localhost:9000/minio/health/live
```

### Problema: Scripts não encontrados
```bash
# Copiar scripts novamente
docker cp bronze_script.py spark_master:/opt/spark/work-dir/
docker cp silver_script.py spark_master:/opt/spark/work-dir/

# Verificar se foram copiados
docker exec spark_master ls -la /opt/spark/work-dir/
```

## 📈 Exemplo de Execução Bem-Sucedida

```
✅ run_bronze_script: Sucesso (2 min 30s)
   - 106 registros processados
   - Dados salvos em s3a://bronze/dados_cintilografia

✅ run_silver_script: Sucesso (1 min 15s)
   - Transformações aplicadas
   - Dados salvos em s3a://silver/dados_cintilografia

✅ check_data: Sucesso (30s)
   - Bronze Layer: 106 registros
   - Silver Layer: 106 registros
```

## 🎯 Próximos Passos

1. **Comece com a DAG simples** para testar
2. **Monitore os logs** para entender o comportamento
3. **Customize as DAGs** conforme suas necessidades
4. **Adicione notificações** por email/Slack
5. **Implemente testes de qualidade** mais avançados

## 🔗 Links Úteis

- **Airflow UI**: http://localhost:8082
- **MinIO Console**: http://localhost:9001
- **Spark Master UI**: http://localhost:8080

## 📝 Logs Importantes

Para debugar problemas, verifique os logs:
```bash
# Logs do Airflow
docker logs airflow_webserver
docker logs airflow_scheduler

# Logs do Spark
docker logs spark_master

# Logs das tasks (via Airflow UI)
```