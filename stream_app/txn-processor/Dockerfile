FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
    openjdk-11-jdk \
    python3.8 \
    python3.8-dev \
    python3-pip \
    build-essential

# First determine the architecture and set JAVA_HOME accordingly
RUN arch=$(dpkg --print-architecture) && \
    if [ "$arch" = "arm64" ]; then \
        echo "JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64" >> /etc/environment; \
    else \
        echo "JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> /etc/environment; \
    fi

# Use a shell to set the ENV variable
RUN . /etc/environment && \
    echo "export JAVA_HOME=$JAVA_HOME" > /etc/profile.d/java_home.sh

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64

WORKDIR /app

COPY *.py *.jar requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# COPY wait-for-it.sh start.sh ./
# RUN chmod +x wait-for-it.sh start.sh

# CMD ["./start.sh"]