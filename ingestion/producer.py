# A Kafka Producer which emits event messages on purchase of a product
import json
import time
import random
import uuid
import datetime
from kafka import KafkaProducer
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

print(API_KEY)
CONFLUENT_CONFIG = {
    "bootstrap_servers": "pkc-l6wr6.europe-west2.gcp.confluent.cloud:9092",
    "security_protocol": "SASL_SSL",
    "sasl_mechanism": "PLAIN",
    "sasl_plain_username": API_KEY,
    "sasl_plain_password": API_SECRET
}

kafka_producer = KafkaProducer(
    bootstrap_servers=CONFLUENT_CONFIG["bootstrap_servers"],
    security_protocol=CONFLUENT_CONFIG["security_protocol"],
    sasl_mechanism=CONFLUENT_CONFIG["sasl_mechanism"],
    sasl_plain_username=CONFLUENT_CONFIG["sasl_plain_username"],
    sasl_plain_password=CONFLUENT_CONFIG["sasl_plain_password"],
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)

def purchase_event():
    currencies = ["USD", "GBP", "EUR"]
    channels = ["Amazon", "Google", "eBay", "Meta", "TikTok", "Email", "Affilliate"]
    event = {
        # A random unique string to act as a unique identifier
        "order_id": str(uuid.uuid4()),
        "user_id": random.randint(1, 1000),
        "product_id": random.randint(1, 100),
        "price": round(random.uniform(5, 200), 2),
        "currency": random.choice(currencies),
        "event_datetime": datetime.datetime.now().isoformat(),
        "channel": random.choice(channels)
    }
    try:

        kafka_producer.send("purchase_event", event)
        kafka_producer.flush()
        print("Kafka message sent successfully.")
    except Exception as e:
        print(f"Error sending event: {e}")


if __name__ == "__main__":
    while True:
        import random
        time.sleep(random.randint(1, 5))        
        purchase_event()