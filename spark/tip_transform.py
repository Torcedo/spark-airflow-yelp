from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import sys 

spark = SparkSession.builder.appName("YelpReviewTransform").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")



# Récupérer les arguments passés par Airflow
input_path = sys.argv[1]
output_path = sys.argv[2]



df = spark.read.option("mode", "PERMISSIVE").json(input_path)

if "_corrupt_record" in df.columns:
    df = df.filter(col("_corrupt_record").isNull()).drop("_corrupt_record")




df_transformed = df.withColumn("date", to_timestamp(col("date"))) \
    .withColumn("year", year(col("date"))) \
    .dropna(subset=["business_id", "user_id", "text"]) \
    .dropDuplicates()


df_transformed.write \
    .partitionBy("year") \
    .mode("overwrite") \
    .parquet(output_path)

spark.stop()
