FROM ubuntu:bionic

RUN apt-get update -y && \
    apt-get install -y python3-pip python-dev
RUN mkdir /app
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt

