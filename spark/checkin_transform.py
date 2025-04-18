from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.appName("YelpCheckinTransform").getOrCreate()


# Lecture du JSON depuis GCS
#input_path = "gs://datasparkyelp-yelp-raw/review/yelp_academic_dataset_review.json"
#output_path = "gs://datasparkyelp-yelp-intermediate/review"


input_path = "data/yelp_academic_dataset_checkin.json"
output_path = "intermediate/datasparkyelp-yelp-intermediate/checkin"

df = spark.read.option("mode", "PERMISSIVE").json(input_path)

if "_corrupt_record" in df.columns:
    df = df.filter(col("_corrupt_record").isNull()).drop("_corrupt_record")

# Séparation des dates
df_cleaned = df.filter(col("date").isNotNull()) \
    .withColumn("checkin_time", explode(split(col("date"), ","))) \
    .withColumn("checkin_time", to_timestamp(col("checkin_time").cast("string"))) \
    .withColumn("year", year("checkin_time")) \
    .withColumn("month", month("checkin_time")) \
    .dropna(subset=["business_id", "checkin_time"])


df_cleaned= df_cleaned.repartition(10)


# Export détaillé avec les dates (partitionné)
df_cleaned.write \
    .partitionBy("year") \
    .mode("overwrite") \
    .parquet(output_path + "/detailed")


spark.stop()
