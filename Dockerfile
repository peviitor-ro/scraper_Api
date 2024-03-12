FROM python:3.9
FROM node:14
FROM openjdk:8-jdk-alpine

RUN apk --no-cache add git
RUN wget https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-5.4.1.tgz && \
    tar -xzf apache-jmeter-5.4.1.tgz -C /opt && \
    rm apache-jmeter-5.4.1.tgz

ENV PATH="/opt/apache-jmeter-5.4.1/bin:${PATH}"


