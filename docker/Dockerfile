FROM bitnami/spark:latest

USER root
RUN apt-get update && apt-get install -y bash coreutils

WORKDIR /app

COPY spark/ /app/spark

