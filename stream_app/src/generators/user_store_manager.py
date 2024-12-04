from src.models.data_models import Transaction, UserProfile, Location
from src.utils.utils import universal_float_format
from faker import Faker

faker = Faker()

class UserStoreManager():
    def __init__(self):
        self.state_store = {}
        self.user_count = 0

    def create_empty_profile(self, ):
        return UserProfile()
    
    def update_state_store(self, user_id: str, updated_profile:UserProfile):
        if user_id not in self.state_store:
            self.user_count += 1
        self.state_store[user_id]  = updated_profile

    def get_user_profile(self, user_id:str):
        try:
            return self.state_store.get(user_id)
        except KeyError:
            raise(f"User: {user_id} not in state store")

    def update_user_profile(self, user_id: str, transaction: Transaction):
        user_profile = self.get_user_profile(user_id)

        user_profile.total_amt += transaction.amount
        user_profile.txn_count +=1 
        user_profile.last_txn_timestamp = transaction.timestamp
        user_profile.last_txn_location = transaction.location 
        user_profile.average_amt = universal_float_format(user_profile.total_amt / user_profile.txn_count)

        self.update_state_store(user_id= user_id, updated_profile= user_profile)

    

    
