from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark import SparkContext

spark = SparkSession.builder.appName("YelpReviewTransform").getOrCreate()

# Lecture du JSON depuis GCS
#input_path = "gs://datasparkyelp-yelp-raw/review/yelp_academic_dataset_review.json"
#output_path = "gs://datasparkyelp-yelp-intermediate/review"


input_path = "data/yelp_academic_dataset_tip.json"
output_path = "intermediate/datasparkyelp-yelp-intermediate/tip"


df = spark.read.json(input_path)

df = spark.read.option("mode", "PERMISSIVE").json(input_path)

if "_corrupt_record" in df.columns:
    df = df.filter(col("_corrupt_record").isNull()).drop("_corrupt_record")


df.show()
df.printSchema()
# Transformations

df_transformed = df.withColumn("date", to_timestamp(col("date"))) \
    .withColumn("year", year(col("date"))) \
    .dropna(subset=["business_id", "user_id", "text"]) \
    .dropDuplicates()


df_transformed.write \
    .partitionBy("year") \
    .mode("overwrite") \
    .parquet(output_path)


spark.stop()
