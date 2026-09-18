from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("HelloSpark") \
    .master("local[*]") \
    .getOrCreate()

print("Spark version:", spark.version)
print("Number of partitions available:", spark.sparkContext.defaultParallelism)

spark.stop()