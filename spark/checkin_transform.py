from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp, year, col
import sys

spark = SparkSession.builder \
    .appName("YelpCheckinTransform") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
    .getOrCreate()

input_path = sys.argv[1]
output_path = sys.argv[2]

df = spark.read.option("multiline", "false").json(input_path)

# Parse timestamp et extraire l'année
df_transformed = df.withColumn("timestamp", to_timestamp(col("timestamp"), "yyyy-MM-dd HH:mm:ss")) \
    .withColumn("year_partition", year(col("timestamp"))) 

# Partitionnement sur GCS par dossier d’année
df_transformed.write \
    .mode("overwrite") \
    .partitionBy("year_partition") \
    .parquet(output_path)

spark.stop()
