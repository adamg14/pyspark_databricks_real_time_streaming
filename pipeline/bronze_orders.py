from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip
from pyspark.sql.types import (
    StructField,
    StructType,
    StringType,
    IntegerType,
    DoubleType
)

purchase_event_schema = StructType([
    StructField("order_id", StringType()),
    StructField("user_id", IntegerType()),
    StructField("product_id", IntegerType()),
    StructField("price", DoubleType()),
    StructField("currency", StringType()),
    StructField("event_datetime", StringType()),
    StructField("channel", StringType())
])


# Spark + Delta session defintion
builder = (
    SparkSession.builder.master("local[*]") \
    .appName("medallion-architecture") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog",  "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
    .config("spark.jars.packages", "org.apache.kafka:kafka-clients:3.5.1")
)

spark = configure_spark_with_delta_pip(builder).getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# data paths
bronze_path = "data/delta/bronze_orders"

try:
    # reading data from the kafka stream and storing it as a JSON string in the bronze delta table
    raw_orders = (
        spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:19092") \
        .option("subscribe", "purchase_events") \
        .option("startingOffsets", "earliest") \
        .load() \
        .selectExpr("CAST(value AS STRING) AS JSON")
    )

    print("Kafka data message stream captured by Pyspark")
    print(f"Stream schema: {raw_orders.schema}")

    raw_orders_query = raw_orders.writeStream \
        .outputMode("append") \
        .format("console") \
        .start()

    raw_orders_query.awaitTermination(30)
    raw_orders_query.stop()
except Exception as e:
    print(f"error: {e}")