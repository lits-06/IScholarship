
import os
import pendulum
from airflow import DAG
from airflow.decorators import task
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from airflow.operators.python_operator import PythonOperator

with DAG(
    dag_id="extract_data",
    catchup=False,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule="@daily",
    tags=["crawl_data"],
) as dag:
    
    path = "/opt/airflow/dags/questions/"
    uri = "mongodb+srv://admin:admin123@cluster0.ymqhm3k.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["db"]
    @task 
    def load_urls():
        print(uri)
        links = []
        rss_collection = db["scholarship_links"]
        for document in list(rss_collection.find({}, {"_id": 0})):
            links.append(document["link"])
        return links[:2]
        

    @task
    def load_questions():
        questions_list =[]
       
        #questions1: verifying whether the url contains scholarship info
        q = open(path + "questions-form.txt","r",encoding="utf8")
        questions =""
        for lines in q:
            questions = questions +lines
        q.close()
        questions_list.append(questions)
        q = open(path + "questions-form6.txt","r",encoding = "utf8")
        #general questions2
        questions2 =""
        for lines in q:
            questions2 = questions2 +lines
        q.close()
        questions_list.append(questions2)
        q = open(path + "questions-form7.txt","r",encoding="utf8")
        questions3 = ""
        for lines in q:
            questions3 = questions3 +lines
        q.close()
        questions_list.append(questions3)
        return questions_list
    
    questions = load_questions() 
    url = load_urls()


    @task 
    def extract_content(url: str):
        
        # getting the text from url
        import requests
        from bs4 import BeautifulSoup
        headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"}
        r =requests.get(url, verify=False)
        html = r.text
        soup = BeautifulSoup(html, "html.parser")
        for element in soup(
                ["header", "footer", "nav", "script", "style", "button"]
            ):
                element.extract()
        text = soup.text
        return {"content": text} 
 
    texts = extract_content.expand(url=url) 


    

    def check_is_scholarship(content: str, question: str):
        import openai
        with open("/opt/airflow/dags/questions/openai.txt") as f:
            key = f.readlines().replace("\n", "")
        openai.api_key = key
     
        completion = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            temperature = 0.5,
            max_tokens = 50,
            messages = [
            {"role": "system", "content": f"Bạn là một bot đang hỗ trợ các lập trình viên để trích xuất thông tin từ một trang web, đây là dữ liệu raw text được crawl về : {content} "},
            {"role": "user", "content": f"\n{question}"},  
        ]
        )
        response = completion.choices[0].message
        
        answers =[]
        answers= answers + response["content"].split("\n")
        if "không" not in answers[0].lower():
            return True
        return False

            
    check_is_scholarship = PythonOperator(
        task_id='check_is_scholarship',
        python_callable=check_is_scholarship,
        provide_context=True
    )

    def process_unextract_links():
        pass

    process_unextract_links = PythonOperator(
        task_id='process_unextract_links',
        python_callable=process_unextract_links,
        provide_context=True,
    )



    def extract_basic_info():
        import openai
        with open("/opt/airflow/dags/questions/openai.txt") as f:
            key = f.readlines().replace("\n", "")
        openai.api_key = key
        completion = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            temperature = 0.5,
            max_tokens = 2000,
            messages = [
            {"role": "system", "content": f"Bạn là một bot đang hỗ trợ các lập trình viên để trích xuất thông tin từ một trang web, đây là dữ liệu raw text được crawl về : {text} "},
            {"role": "user", "content": f"(Chỉ đưa ra thông tin được hỏi, không giải thích gì thêm, mỗi câu trả lời viết trên một dòng) : \n{mylist[1]}"},
        ]
        ) 
        response = completion.choices[0].message
        pass



    extract_basic_info = PythonOperator(
        task_id='extract_basic_info',
        python_callable=extract_basic_info,
        provide_context=True,
    )

    def extract_advanced_info():
        pass

    extract_advanced_info = PythonOperator(
        task_id='extract_advanced_info',
        python_callable=extract_advanced_info,
        provide_context=True,
    )
   

    texts >> check_is_scholarship
    check_is_scholarship >> extract_basic_info >> extract_advanced_info
    check_is_scholarship >> process_unextract_links

    
