
# cd to current directory 

docker-compose up -d 

# python env 
cd stream_app
python3.8 -m venv .stream-app
source .stream-app/bin/activate
pip install -r requirements.txt 
pip install -e .
python -m pip install apache-flink

# in a separte terminal: cd to stream_app
python3 transaction_producer.py

# in a separte terminal: cd to stream_app
python3 anverage_analyzer.py
# in a separte terminal: cd to stream_app
python3 counter_analyzer.py
# in a separte terminal: cd to stream_app
python3 proximity_analyzer.py
# in a separte terminal: cd to stream_app
python3 score_aggregator.py


# in seperate terminal - check kafka 

docker exec -it broker kafka-console-consumer  \
    --bootstrap-server localhost:9092 \
    --topic transaction

OR 

docker exec -it broker kafka-console-consumer  \
    --bootstrap-server localhost:9092 \
    --topic transaction-scored

docker exec -it broker kafka-console-consumer  \
    --bootstrap-server localhost:9092 \
    --topic transaction-fraud  