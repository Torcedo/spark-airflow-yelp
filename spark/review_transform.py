from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark import SparkContext

spark = SparkSession.builder.appName("YelpReviewTransform").getOrCreate()

# Lecture du JSON depuis GCS
#input_path = "gs://datasparkyelp-yelp-raw/review/yelp_academic_dataset_review.json"
#output_path = "gs://datasparkyelp-yelp-intermediate/review"


input_path = "data/yelp_academic_dataset_review.json"
output_path = "intermediate/datasparkyelp-yelp-intermediate/review"

df = spark.read.json(input_path)

df = spark.read.option("mode", "PERMISSIVE").json(input_path)

if "_corrupt_record" in df.columns:
    df = df.filter(col("_corrupt_record").isNull()).drop("_corrupt_record")

df.show()
df.printSchema()
# Transformations

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
