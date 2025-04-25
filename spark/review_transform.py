from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import sys

spark = SparkSession.builder.appName("YelpReviewTransform").getOrCreate()

# Récupérer les arguments passés par Airflow
input_path = sys.argv[1]
output_path = sys.argv[2]

# Lecture du JSON
df = spark.read.option("mode", "PERMISSIVE").json(input_path)

# Nettoyage si champ corrompu
if "_corrupt_record" in df.columns:
    df = df.filter(col("_corrupt_record").isNull()).drop("_corrupt_record")

# Transformation avec duplication de la colonne de partition
df_transformed = df.withColumn("date", to_timestamp(col("date"))) \
    .withColumn("text_length", length(col("text"))) \
    .withColumn("engagement", col("useful") + col("cool") + col("funny")) \
    .withColumn("year_partition", year("date")) \
    .dropna(subset=["review_id", "user_id", "business_id"]) \
    .dropDuplicates(["review_id"])

# Écriture partitionnée
df_transformed.write \
    .partitionBy("year_partition") \
    .mode("overwrite") \
    .parquet(output_path)

spark.stop()
