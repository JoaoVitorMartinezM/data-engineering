from pyspark.sql import SparkSession

spark = SparkSession.builder.appName('DataQuality') \
  .config('spark.sql.extensions', 'io.delta.sql.DeltaSparkSessionExtension') \
  .config('spark.sql.catalog.spark_catalog', 'org.apache.spark.sql.delta.catalog.DeltaCatalog') \
  .config('spark.hadoop.fs.s3a.endpoint', 'http://minio:9000') \
  .config('spark.hadoop.fs.s3a.access.key', 'admin') \
  .config('spark.hadoop.fs.s3a.secret.key', 'password') \
  .config('spark.hadoop.fs.s3a.path.style.access', 'true') \
  .config('spark.hadoop.fs.s3a.impl', 'org.apache.hadoop.fs.s3a.S3AFileSystem') \
  .config('spark.hadoop.fs.s3a.connection.ssl.enabled', 'false') \
  .getOrCreate()

print('=' * 60)
print('🏗️  VERIFICAÇÃO COMPLETA DOS LAYERS')
print('=' * 60)

# Bronze Layer
bronze_df = spark.read.format('delta').load('s3a://bronze/dados_cintilografia')
bronze_count = bronze_df.count()
print(f'🥉 Bronze Layer: {bronze_count} registros')

# Silver Layer  
silver_df = spark.read.format('delta').load('s3a://silver/dados_cintilografia')
silver_count = silver_df.count()
print(f'🥈 Silver Layer: {silver_count} registros')

# Estatísticas
print()
print('📊 ESTATÍSTICAS:')
print(f'   Total pacientes únicos (Bronze): {bronze_df.select("ID_PACIENTE").distinct().count()}')
print(f'   Total pacientes únicos (Silver): {silver_df.select("ID_PACIENTE").distinct().count()}')

print()
print('✅ PIPELINE BRONZE → SILVER FUNCIONANDO!')
spark.stop()