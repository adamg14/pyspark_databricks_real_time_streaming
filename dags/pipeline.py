from airflow import DAG
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta

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
    pipeline_start = DummyOperator(task_id="pipeline_start")
    pipeline_end = DummyOperator(task_id="pipeline_end")

    pipeline_start >> pipeline_end