from pyspark.sql import SparkSession
from delta.tables import DeltaTable
import urllib.request

# Configurações para Spark 3.5.7 com Delta Lake 3.2.0 e MinIO
# Os JARs já estão incluídos na imagem spark-delta:3.5.7
spark = SparkSession.builder.appName("bronze_delta")\
  .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")\
  .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")\
  .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")\
  .config("spark.hadoop.fs.s3a.access.key", "admin")\
  .config("spark.hadoop.fs.s3a.secret.key", "password")\
  .config("spark.hadoop.fs.s3a.path.style.access", "true")\
  .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")\
  .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")\
  .getOrCreate()

# URLs e caminhos
BRONZE_PATH = "s3a://bronze"
CINTILOGRAFIA_URL = "https://raw.githubusercontent.com/JoaoVitorMartinezM/data-engineering/refs/heads/main/data/dados_cintilografia.csv"

# 1. BAIXANDO DADOS DA URL DO GITHUB
print("\n--- 1. BAIXANDO DADOS DA URL DO GITHUB ---")
temp_file = "/tmp/dados_cintilografia.csv"

# Download usando urllib
urllib.request.urlretrieve(CINTILOGRAFIA_URL, temp_file)
print(f"Arquivo baixado com sucesso para: {temp_file}")

# 2. LENDO E PROCESSANDO DADOS
print("\n--- 2. LENDO E PROCESSANDO DADOS ---")
df = spark.read.csv(temp_file, header=True, inferSchema=True)
print(f"Total de registros lidos: {df.count()}")
print("Schema dos dados:")
df.printSchema()

# 3. LIMPANDO NOMES DAS COLUNAS PARA DELTA LAKE
print("\n--- 3. AJUSTANDO NOMES DAS COLUNAS ---")
# Substituir espaços, parênteses e caracteres especiais por underscore
for col_name in df.columns:
    clean_name = col_name.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_").replace("º", "_num").replace("Nº", "num")
    df = df.withColumnRenamed(col_name, clean_name)

print("Nomes de colunas ajustados:")
df.printSchema()

# 4. SALVANDO NO FORMATO DELTA
print("\n--- 4. SALVANDO NO BRONZE LAYER ---")
df.write.format("delta").mode("overwrite").save(BRONZE_PATH + "/dados_cintilografia")

# 4. VERIFICANDO DADOS SALVOS
print("\n--- 5. VERIFICANDO DADOS SALVOS NO BRONZE ---")
df_bronze = spark.read.format("delta").load(BRONZE_PATH + "/dados_cintilografia")
df_bronze.show(5, truncate=False)
print(f"Total de registros no bronze: {df_bronze.count()}")

# Limpando arquivo temporário
import os
os.remove(temp_file)

print("\n✅ Dados carregados no bronze layer com sucesso!")
spark.stop()