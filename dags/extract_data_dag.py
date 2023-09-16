
import os
import pendulum
from airflow import DAG
from airflow.decorators import task

with DAG(
    dag_id="hearing_news",
    catchup=False,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule="@daily",
    tags=["crawl_data"],
) as dag:
    
    @task
    def load_questions():
        pass