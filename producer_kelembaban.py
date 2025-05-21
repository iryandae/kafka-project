from kafka import KafkaProducer
import json, time, random

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

gudang_ids = ['G1', 'G2', 'G3']

while True:
    data = {
        "gudang_id": random.choice(gudang_ids),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "kelembaban": random.randint(65, 80)
    }
    producer.send('sensor-kelembaban-gudang', value=data)
    print(f"Sent: {data}")
    time.sleep(1)
