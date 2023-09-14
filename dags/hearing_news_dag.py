
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
    def check_new_posts():
        from pymongo.mongo_client import MongoClient
        from pymongo.server_api import ServerApi
        import requests
        import feedparser
        from datetime import datetime
        
        client = MongoClient(os.getenv("MONGO_URL"), server_api=ServerApi('1'))
        db = client["db"]
        collection = db["rss_links"]

        # with open(rss_links_file, "r") as file:
        #     for link in file:
        #         response = requests.get(link, verify=False)
        #         feed = feedparser.parse(response.text)
        #         if feed.bozo == 1:
        #             print("some error")
        #         for entry in feed.entries:
        #             if not collection.find_one({"title": entry.title}) and "học bổng" in entry.title.lower():
        #                 new_post = {
        #                     "title": entry.title,
        #                     "link": entry.link,
        #                     "published": datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z"),
        #                 }
        #                 collection.insert_one(new_post)

    check_new_posts()