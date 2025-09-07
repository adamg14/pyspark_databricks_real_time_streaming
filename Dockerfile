# docker image
FROM bitnami/spark:3.5.1

# set the working directoru
WORKDIR /app

# installing the system dependencies
USER root
RUN apt-get update && apt-get install -y \
curl \
&& rm -rf /var/lib/apt/lists/*

# installing the package dependencies for python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# # installing kafka dependencies for Spark
# RUN ${SPARK_HOME}/bin/spark-shell --packages \
#     "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,io.delta:delta-spark_2.12:3.2.0" \
#     --repositories https://repo1.maven.org/maven2/ \
#     --conf spark.jars.ivy=/tmp/.ivy
    
# copy the files/folders required for the project
COPY ingestion/ ./ingestion/
COPY pipeline ./pipeline/
COPY entrypoint.sh .

# create data directory for Spark delta tables
RUN mkdir -p /app/data/delta

# environment variables
ENV PYSPARK_PYTHON=python3
ENV PYTHONPATH=/app
ENV SPARK_HOME=/opt/spark

# make the entrypoint file executable
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]