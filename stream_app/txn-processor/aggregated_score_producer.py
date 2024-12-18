from kafka import KafkaConsumer
import json
import psycopg2
from psycopg2.extras import execute_batch

# Configure Kafka consumer
consumer = KafkaConsumer(
    'transaction-final',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# PostgreSQL connection
conn = psycopg2.connect(
    dbname="frauddb",
    user="myuser",
    password="mypassword",
    host="postgres",
    port="5432"
)
cursor = conn.cursor()

# DELETE  table 
cursor.execute("""
    DROP TABLE IF EXISTS fraud_events 
""")
conn.commit()
print('CLEAN fraud_events TABLE')

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
print('CREATE fraud_events TABLE')
conn.commit()

# Consume messages and insert into PostgreSQL
batch_size = 100
batch = []
insert_query = """
    INSERT INTO fraud_events (
        transaction_id, user_id, txn_time, amount,location, transaction_type, fraud_score
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
"""
counter = 0 

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
        print(f'Flush data - batch index {counter} - Total messages: {counter * batch_size}')
        counter += 1 
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