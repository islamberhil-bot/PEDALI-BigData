from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("PEDALI-Partie1-Cluster")
    .getOrCreate()
)

sc = spark.sparkContext
sc.setLogLevel("WARN")

print("=== PEDALI CLUSTER DISTRIBUE ===")
print("Version Spark :", spark.version)
print("Master :", sc.master)
print("AppName :", sc.appName)
print("Coeurs disponibles :", sc.defaultParallelism)

rdd = sc.parallelize(range(1, 1001), 2)
resultat = rdd.map(lambda x: x * x).sum()

print("Nombre de partitions :", rdd.getNumPartitions())
print("Somme des carres :", resultat)

assert spark.version == "3.5.3"
assert sc.master == "spark://spark-master:7077"
assert resultat == 333833500

print("TEST DISTRIBUE REUSSI")

spark.stop()
