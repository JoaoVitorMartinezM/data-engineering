from pyspark.sql import SparkSession
from delta.tables import DeltaTable

# Configurações para Spark 3.5.7 com Delta Lake 3.2.0 e MinIO
# Os JARs já estão incluídos na imagem spark-delta:3.5.7
spark = SparkSession.builder.appName("trying_delta")\
  .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")\
  .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")\
  .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")\
  .config("spark.hadoop.fs.s3a.access.key", "admin")\
  .config("spark.hadoop.fs.s3a.secret.key", "password")\
  .config("spark.hadoop.fs.s3a.path.style.access", "true")\
  .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")\
  .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")\
  .getOrCreate()

# Caminho no MinIO
DELTA_PATH = "s3a://spark-timetravel/test"

# 1. ESCRITA INICIAL (VERSÃO 0)
print("\n--- 1. ESCREVENDO VERSÃO 0 ---")
data = [("Alice", 1), ("Bob", 2), ("Charlie", 3)]
df = spark.createDataFrame(data, ["name", "id"])
df.write.format("delta").mode("overwrite").save(DELTA_PATH)
df_v0 = spark.read.format("delta").load(DELTA_PATH)
df_v0.show()

# 2. ATUALIZAÇÃO (VERSÃO 1)
print("\n--- 2. ATUALIZANDO DADOS PARA VERSÃO 1 ---")
deltaTable = DeltaTable.forPath(spark, DELTA_PATH)
deltaTable.update(
    condition="name = 'Bob'",
    set={"name": "'Robert'", "id": "100"}
)

# 3. VERIFICAÇÃO DO ESTADO ATUAL (VERSÃO 1)
print("\n--- 3. LENDO O ESTADO ATUAL (VERSÃO 1) ---")
spark.read.format("delta").load(DELTA_PATH).show()

# 4. TIME TRAVEL: LENDO A VERSÃO ANTIGA
print("\n--- 4. TIME TRAVEL: LENDO VERSÃO 0 (DADOS ANTIGOS) ---")
df_v_old = spark.read.format("delta").option("versionAsOf", 0).load(DELTA_PATH)
df_v_old.show() # Deve mostrar "Bob" e id 2

# 5. VERIFICAR HISTÓRICO DE VERSÕES
print("\n--- 5. HISTÓRICO DE VERSÕES ---")
deltaTable.history().select("version", "timestamp", "operation").show(truncate=False)

print("Delta Lake Time Travel concluído com sucesso!")
spark.stop()