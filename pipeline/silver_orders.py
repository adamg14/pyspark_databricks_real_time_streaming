# creating a silver order delta table that enforces a defined schema 
import pyspark
from pyspark.sql import SparkSession
from pipeline.bronze_orders import bronze_path
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
import pyspark.sql.functions as F

silver_schema =  StructType(
    [
        StructField("order_id", StringType()),
        StructField("user_id", IntegerType()),
        StructField("product_id", IntegerType()),
        StructField("price", DoubleType()),
        StructField("currency", StringType()),
        StructField("event_datetime", TimestampType()),
        StructField("channel", StringType())
    ]
)

silver_path = "data/delta/silver_orders"


def schema_enforment():

    builder = (
        SparkSession.builder.master("local[*]")
        .appName("bronze-analysis")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.2.0")  
    )

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    bronze_orders = spark.read.format("delta").load(bronze_path)

    silver_orders = bronze_orders.select(
        F.from_json("json_data", silver_schema) \
            .alias("parsed_json"),
        F.col("timestamp") \
            .alias("ingested_timestamp")
    ).select(
        F.col("parsed_json.order_id").alias("order_id"),
        F.col("parsed_json.user_id").alias("user_id"),
        F.col("parsed_json.product_id").alias("product_id"),
        F.col("parsed_json.price").alias("price"),
        F.col("parsed_json.currency").alias("currency"),
        F.col("parsed_json.event_datetime").alias("event_timestamp"),
        F.col("parsed_json.channel").alias("channel"),
        F.col("ingested_timestamp")
    )

    print("Writing to silver orders...")
    silver_orders.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .save(silver_path)
    print("Delta table written to successfully")

    silver_orders = spark.read.format("delta").load(silver_path)
    print(f"silver delta table head: {silver_orders.show(5, truncate=True)}")
    print(f"silver delta table schema: {silver_orders.printSchema()}")


if __name__ == '__main__':
    schema_enforment()