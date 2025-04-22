from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import sys

spark = SparkSession.builder.appName("YelpReviewTransform").getOrCreate()

# Lecture du JSON depuis GCS
#input_path = "gs://datasparkyelp-yelp-raw/review/yelp_academic_dataset_review.json"
#output_path = "gs://datasparkyelp-yelp-intermediate/review"


# Récupérer les arguments passés par Airflow
input_path = sys.argv[1]
output_path = sys.argv[2]


df = spark.read.option("mode", "PERMISSIVE").json(input_path)

if "_corrupt_record" in df.columns:
    df = df.filter(col("_corrupt_record").isNull()).drop("_corrupt_record")



df_transformed = df.withColumn("yelping_since", to_timestamp(col("yelping_since"))) \
    .withColumn("nb_friends", size(split(col("friends"), ","))) \
    .withColumn("engagement", col("useful") + col("funny") + col("cool")) \
    .withColumn("elite_count", size(split(col("elite"), ","))) \
    .withColumn("year", year("yelping_since")) \
    .dropna(subset=["user_id", "name"]) \
    .dropDuplicates(["user_id"]) \
    .drop("friends", "elite", "fans", "compliment_hot", "compliment_more",
          "compliment_profile", "compliment_cute", "compliment_list", "compliment_note",
          "compliment_plain", "compliment_cool", "compliment_funny", "compliment_writer",
          "compliment_photos", "useful", "funny", "cool", "type")

df_transformed.write \
    .partitionBy("year") \
    .mode("overwrite") \
    .parquet(output_path)


spark.stop()
