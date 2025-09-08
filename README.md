# Pyspark Realtime e-Commerce Purchase Data Pipeline

This project takes simulated realtime purchase order data using an Apache Kafka message broker, and processes the data using a Medallion architecture.

## Technologies Used
- *Terraform* = Terraform is used to automate the build and testing of databricks infrastructure, fitting with CI/CD principals (a temporarly abandoned feature)
- *Confluent Cloud* = Confluent cloud is used to be able to have a managed Apache Kafka bootstrap server (abandoned due to dev costs)
- *Docker* = Container which contains images of a local kafka broker and a corresponding, in order to run Apache Kafka locally.
- *Pyspark* = Pyspark is used to build the distributed processing data pipeline. Subscribing to the Kafka topic, where purchase events are produced; Continously ingesting the messages via subscription and delta tables; data cleaning through medallion filtering
- *Python* = Scripting to: simulated purchase events; run the Pyspark pipeline, Created an Apache Kafka producer

## Next steps 
- Additional Medallion layers
- Full Dockerisation 
- CI/CD - Automated testing and deployment
- Airflow - Orchastration
- AI/ML
- Databricks


## Commands
Running the containerised version of the pipeline, for development and local testing:
```bash
docker-compose run -d postgres
docker-compose run -d redis
docker-compose up -build
```
