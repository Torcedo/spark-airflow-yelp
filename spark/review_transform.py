from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import sys

spark = SparkSession.builder.appName("YelpReviewTransform").getOrCreate()

# Récupérer les arguments passés par Airflow
input_path = sys.argv[1]
output_path = sys.argv[2]

df = spark.read.option("mode", "PERMISSIVE").json(input_path)

if "_corrupt_record" in df.columns:
    df = df.filter(col("_corrupt_record").isNull()).drop("_corrupt_record")


df_transformed = df.withColumn("date", to_timestamp(col("date"))) \
    .withColumn("text_length", length(col("text"))) \
    .withColumn("engagement", col("useful") + col("cool") + col("funny"))\
    .withColumn("year", year("date")) \
    .withColumn("month", month("date")) \
    .dropna(subset=["review_id", "user_id", "business_id"])\
    .dropDuplicates(["review_id"])

#Partionnement par année au format parquet
df_transformed.write \
    .partitionBy("year") \
    .mode("overwrite") \
    .parquet(output_path)

spark.stop()
