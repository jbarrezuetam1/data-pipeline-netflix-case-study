from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Parquet").master("local[*]").getOrCreate()

employees_data = [
	("Ana","Data Engineer",3200,4),
	("Luis","Data Engineer",2800,2),
	("Marta","Marketing",2100,5),
	("Pedro","Marketing",1900,1),
	("Sofia","Data Engineer",4100,7),
	("Carlos","Sales",2500,3),
]
employees = spark.createDataFrame(employees_data,["name","dep","salary","years"])

print("--- Writing in Parquet ---")
employees.write.mode("overwrite").parquet("week2-pyspark-practice/output-employees_parquet")
print("Done, saved in week2-pyspark-practice/output/employees_parquet")

print("--- Reading from Parquet ---")
employees_read = spark.read.parquet("week2-pyspark-practice/output-employees_parquet")
employees_read.show()

print("--- Schema Auto ---")
employees_read.printSchema()

spark.stop()