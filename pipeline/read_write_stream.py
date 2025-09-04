# reading and writing (w/o storing to a delta table)
# the purpose of this script is to test the connection between pyspark and the local apache kafka bootstrap server
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructField,
    StructType,
    StringType,
    IntegerType,
    DoubleType
)

print(f"Pyspark version: {pyspark.__version__}")

# required packages for setting up the correct spark session
builder = (
    SparkSession.builder \
        .master("local[*]") \
        .appName("medallion-architecture") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.jars.packages",
                "io.delta:delta-spark_2.12:3.2.0,"
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,"
                "org.apache.kafka:kafka-clients:3.5.1")
)

spark = builder.getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# data path
bronze_path = "data/delta/bronze_orders"

try:
    kafka_stream = (
        spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:19092") \
        .option("subscribe", "purchase_events") \
        .option("startingOffsets", "earliest") \
        .load() \
        .selectExpr("CAST(value AS STRING) AS json_data", "timestamp")
    )

    print("Kafka data stream captured.")

    query = kafka_stream \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .start()
    
    query.awaitTermination(30)
    query.stop()
except Exception as e:
    print(f"An error occurred: {e}")