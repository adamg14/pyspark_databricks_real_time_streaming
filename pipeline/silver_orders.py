# read and write from the bronze orders delta table
import pyspark
from pyspark.sql import SparkSession
from bronze_orders import bronze_path
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType


silver_schema =  StructType(
    [
        StructField("order_id", StringType()),
        StructType("user_id", IntegerType()),
        StructType("product_id", IntegerType()),
        StructType("price", DoubleType()),
        StructType("currency", StringType()),
        StructType("event_datetime", ),
        StructField("channel", StringType())
    ]
)
silver_path = "data/delta/silver_orders"

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