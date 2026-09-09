import json
import random
import time
from datetime import datetime, timezone
from kafka import KafkaProducer

# Use explicit loopback IP for WSL2-to-Docker routing
BROKER = '127.0.0.1:19092'
TOPIC = 'financial_trades'

ACCOUNTS = [f"ACC_{i:04d}" for i in range(1, 21)]
SYMBOLS = ['AAPL', 'NVDA', 'MSFT', 'AMZN', 'GOOGL', 'TSLA']
ORDER_TYPES = ['BUY', 'SELL']

print(f"Connecting to Redpanda broker at {BROKER}...")

producer = KafkaProducer(
    bootstrap_servers=[BROKER],
    api_version=(2, 8, 0),
    request_timeout_ms=5000,
    metadata_max_age_ms=5000,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_trade_event():
    return {
        "trade_id": f"TRD_{random.randint(1000000, 9999999)}",
        "account_id": random.choice(ACCOUNTS),
        "symbol": random.choice(SYMBOLS),
        "order_type": random.choice(ORDER_TYPES),
        "quantity": random.randint(10, 500),
        "price": round(random.uniform(100.0, 900.0), 2),
        "trade_timestamp": datetime.now(timezone.utc).isoformat(),
        "record_source": "STREAMING_EXCHANGE_FEED"
    }

if __name__ == "__main__":
    print(f"🚀 Streaming trade events to Redpanda broker at {BROKER}...")
    try:
        while True:
            event = generate_trade_event()
            future = producer.send(TOPIC, value=event)
            record_metadata = future.get(timeout=10)
            print(f"Sent: {event['trade_id']} | {event['symbol']} | {event['quantity']} @ ${event['price']} -> Partition {record_metadata.partition} @ Offset {record_metadata.offset}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nProducer stopped.")