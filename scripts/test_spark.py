from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .master("local[2]")
    .appName("PEDALI-Test-Spark")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

print("=== TEST PEDALI ===")
print("Version :", spark.version)
print("Master :", spark.sparkContext.master)
print("Coeurs :", spark.sparkContext.defaultParallelism)

resultat = spark.range(1, 1001).count()

print("Nombre de lignes :", resultat)
print("TEST REUSSI" if resultat == 1000 else "TEST ECHOUE")

spark.stop()
