from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, round

spark = SparkSession.builder.appName("Joins").master("local[*]").getOrCreate()

#Dataset 1: employees

employees_data = [
	("Ana","Data Engineering",3200,4),
	("Luis","Data Engineering",2800,2),
	("Marta","Marketing",2100,5),
	("Pedro","Marketing",1900,1),
	("Sofia","Data Engineering",4100,7),
	("Carlos","Sales",2500,3),
]

employees = spark.createDataFrame(employees_data, ["name","department","salary","years_exp"])

#Dataset 2: Department (budget)

departments_data = [
	("Data Engineering",500000),
	("Marketing",150000),
	("RRHH",80000),
]
departments = spark.createDataFrame(departments_data, ["department","budget"])

print("-- INNER JOIN --")
employees.join(departments, on="department", how="inner").show()

print("-- LEFT JOIN --")
employees.join(departments, on="department", how="left").show()

print("-- RIGHT JOIN --")
employees.join(departments, on="department", how="right").show()

spark.stop()