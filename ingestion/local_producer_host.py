from confluent_kafka import Producer
import random
import time
import datetime
import uuid
import json

print("hello world")

producer_host = Producer({
    "bootstrap.servers": "localhost:19092",
})

def purchase_event():
    print("Generating event...")
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
        print("Sending event...")
        producer_host.produce(
            topic="purchase_events",
            value=json.dumps(event).encode("utf-8")
            )
        producer_host.flush()
        print("Kafka message sent successfully.")
    except Exception as e:
        print(f"Error sending event: {e}")


if __name__ == "__main__":
    while True:
        time.sleep(random.randint(1, 5))
        purchase_event()