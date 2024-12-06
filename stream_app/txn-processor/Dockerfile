FROM apache/flink:1.20-java11

# install python3 and pip3
RUN apt-get update -y && \
apt-get install -y python3 python3-pip python3-dev && rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/python3 /usr/bin/python

# install PyFlink
RUN pip3 install --no-cache-dir apache-flink
RUN pip3 install kafka-python
RUN pip3 install psycopg2-binary

# Copy application files
COPY *.py *.jar requirements.txt ./

# Copy and prepare scripts
COPY wait-for-it.sh start.sh ./
RUN chmod +x wait-for-it.sh start.sh

#CMD ["./start.sh"]