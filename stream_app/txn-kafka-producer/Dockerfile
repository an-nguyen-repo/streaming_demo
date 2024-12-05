FROM python:3.8

WORKDIR /app

COPY requirements.txt pyproject.toml ./
COPY transaction_producer.py ./
RUN pip install --no-cache-dir -r requirements.txt

RUN pip uninstall kafka --yes
RUN pip install kafka 
RUN pip install kafka-python 

COPY src/ ./src/
COPY tests/ ./tests/

RUN pip install -e .

COPY wait-for-it.sh ./
RUN chmod +x wait-for-it.sh


CMD ./wait-for-it.sh -s -t 30 $ZOOKEEPER_SERVER -- ./wait-for-it.sh -s -t 30 $KAFKA_SERVER -- python -m transaction_producer.py
