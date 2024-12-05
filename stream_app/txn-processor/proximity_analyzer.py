from pyflink.datastream import StreamExecutionEnvironment, CheckpointingMode
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.connectors.kafka import (
    KafkaSource, 
    KafkaOffsetsInitializer,
    KafkaSink,
    KafkaRecordSerializationSchema
)
from pyflink.datastream.functions import MapFunction, KeyedProcessFunction
from pyflink.common.typeinfo import Types
from pyflink.common import WatermarkStrategy
import json, os 
import logging
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.datastream.connectors import FileSink
from pyflink.common.serialization import Encoder
from pyflink.common import Types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionParser(MapFunction):
    def map(self, value):
        return json.loads(value)

class TransactionState:
    def __init__(self, last_location: str ='', last_transaction_time: int = 0):
        self.last_transaction_time = last_transaction_time
        self.last_location = last_location

class ProximityAnalyzer(KeyedProcessFunction):
    def open(self, runtime_context):
        state_desc = ValueStateDescriptor('proximty-state', Types.PICKLED_BYTE_ARRAY())
        self.state = runtime_context.get_state(state_desc)

    def process_element(self, transaction: dict, ctx: KeyedProcessFunction.Context):
        if transaction is None:
            return
        

        current_loc = transaction['location']
        current_time = transaction['txn_time']
        
        state_value = self.state.value()
        if state_value is None:
            new_state = TransactionState(current_loc, current_time)
            self.state.update(new_state)
            transaction['fraud_score'] = 0
        else:
            if current_loc != state_value.last_location:
                transaction['fraud_score'] = 1
            else:
                transaction['fraud_score'] = 0
                new_state = TransactionState(
                    current_loc,
                    current_time
                )
                self.state.update(new_state)
        
        yield json.dumps(transaction) 

def create_kafka_source() -> KafkaSource:
    props = {
        'group.id': 'proximity-analyzer-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': 'true',
        'max.poll.records': '100',
        'session.timeout.ms': '30000',
        'request.timeout.ms': '40000',
        'max.poll.interval.ms': '300000'
    }
    
    return KafkaSource.builder() \
        .set_bootstrap_servers('localhost:9092') \
        .set_topics('transaction') \
        .set_group_id('proximity-analyzer-group') \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_properties(props) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()

def create_kafka_sink() -> KafkaSink:
    # Create serialization schema for the sink
    serialization_schema = KafkaRecordSerializationSchema.builder() \
        .set_topic("transaction-scored") \
        .set_value_serialization_schema(SimpleStringSchema()) \
        .build()
    
    # Create and configure the Kafka sink
    return KafkaSink.builder() \
        .set_bootstrap_servers('localhost:9092') \
        .set_record_serializer(serialization_schema) \
        .build()


def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    
    # Configure environment
    env.enable_checkpointing(5000)
    env.get_checkpoint_config().set_checkpointing_mode(CheckpointingMode.EXACTLY_ONCE)
    env.get_checkpoint_config().set_min_pause_between_checkpoints(1000)
    env.set_parallelism(1)
    
    # Add Kafka connector
    current_dir = os.getcwd()
    kafka_jar = os.path.join(current_dir, "flink-sql-connector-kafka-3.3.0-1.20.jar")
    if not os.path.exists(kafka_jar):
        logger.error(f"Kafka connector jar not found at: {kafka_jar}")
        return
    env.add_jars(f"file://{kafka_jar}")

    kafka_source = create_kafka_source()
    kafka_sink = create_kafka_sink()


    try:
        # Process the stream
        ds = (
            env.from_source(
                source=kafka_source,
                watermark_strategy=WatermarkStrategy.no_watermarks(),
                source_name="Kafka Source"
            )
            .map(TransactionParser())
            .key_by(lambda x: x['user_id'])
            .process(ProximityAnalyzer())
            .map(lambda x: x , output_type=Types.STRING())
        )


        ds.sink_to(kafka_sink)

        
        ds.print()  
        
        env.execute("Transaction Average Analyzer")
    except Exception as e:
        logger.error(f"Error executing Flink job: {e}")

if __name__ == '__main__':
    main()