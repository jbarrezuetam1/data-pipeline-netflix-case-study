from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("LazyEvaluation").master("local[*]").getOrCreate()


employees_data = [
	("Ana","Data Engineer",3200,4),
	("Juan","Data Engineer",4800,7),
	("Luis","Marketing",2100,3),
	("Pedro","Data Engineer",1800,2),
	("Carlos","Marketing",3500,4),
	("Sergio","Sales",2900,3),
]

employees = spark.createDataFrame(employees_data,["name","dep","salary","years"])

print("***** Step 1: Adding Filter (No execution yet) *****")
filter = employees.filter(col("salary")>3000)
print("***** Filter is saved but Spark has not executed *****")


print("***** Step 2: SELECT statement (No execution yet) *****")
selection = filter.select("name","salary")
print("***** Select is saved but not executed")

print("***** Step 3: Call to action with .show() = Execute the Data Transformation")
selection.show()

print("Spark - Backstage")
selection.explain()

spark.stop()