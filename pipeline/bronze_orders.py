# real time streaming, from the apache kafka message stream (bootstrap server) to the bronze orders Pyspark delta table
# the schema of the bronze table keeps the Kafka message in the json format, along with the load datetime
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
        .appName("medallion_ingestion") \
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
    
    query.awaitTermination(10)
    query.stop()

    try:
        # continous streaming job
        kafka_stream_write = kafka_stream \
            .writeStream \
            .format("delta") \
            .outputMode("append") \
            .option("checkpointLocation", f"{bronze_path}/_checkpoints") \
            .option("path", bronze_path) \
            .start()

        print("Continous ingestion to Delta Lake...")
        kafka_stream_write.awaitTermination()

    except Exception as e:
        print(f"An error occurred with the continous streaming of kafka messages: {e}")
    
except Exception as e:
    print(f"An error occurred: {e}")