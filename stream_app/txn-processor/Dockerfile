FROM python:3.8

WORKDIR /app

COPY aggregated_score_producer.py  ./
COPY average_analyzer.py  ./
COPY counter_analyzer.py  ./
COPY flink-sql-connector-kafka-3.3.0-1.20.jar  ./
COPY proximity_analyzer.py  ./
COPY requirements.txt  ./
COPY score_aggregator.py  ./


RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-it.sh ./
RUN chmod +x wait-for-it.sh

COPY start.sh ./
RUN chmod +x start.sh
CMD ["./start.sh"]
