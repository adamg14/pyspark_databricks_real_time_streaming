# Dockerfile
FROM apache/airflow:2.8.0

USER root
RUN apt-get update && \
    apt-get install -y --fix-missing openjdk-17-jdk && \
    apt-get clean


USER airflow
RUN pip install pyspark==3.5.1 delta-spark==3.2.0


ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"