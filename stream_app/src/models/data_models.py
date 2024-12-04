
from pydantic import BaseModel, Field 
from datetime import datetime 
from enum import Enum
from typing import NamedTuple, Union
import uuid
from faker import Faker
import src.utils.utils  as ut 

fake = Faker()
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
    transaction_id: str = f'txn-{uuid.uuid4()}'
    user_id: str 
    amount: float = Field(default= 0 ,ge =0)
    timestamp: datetime = datetime.now()
    location: Location = Location()
    transaction_type: TransactionType = TransactionType.NORMAL


class UserProfile(BaseModel):
    user_id: str = f'user-{uuid.uuid4()}'
    created_date: datetime = datetime.now()
    main_location: Location = Location(country = fake.country())
    #transaction base 
    average_amt: float = 0
    total_amt: float = 0.0
    txn_count: int = 0.0
    last_txn_timestamp: datetime = datetime(1970,1,1)
    last_txn_location: Location = Location()


    def has_no_transact_history(self):
        return self.txn_count ==0 
    
    
    



