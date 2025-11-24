from pyspark.sql import SparkSession
from pyspark.sql.functions import col

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
SILVER_PATH = "s3a://silver"
CINTILOGRAFIA_PATH = "s3a://bronze/dados_cintilografia"
# 1. ESCRITA INICIAL (VERSÃO 0)
print("\n--- LENDO DADOS BRONZE ---")
df = spark.read.format("delta").load(CINTILOGRAFIA_PATH)
df.show(2)

print("--- TRATANDO DADOS ---")
df = df.filter( col("N_num_REPETIÇÃO") > 0)

df = df.drop("_c0")
subset = ['ID_PACIENTE', 'N_num_REPETIÇÃO', 'HORA_INJEÇÃO_Repouso', 'ATIVIDADE_mCi_Esforço']
df = df.dropna(subset=subset, how='any')
print('--- MOSTRANDO DADOS ---')
df.show(2)

print('--- ESCREVENDO DADOS EM SILVER ---')
df.write.format("delta").mode("overwrite").save(SILVER_PATH + "/dados_cintilografia")
#
#
print("Delta Lake Time Travel concluído com sucesso!")
spark.stop()