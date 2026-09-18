from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, round

spark = SparkSession.builder.appName("DataFrameBasics").master("local[*]").getOrCreate()

data = [
    ("Ana","Data Engineering", 3200, 4),
    ("Luis","Data Engineering", 2800, 2),
    ("Marta","Marketing", 2100, 5),
    ("Pedro","Marketing", 1900, 1),
    ("Sofia","Data Engineering", 4100, 7),
    ("Carlos","Sales", 2500, 3),
]
columns = ["name","job","salary","experience_years"]

df = spark.createDataFrame(data,columns)

print("-- DataFrame Completed --")
df.show()

print("-- SELECT: Only name and salary --")
df.select("name","salary").show()

print("-- FILTER: Salary > 2500 --")
df.filter(df.salary > 2500).show()

print("-- GROUP BY: Avg salary per job --")
df.groupBy("job").agg(round(avg("salary"),1).alias("average_salary")).show()

print("-- WITHCOLUMN: Add new column: bonus (10% of salary) --")
df.withColumn("bonus", df.salary * 0.10).show()

spark.stop()
