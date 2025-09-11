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
import os

print(f"Pyspark version: {pyspark.__version__}")

# data path
bronze_path = os.getenv("BRONZE_DELTA_PATH", "data/delta/bronze_orders")

def build_spark_session(testing):
    if testing == True:
        builder = SparkSession.builder.master("local[*]").app_name("medallion_ingestion")
    else:
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
    
    return spark

def read_kafka_stream(spark):
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

        # log to the terminal
        query = kafka_stream \
            .writeStream \
            .outputMode("append") \
            .format("console") \
            .start()
        
        query.awaitTermination(10)
        query.stop()

        return kafka_stream
    except Exception as e:
            print(f"An error occurred with the continous streaming of kafka messages: {e}")
        


def read_test_stream(spark):
    """
    use a simulated data source for testing the data ingestion
    """
    df = (
        spark \
        .format("rate") \
        .option("rowsPerSecond", 3) \
        .load() \
        .selectExpr("CAST(value AS STRING) AS value", "timestamp")
    )
    
    return df

def write_to_delta(spark, kafka_stream):
    # writing the ingested data to the delta table for production purposes
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
        kafka_stream_write.awaitTermination(120000)
        kafka_stream_write.stop()
        spark.stop()
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def write_to_memory(df, table_name):
    try:
        memory_write = df \
            .writeStream \
            .format("memory") \
            .outputMode("append") \
            .start()
        print("Writing to memory...")
        memory_write.awaitTermination()
        memory_write.stop()
    except Exception as e:
        print(f"An error has occurred: {e}")


def bronze_ingestion(testing):
    spark = build_spark_session(testing=testing)
    
    try:
        if testing:
            data_streaming = read_kafka_stream(spark)
        else:
            data_streaming = read_test_stream(spark)
        
        if testing:
            write_to_memory(data_streaming)
        else:
            write_to_delta(spark=spark, kafka_stream=data_streaming)
    except Exception as e:
        print(f"An error has occurred: { e }")
    finally:
        spark.stop()

if __name__ == '__main__':
    bronze_ingestion(testing=True)