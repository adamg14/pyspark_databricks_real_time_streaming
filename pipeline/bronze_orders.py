import dlt
import json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

orders_schema = StructType([
    StructField("order_id", StringType()),
    StructField("user_id", IntegerType()),
    StructField("product_id", IntegerType()),
    StructField("price", DoubleType()),
    StructField("currency", StringType()),
    StructField("event_datetime", StringType()),
    StructField("channel", StringType())
])

@dlt.table(
    name = "bronze_orders",
    comment = "Raw order data ingested from Confluent Cloud (Kafka value as JSON string)"
    table_properties={"quality": "Bronze"}
)
def bronze_orders():
    bootstrap = dbutils.secrets.get("confluent", "confluent_bootstrap")
    api_key = dbutils.secrets.get("confluent", "confluent_api_key")
    api_secret = dbutils.secrets.get("confluent", "confluent_api_secret")
    topic = dlt.conf.get("kafka.topic", "purchase_event")
    jaas = f'org.apache.kafka.common.security.plain.PlainLoginModule required username="{api_key}" password="{api_secret}";'
    
    raw_order_stream = (
        spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", bootstrap) \
            .option("subscribe", topic) \
            .option("startingOffsets", "earliest") \
            .option("kafka.security.protocols", "SASL_SSL") \
            .option("kafka.sasl.mechanism", "PLAIN") \
            .option("kafka.sasl.jaas.config", jaas) \
            .option("kafka.ssl.endpoint.identification.algorithm", "https") \
            .load()
    )

    # the bronze table stores the original data stream as a JSON string
    return raw_order_stream.selectExpr("CAST(value AS STRING) AS json")