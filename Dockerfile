FROM ubuntu:bionic

RUN apt-get update -y && \
    apt-get install -y python3-pip python-dev
RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY src ./src/
COPY config.yaml .
