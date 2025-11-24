from pyspark.sql import SparkSession
from pyspark.sql import functions as f

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
GOLD_PATH = "s3a://gold"
CINTILOGRAFIA_PATH = "s3a://silver/dados_cintilografia"
# 1. ESCRITA INICIAL (VERSÃO 0)
print("\n--- LENDO DADOS SILVER ---")
df = spark.read.format("delta").load(CINTILOGRAFIA_PATH)
df.show(2)

print("--- AGREGANDO DADOS ---")
df = df.withColumn('ANO', f.year('DATA'))
df = df.withColumn('MES', f.month('DATA'))

print('--- MOSTRANDO DADOS ---')
df.show(2)

print('--- ESCREVENDO DADOS EM GOLD ---')
df.write.format("delta").mode("overwrite").partitionBy(['ANO', 'MES']).save(GOLD_PATH + "/dados_cintilografia")
#
#
print("DADOS AGREGADOS SALVOS COM SUCESSO EM GOLD")
spark.stop()