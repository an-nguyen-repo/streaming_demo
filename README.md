
# HOW TO RUN 
0. Start Docker desktop 
1. cd to current directory 
```
cd FraudDetectionStreaming
```

2. Build docker image 
Build docker image for kafka transaction producer. This producer will generate fake transaction with configurable transaction rate per second, fraud transaction rate per 1000 transaction and input into kafka topic `transaction`

```
cd stream-app/txn-kafka-producer
docker build -t txn-kafka-producer . 
cd ..
```

Build docker iamge for transaction producer. This create flink env for:
- AverageAnalyzer: read from kafka topic `transaction` compare current transaction with user all time average spending. Mark fraud_score=1 if average >=3 time global average. Input into kafka topic `transaction-scored`
- CounterAnalyazr: read from kafka topic `transaction` compare curernt transactime time with previous transaction. Mark fraud_score= 1 if current transaction is too close with previous transaction. Input into kafka topic `transaction-scored`
- ProximityAnalyzer: read from kafka topic `transaction` compare current location with previos transaciton location. Mark fraud_score =1 if current location is diff from previous transaction. Input into kafka topic `transaction-scored`
- ScoreAggrigator: read from kafka topic `transaction-scored`. Key by transaction window by session. Sum up fraud_score. Mark transaction type = form if fraud_score >=2. Input into kafka topic `transaction-final`
- AggregatedScoreProducer: read from kafka topic `transaction-final`. Create table fraud_events in postgres. Batch insert into postgress every 100 transaction received 
```
cd  stream-app/txn-processor
docker build -t txn-processor .
cd ..
```

3. Run all service 
This will start 
- An instance of txn-kafka-producer to produce input transaction
- 5 instance of txn-processor for each of above flink processor 
- An instance of postgres
- An instance of kafka + zookeeper
- An instance of grafana

```
docker-compose up -d 
```

# ANALYSYS 

## CHECKING TRANSACTION PRODUCER 
Checking producer terminal logs 
```
docker logs frauddetectionstreaming-txn-kafka-producer-1
```


Checking kafka `transaction` topic 
```
docker exec -it frauddetectionstreaming-kafka-1 kafka-console-consumer --bootstrap-server kafka:9092 --topic transaction --from-beginning
```

## CHECKING ANALYZER PROCESSOR 
Checking producer terminal logs 
``` 
docker logs frauddetectionstreaming-txn-anverage-analyzer-1
```

Checking kafka `transaction-scored` topic 
```
docker exec -it frauddetectionstreaming-kafka-1 kafka-console-consumer --bootstrap-server kafka:9092 --topic transaction-scored --from-beginning
```

Checking kafka `transaction-final` topic 
```
docker exec -it frauddetectionstreaming-kafka-1 kafka-console-consumer --bootstrap-server kafka:9092 --topic transaction-final --from-beginning
```

## CHECKING POSTGRES
```
docker exec -it postgres psql -U myuser -d frauddb
```

Check table data 
```
select count(*) from fraud_events;
```

## CHECKING GRAFANA 

At localhost:3001 web UI