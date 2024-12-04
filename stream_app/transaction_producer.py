from kafka import KafkaProducer
import logging 
import json 
from src.generators.transaction_generators import TransactionGenerator
from src.generators.user_store_manager import UserStoreManager
from src.models.data_models import *
import random
import time


TRANSACTION_PER_SEC = 10
FRAUD_TXN_INGEST_INTERVAL = 1000 # Random n fraud transaction within this interval
FRAUD_COUNTER_RANGE = (0, 20)



# Config logging 
logging.basicConfig(level= logging.INFO)
logger = logging.getLogger(__name__)

class KafkaTransactionProducer:
    def __init__(
            self, 
            bootstrap_servers: str, 
            topic_name: str,
            n_users: int
            ):
        self.topic_name = topic_name 
        self.producer = KafkaProducer(
            bootstrap_servers = bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
        )

        self.txn_generator = TransactionGenerator()
        self.user_store = UserStoreManager()
        self.n_users = n_users
        self._bootstrap_user_base()
        print(self.user_store.user_count)

    def _bootstrap_user_base(self, ):
        for i in range(self.n_users):
            user_profile = self.user_store.create_empty_profile()
            self.user_store.update_state_store(
                user_id = user_profile.user_id,
                updated_profile= user_profile
            )

        

    def define_fraud_txn_index(self, ):
        n_fraud_within_interval = random.randint(a = FRAUD_COUNTER_RANGE[0], b = FRAUD_COUNTER_RANGE[1])
        counter = 0
        txn_index = []
        while counter < n_fraud_within_interval:
            random_idx = random.randint(a = 0, b = FRAUD_TXN_INGEST_INTERVAL)
            if random_idx not in txn_index:
                txn_index.append(random_idx)
                counter += 1 

        return txn_index
    
    def random_fraud_types(self, ):
        fraud_types = random.sample(population= list(FraudType), k = random.randint(a =1 , b= 3))
        return fraud_types
    
    def get_random_user_profile(self):
        user_id = random.choice(list(self.user_store.state_store.keys()))
        return self.user_store.get_user_profile(user_id)
    
    def _json_dump(self, transaction: Transaction):
        transaction_dict = transaction.model_dump()
        transaction_dict['timestamp'] = int(transaction_dict['timestamp'].timestamp())
        transaction_dict['transaction_type'] = transaction_dict['transaction_type'].value
        return json.dumps(transaction_dict)
    
    def send_transaction(self, transaction: Transaction ):

        transaction = self._json_dump(transaction)
        try:
            future = self.producer.send(
                self.topic_name,
                value = transaction,
                #key = str(transaction['user_id'].encode('utf-8'))
            ) 
            record_metadata = future.get(timeout = 10)

            if record_metadata.offset %10 ==0:
                print(
                    f"Transaction sent - Topic: {record_metadata.topic}, "
                    f"Partition: {record_metadata.partition}, "
                    f"Offset: {record_metadata.offset}",
                    f"Data: {transaction}",
                    )
        except Exception as e:
            logger.error(f"Error sending transaction: {transaction}\nError: {str(e)}")
 
    def start_streaming(self, transaction_per_sec: int = TRANSACTION_PER_SEC):
        try:
            fraud_txn_index = self.define_fraud_txn_index()
            counter = 0
            
            while True:
                if counter == FRAUD_TXN_INGEST_INTERVAL:
                    counter = 0 
                    fraud_txn_index = self.define_fraud_txn_index()
                if counter in fraud_txn_index: # fraud transaction 
                    fraud_types = self.random_fraud_types()
                else:
                    fraud_types = []

                user_profile = self.get_random_user_profile()

                transaction = self.txn_generator.generate(
                    user_profile = user_profile,
                    fraud_actions= fraud_types
                ) 

                self.send_transaction(transaction)
                
                # update transaction back to the state store 
                self.user_store.update_user_profile(
                    user_id= user_profile.user_id,
                    transaction= transaction
                )


                # increase counter 
                counter += 1 
                time.sleep(1.0/ transaction_per_sec)
        except KeyboardInterrupt:
            logger.info("Streaming stopped by user")

def main():
    KAFKA_CONFIG = {
        'bootstrap_servers': 'localhost:9092',
        'topic_name': 'transactions'
    }

    try:
        producer = KafkaTransactionProducer(
            KAFKA_CONFIG['bootstrap_servers'],
            KAFKA_CONFIG['topic_name'],
            n_users= 1000
        )

        producer.start_streaming(transaction_per_sec = TRANSACTION_PER_SEC )

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")

if __name__ =="__main__":
    main()
