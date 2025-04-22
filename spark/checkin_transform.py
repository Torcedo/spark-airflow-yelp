from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp, year, col
import sys

# Initialisation Spark
spark = SparkSession.builder \
    .appName("YelpCheckinTransform") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
    .getOrCreate()
# Récupérer les arguments passés par Airflow

input_path = sys.argv[1]
output_path = sys.argv[2]

df = spark.read.option("multiline", "false").json(input_path)

# Transformation
df_clean = df.withColumn("timestamp", to_timestamp(col("timestamp"), "yyyy-MM-dd HH:mm:ss"))
df_with_year = df_clean.withColumn("year", year(col("timestamp")))

df_with_year = df_with_year.repartition(100, "year")

df_with_year.write \
    .mode("overwrite") \
    .partitionBy("year") \
    .parquet(output_path)

spark.stop()
