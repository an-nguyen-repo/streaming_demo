from src.generators.user_store_manager import UserStoreManager
from abc import ABC, abstractmethod
from datetime import datetime , timedelta
import random 
from src.models.data_models import *
import random 
import src.utils.utils as ut
from faker import Faker

class TransactionBehavior(ABC):

    @abstractmethod
    def apply(self, transaction: Transaction, user_profile: UserProfile):
        pass

class NormalBehavior(TransactionBehavior):
    def __init__(self):
        super().__init__()

    def apply(self, transaction: Transaction, user_profile: UserProfile):
        transaction.amount = user_profile.average_amt * ut.random_float_in_range(
            a = TransactionConstants.AMOUNT_FACTOR_RANGE.low,
            b  = TransactionConstants.AMOUNT_FACTOR_RANGE.high
        )

        if abs((transaction.timestamp - user_profile.last_txn_timestamp).seconds) <= TransactionConstants.NORMAL_TXN_TIME_RANGE.low:
            transaction.timestamp = user_profile.last_txn_timestamp + timedelta(seconds = random.randint(30, 1000))

        return transaction 

class HighAmountFraudBehavior(TransactionBehavior):
    def __init__(self):
        super().__init__()

    def apply(self, transaction: Transaction, user_profile: UserProfile):
        transaction.amount = user_profile.average_amt * ut.random_float_in_range(
            a = TransactionConstants.FRAUD_FACTOR_RANGE.low,
            b = TransactionConstants.FRAUD_FACTOR_RANGE.high
        )
        return transaction

class ProximityFraudBehavior(TransactionBehavior):
    def __init__(self):
        super().__init__()

    def apply(self, transaction: Transaction, user_profile: UserProfile):
        fake = Faker()
        while True:
            loc = Location(country = fake.country())
            if loc != user_profile.main_location:
                transaction.location = loc
                transaction.timestamp = user_profile.last_txn_timestamp + timedelta(
                    seconds= random.randint(
                        a = TransactionConstants.LOCATION_TIME_WINDOW.low,
                        b = TransactionConstants.LOCATION_TIME_WINDOW.high)
                    )
                return transaction

class TimeSensitiveFraudBehavior(TransactionBehavior):
    def __init__(self):
        super().__init__()

    def apply(self, transaction: Transaction, user_profile: UserProfile):
        transaction.timestamp = user_profile.last_txn_timestamp + timedelta(
            milliseconds= random.randint(
                a = TransactionConstants.CLOSE_TIME_WINDOW.low,
                b = TransactionConstants.CLOSE_TIME_WINDOW.high
            )
        )

        return transaction

class TransactionGenerator:
    def __init__(self,):
        self.fraud_behaviors = {
            FraudType.HIGH_VALUE_FRAUD : HighAmountFraudBehavior(),
            FraudType.PROXIMITY_FRAUD : ProximityFraudBehavior(),
            FraudType.TIME_FRAUD : TimeSensitiveFraudBehavior()
        }
        

    def generate(self,user_profile: UserProfile, fraud_actions: list = []):
        
        #empty transaction
        transaction = Transaction(
            user_id = user_profile.user_id,
            location = user_profile.main_location
        )

        if user_profile.has_no_transact_history():
            #enfore first transact as normal
            transaction.amount = ut.random_float_in_range(
            TransactionConstants.AMOUNT_RANGE.low, 
            TransactionConstants.AMOUNT_RANGE.high
            )
            return transaction

        # apply normal behavior
        transaction = NormalBehavior().apply(transaction , user_profile)

        # appy fraudulent transaction if exists
        if fraud_actions:
            for fraud_type in fraud_actions:
                behavior = self.fraud_behaviors[fraud_type]
                transaction = behavior.apply(transaction, user_profile)
            transaction.transaction_type = TransactionType.FRAUD
        return transaction


class TransactionSystemController:
    def __init__(self,):
        self.user_store = UserStoreManager()
        self.generator = TransactionGenerator()

    def _bootstrap_user_store(self, n_users: int = 1000 ):
        for i in range(n_users):
            user_profile = self.user_store.create_empty_profile()
            self.user_store.update_state_store(
                user_id = user_profile.user_id,
                updated_profile= user_profile
            )

    
        

