# Dockerfile
FROM apache/airflow:2.8.0

# Install Java as root
USER root
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk && \
    apt-get clean

# Switch to airflow user and install Python packages
USER airflow
RUN pip install pyspark==3.5.1 delta-spark==3.2.0

# Set Java environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"