
import os
import pendulum
from airflow import DAG
from airflow.decorators import task
import requests
import feedparser
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

with DAG(
    dag_id="hearing_news",
    catchup=False,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule="@daily",
    tags=["crawl_data"],
) as dag:
    
    uri = "mongodb+srv://admin:admin123@cluster0.ymqhm3k.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["db"]
   
    @task
    def get_source_urls():
        """
        input: None
        Get rss feed urls from mongodb
        Output: return all urls 
        """
        print(uri)
        links = []
        rss_collection = db["scholarship_links"]
        for document in list(rss_collection.find({}, {"status": "New"})):
            links.append({"title":document["title"], "link":document["link"]})
        return links

    @task 
    def check_new_posts(url: str):
        """
            input: a url 
            output: all new schoolarship today url
        """
        response = requests.get(url, verify=False)
        feed = feedparser.parse(response.text)
        collection = db["scholarship_links"]
        if feed.bozo == 1:
            print("some error")
        for entry in feed.entries:
            if not collection.find_one({"title": entry.title}) and not collection.find_one({"link": entry.link}) and "học bổng" in entry.title.lower():
                new_post = {
                    "title": entry.title,
                    "link": entry.link,
                    "published": datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z"),
                    "status": "New"
                }
                collection.insert_one(new_post)


    url = get_source_urls()
    check_new_posts.expand(url=url)


    