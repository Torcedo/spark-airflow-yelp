from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark import SparkContext

spark = SparkSession.builder.appName("YelpBusinessTransform").getOrCreate()

input_path = "data/yelp_academic_dataset_business.json"
output_path = "intermediate/datasparkyelp-yelp-intermediate/business"

df = spark.read.option("mode", "PERMISSIVE").json(input_path)

if "_corrupt_record" in df.columns:
    df = df.filter(col("_corrupt_record").isNull()).drop("_corrupt_record")

df.show()
df.printSchema()

df_transformed = df.dropna(subset=["business_id", "name", "address", "city", "state"]) \
    .dropDuplicates(["business_id"]) \
    .withColumn("is_open", col("is_open").cast("boolean")) \
    .withColumn("review_count", col("review_count").cast("int")) \
    .withColumn("stars", col("stars").cast("double"))

df_transformed.write \
    .partitionBy("state") \
    .mode("overwrite") \
    .parquet(output_path)

spark.stop()
