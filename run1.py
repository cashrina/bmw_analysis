from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("BMW Analysis") \
    .getOrCreate()

df = spark.read.csv("bmw.csv", header=True)

# Select subset of features and filter for balance > 0
filtered_df = df.select("model", "year").filter("price > 20000")

# Generate summary statistics
filtered_df.summary().show()

