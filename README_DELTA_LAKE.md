# Delta Lake Time Travel - Guia de Uso

## 🎯 O que foi implementado

Configuração completa do **Delta Lake 3.2.0** com **Apache Spark 3.5.7** para suportar **Time Travel** em um ambiente Docker com MinIO como storage S3.

## 🔧 Componentes

1. **Imagem Docker customizada** (`spark-delta:3.5.7`):
   - Spark 3.5.7 com Python 3
   - Delta Lake 3.2.0 (JARs pré-instalados)
   - Hadoop AWS 3.3.4
   - AWS SDK Bundle 1.12.262

2. **Script de Time Travel** (`delta_timetravel.py`):
   - Escrita inicial de dados (versão 0)
   - Atualização de registros (versão 1)
   - Leitura da versão atual
   - **Time Travel** para versões anteriores
   - Visualização do histórico de versões

## 🚀 Como executar

### 1. Certifique-se de que os containers estão rodando

```powershell
docker-compose up -d spark-master spark-worker minio
```

### 2. Execute o script dentro do container Spark

```powershell
docker exec spark_master python3 /opt/spark/work-dir/delta_timetravel.py
```

## 📊 O que o script faz

### Versão 0 (Dados originais)
```
+-------+---+
|   name| id|
+-------+---+
|  Alice|  1|
|    Bob|  2|
|Charlie|  3|
+-------+---+
```

### Versão 1 (Após update)
```
+-------+---+
|   name| id|
+-------+---+
|  Alice|  1|
| Robert|100|  ← Bob foi atualizado!
|Charlie|  3|
+-------+---+
```

### Time Travel - Lendo Versão 0
```python
# Mesmo após o update, você pode ler a versão antiga
df_old = spark.read.format("delta").option("versionAsOf", 0).load(DELTA_PATH)
# Retorna os dados originais com "Bob" em vez de "Robert"
```

### Histórico de versões
```
+-------+-------------------+---------+
|version|timestamp          |operation|
+-------+-------------------+---------+
|1      |2025-11-21 14:03:18|UPDATE   |
|0      |2025-11-21 14:03:08|WRITE    |
+-------+-------------------+---------+
```

## 🔍 Funcionalidades do Delta Lake

### Time Travel por Versão
```python
# Ler uma versão específica
df = spark.read.format("delta").option("versionAsOf", 0).load(path)
```

### Time Travel por Timestamp
```python
# Ler dados de um momento específico
df = spark.read.format("delta")\
    .option("timestampAsOf", "2025-11-21 14:00:00")\
    .load(path)
```

### Consultar Histórico
```python
from delta.tables import DeltaTable

deltaTable = DeltaTable.forPath(spark, path)
deltaTable.history().show()
```

### Operações ACID
```python
# Update
deltaTable.update(
    condition="name = 'Bob'",
    set={"name": "'Robert'", "id": "100"}
)

# Delete
deltaTable.delete("id > 100")

# Merge (Upsert)
deltaTable.merge(
    source_df,
    "target.id = source.id"
).whenMatchedUpdate(set={"name": "source.name"})\
 .whenNotMatchedInsert(values={"id": "source.id", "name": "source.name"})\
 .execute()
```

## 🗂️ Estrutura dos Arquivos

```
intro-de/
├── delta_timetravel.py         # Script principal de Time Travel
├── delta_timetravel_simple.py  # Versão simplificada do script
├── Dockerfile.spark-delta      # Dockerfile customizado com Delta Lake
├── docker-compose.yaml         # Configuração dos containers
└── datalake/
    └── spark-timetravel/
        └── test/                # Pasta onde os dados Delta são salvos
            ├── _delta_log/      # Transaction log do Delta Lake
            └── *.parquet        # Arquivos de dados
```

## 🛠️ Reconstruir a imagem (se necessário)

Se você precisar modificar o Dockerfile:

```powershell
docker build -t spark-delta:3.5.7 -f Dockerfile.spark-delta .
docker-compose restart spark-master spark-worker
```

## 🔗 Compatibilidade das Versões

| Componente | Versão | Motivo |
|------------|--------|--------|
| Spark | 3.5.7 | Versão estável atual |
| Delta Lake | 3.2.0 | Compatível com Spark 3.5.x |
| Scala | 2.12 | Versão padrão do Spark 3.5.7 |
| Hadoop AWS | 3.3.4 | Compatível com Spark 3.5.x |
| AWS SDK | 1.12.262 | Recomendado para Hadoop 3.3.4 |

## 📍 Acessar o MinIO

- Console: http://localhost:9001
- Usuário: `admin`
- Senha: `password`

Você pode visualizar os arquivos Delta criados no bucket `spark-timetravel/test/`.

## ⚠️ Notas Importantes

1. **Os JARs estão pré-instalados**: Não é necessário especificar `spark.jars.packages` no código
2. **Execute dentro do container**: O PySpark só está disponível dentro do container
3. **Dados persistentes**: Os dados ficam salvos em `./datalake/spark-timetravel/`
4. **MinIO deve estar rodando**: O script precisa do MinIO para funcionar como storage S3

## 🎓 Recursos Adicionais

- [Documentação Delta Lake](https://docs.delta.io/)
- [Delta Lake Time Travel](https://docs.delta.io/latest/delta-batch.html#-deltatimetravel)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
