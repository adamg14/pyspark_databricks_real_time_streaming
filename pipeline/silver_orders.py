# read and write from the bronze orders delta table
import pyspark
from pyspark.sql import SparkSession
from bronze_orders import bronze_path

builder = (
    SparkSession.builder.master("local[*]")
    .appName("bronze-analysis")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.2.0")  
)

spark = builder.getOrCreate()

bronze_orders = spark.read.format("delta").load(bronze_path)

print(f"bronze order delta table schema: {bronze_orders.printSchema()}")

print(f"delta table head: {bronze_orders.show()}")