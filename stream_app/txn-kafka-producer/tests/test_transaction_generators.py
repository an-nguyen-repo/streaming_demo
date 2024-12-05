from src.generators.user_store_manager import UserStoreManager
from src.generators.transaction_generators import TransactionGenerator
from src.models.data_models import *

TEST_PROFILE = UserProfile(
    user_id = 'user-00000',
    main_location = Location(country = 'Vietnam'),
    average_amt = 10.0,
    total_amt = 10.0,
    txn_count = 1,
    last_txn_timestamp = datetime(2024,1,1),
    last_txn_location = Location(country = 'Vietnam'),
)


def test_txn_gen_generate_normal_transaction():
    user_store = UserStoreManager() 
    user_store.update_state_store(
        user_id= TEST_PROFILE.user_id,
        updated_profile= TEST_PROFILE
        )
    txn_generator = TransactionGenerator()
    transaction = txn_generator.generate(
        user_profile= TEST_PROFILE,
        fraud_actions= []
    )
    print(f'Normal: {transaction}')

    assert True

def test_txn_gen_generate_time_fraud_transaction():
    user_store = UserStoreManager() 
    user_store.update_state_store(
        user_id= TEST_PROFILE.user_id,
        updated_profile= TEST_PROFILE
        )
    txn_generator = TransactionGenerator()
    transaction = txn_generator.generate(
        user_profile= TEST_PROFILE,
        fraud_actions= [FraudType.TIME_FRAUD]
    )
    print(f'Time Fraud: {transaction}')


    assert (transaction.timestamp - TEST_PROFILE.last_txn_timestamp).seconds <= 20


def test_txn_gen_generate_proximity_fraud_transaction():
    user_store = UserStoreManager() 
    user_store.update_state_store(
        user_id= TEST_PROFILE.user_id,
        updated_profile= TEST_PROFILE
        )
    txn_generator = TransactionGenerator()
    transaction = txn_generator.generate(
        user_profile= TEST_PROFILE,
        fraud_actions= [FraudType.PROXIMITY_FRAUD]
    )
    print(f'Proximity Fraud: {transaction}')
    assert transaction.location != TEST_PROFILE.main_location 

def test_txn_gen_generate_value_fraud_transaction():
    user_store = UserStoreManager() 
    user_store.update_state_store(
        user_id= TEST_PROFILE.user_id,
        updated_profile= TEST_PROFILE
        )
    txn_generator = TransactionGenerator()
    transaction = txn_generator.generate(
        user_profile= TEST_PROFILE,
        fraud_actions= [FraudType.HIGH_VALUE_FRAUD]
    )
    print(f'Value Fraud: {transaction}')

    assert (transaction.amount/ TEST_PROFILE.average_amt) >=3



