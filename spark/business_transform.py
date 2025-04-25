from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import sys

spark = SparkSession.builder.appName("YelpBusinessTransform").getOrCreate()

# Récupérer les arguments passés par Airflow
input_path = sys.argv[1]
output_path = sys.argv[2]


df = spark.read.option("mode", "PERMISSIVE").json(input_path)

if "_corrupt_record" in df.columns:
    df = df.filter(col("_corrupt_record").isNull()).drop("_corrupt_record")

df_transformed = df.dropna(subset=["business_id", "name", "address", "city", "state"]) \
    .dropDuplicates(["business_id"]) \
    .withColumn("is_open", col("is_open").cast("boolean")) \
    .withColumn("review_count", col("review_count").cast("int")) \
    .withColumn("stars", col("stars").cast("double")) \
    .withColumn("state_partition", col("state"))

df_transformed.write \
    .partitionBy("state") \
    .mode("overwrite") \
    .parquet(output_path)

spark.stop()
