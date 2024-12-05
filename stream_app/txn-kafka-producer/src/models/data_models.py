
from pydantic import BaseModel, Field 
from datetime import datetime 
from enum import Enum
from typing import NamedTuple, Union
from faker import Faker
import src.utils.utils  as ut 
import time 
import random 
import string 


fake = Faker()


def generate_id():
   timestamp = str(int(time.time() * 1000))
   random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
   return f"{timestamp}{random_chars}"


class Location(BaseModel):
    country: str = ''

    def is_empty(self):
        return self.country ==''
    
    def __eq__(self, other):
        if not isinstance(other, Location):
            return NotImplemented
        
        return self.country.lower() == other.country.lower()
 
class TransactionType(Enum):
    NORMAL = 'Normal'
    FRAUD = 'Fraud'


class FraudType(Enum):
    HIGH_VALUE_FRAUD = 'High Value Fraud'
    PROXIMITY_FRAUD = 'Proximity Fraud'
    TIME_FRAUD = "Time Fraud"

class ValueRange(NamedTuple):
    low: Union[int, float]
    high: Union[int, float] 


class TransactionConstants:
    AMOUNT_RANGE = ValueRange(low = 1.0, high = 100000.0)
    AMOUNT_FACTOR_RANGE = ValueRange(low = 0.8, high = 1.2)
    LOCATION_TIME_WINDOW = ValueRange(low = 1, high = 10 *60) # seconds 
    CLOSE_TIME_WINDOW = ValueRange(low = 1, high= 1000 *20) # milliseconds
    FRAUD_FACTOR_RANGE = ValueRange(low = 3.0, high = 10.0)
    NORMAL_TXN_TIME_RANGE = ValueRange(low = 30.0, high = None ) 
    

class Transaction(BaseModel):
    transaction_id: str = ''
    user_id: str 
    amount: float = Field(default= 0 ,ge =0)
    timestamp: datetime = datetime.now()
    location: Location = Location()
    transaction_type: TransactionType = TransactionType.NORMAL

    def model_post_init(self, __context__):
        self.transaction_id = f"txn-{generate_id()}" 

class UserProfile(BaseModel):
    user_id: str = ''
    created_date: datetime = datetime.now()
    main_location: Location = ''
    #transaction base 
    average_amt: float = 0
    total_amt: float = 0.0
    txn_count: int = 0.0
    last_txn_timestamp: datetime = datetime(1970,1,1)
    last_txn_location: Location = Location()

    def model_post_init(self, __context__):
        self.user_id = f"user-{generate_id()}" 
        faker = Faker()
        self.main_location = Location(country = faker.country())

    def has_no_transact_history(self):
        return self.txn_count ==0 
    
    
    



