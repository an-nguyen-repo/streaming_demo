from kafka import KafkaConsumer
import json
import psycopg2
from psycopg2.extras import execute_batch

# Configure Kafka consumer
consumer = KafkaConsumer(
    'transaction-final',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# PostgreSQL connection
conn = psycopg2.connect(
    dbname="frauddb",
    user="myuser",
    password="mypassword",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()


# Create table (adjust schema according to your data)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS fraud_events (
        id SERIAL PRIMARY KEY,
        transaction_id VARCHAR(255),
        user_id  VARCHAR(255),
        txn_time INT,
        amount DECIMAL(10,3),
        location VARCHAR(255),
        transaction_type VARCHAR(255),
        fraud_score  INT
    )
""")
conn.commit()

# Consume messages and insert into PostgreSQL
batch_size = 100
batch = []
insert_query = """
    INSERT INTO fraud_events (
        transaction_id, user_id, txn_time, amount,location, transaction_type, fraud_score
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
"""


try:
    for message in consumer:
        data = message.value
        batch.append((
                data['transaction_id'],
                data['user_id'],
                data['txn_time'],
                data['amount'],
                data['location'],
                data['transaction_type'],
                data['fraud_score']
            ))
        
        if len(batch) >= batch_size:
            execute_batch(cursor, insert_query, batch)
            conn.commit()
            batch = []

except KeyboardInterrupt:
    if batch:  # Insert any remaining messages
        execute_batch(cursor, insert_query, batch)
        conn.commit()
    
    cursor.close()
    conn.close()
    consumer.close()