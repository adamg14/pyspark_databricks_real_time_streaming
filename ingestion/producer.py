# A Kafka Producer which emits event messages on purchase of a product
import json
import time
import random
import uuid
import datetime
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer= lambda value: json.dumps(value).encode()
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
    producer.send(event)

if __name__ == "__main__":
    while True:
        import random
        time.sleep(random.rand(1, 5))
        
        purchase_event()