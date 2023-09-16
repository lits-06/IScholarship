
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
    
    rss_links_file = "rss_links.txt"
    @task
    def get_source_urls():
        """
        input: None
        Get rss feed urls from mongodb
        Output: return all urls 
        """

    @task 
    def check_new_posts(url: str):
        """
            input: a url 
            output: all new schoolarship today url
        """

    url = get_source_urls()
    check_new_posts.expand(url=url)


    