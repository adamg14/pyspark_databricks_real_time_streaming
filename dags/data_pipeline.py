from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipeline.bronze_orders import bronze_ingestion
from pipeline.silver_orders import silver_orders
from ingestion.local_producer_host import purchase_event

default_args = {
    "owner": "Adam Worede",
    "depends_on_past": False,
    "start_date": datetime(2025, 9, 7),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

# pipeline skeleton for testing purposes
with DAG("data_pipeline",
         default_args=default_args,
         description="Architecture Pipeline",
         schedule_interval="@daily",
         catchup=False,
         tags=["kafka", "spark", "delta"]
         ) as dag:
    
    pipeline_start = DummyOperator(
        task_id="pipeline_start",
        dag=dag
    )
    

    bronze_orders = PythonOperator(
        task_id = "bronze_orders",
        python_callable=bronze_ingestion,
        dag=dag
    )

    pipeline_end = DummyOperator(
        task_id="pipeline_end",
        dag=dag
    )

    pipeline_start >> bronze_ingestion
    bronze_ingestion >> pipeline_end