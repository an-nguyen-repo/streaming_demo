from typing import Tuple, Iterable
from pyflink.common import Types
from pyflink.datastream import StreamExecutionEnvironment, CheckpointingMode
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.connectors.kafka import (
    KafkaSource, 
    KafkaOffsetsInitializer,
    KafkaSink,
    KafkaRecordSerializationSchema
)
from pyflink.datastream.functions import MapFunction, WindowFunction
from pyflink.common.typeinfo import Types
from pyflink.common import WatermarkStrategy
import json, os 
import logging
from pyflink.common import Types
from typing import Iterable
from pyflink.datastream.window import TumblingProcessingTimeWindows, Time
from pyflink.datastream.functions import ProcessWindowFunction


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionParser(MapFunction):
    def map(self, value):
        return json.loads(value)


class FraudWindowAggregator(ProcessWindowFunction):

    def process(self, key: str, context: ProcessWindowFunction.Context,
                elements) -> Iterable[str]:
        
        base_txn = elements[-1].copy()
        for txn in elements[:-1]:
            base_txn['fraud_score'] += txn['fraud_score']

        if base_txn['fraud_score'] >=2:
            base_txn['transaction_type'] ='Fraud'
            yield json.dumps(base_txn)

        yield None 




def create_kafka_source() -> KafkaSource:
    props = {
        'group.id': 'scorer-analyzer-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': 'true',
        'max.poll.records': '100',
        'session.timeout.ms': '30000',
        'request.timeout.ms': '40000',
        'max.poll.interval.ms': '300000'
    }
    
    return KafkaSource.builder() \
        .set_bootstrap_servers('localhost:9092') \
        .set_topics('transaction-scored') \
        .set_group_id('scorer-analyzer-group') \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_properties(props) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()

def create_kafka_sink() -> KafkaSink:
    # Create serialization schema for the sink
    serialization_schema = KafkaRecordSerializationSchema.builder() \
        .set_topic("transaction-fraud") \
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
            .key_by(lambda x: x['transaction_id'])
            .window(TumblingProcessingTimeWindows.of(Time.seconds(5)))
            .process(FraudWindowAggregator(), output_type = Types.STRING())
            .filter(lambda x: x  is not None )
        )


        ds.sink_to(kafka_sink)

        
        env.execute("Transaction Average Analyzer")
    except Exception as e:
        logger.error(f"Error executing Flink job: {e}")

if __name__ == '__main__':
    main()