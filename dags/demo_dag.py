
import pendulum
from airflow import DAG
from airflow.decorators import task

with DAG(
    dag_id="demo",
    catchup=False,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule="@daily",
    tags=["demo"],
) as dag1:
    @task
    def task_one():
        return ['Hello']
    
    @task
    def task_two(input: list):
        if len(input) == 0:
            return None
        return input[0] + "world"

    input = task_one()
    task_two(input)