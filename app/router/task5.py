from typing import Optional
import os

from fastapi import FastAPI,APIRouter 
from bs4 import BeautifulSoup
import requests

  
def extract_soup(url: str):
    # getting the text from url
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"}
    # avoid 
    r =requests.get(url, verify=False)
    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    for element in soup(
            ["header", "footer", "nav", "script", "style", "button"]
        ):
            element.extract()
    return soup 

class Task5():
    def extract(url : str):
        soup = extract_soup(url)
        tag_map={} 
        for a_tag in soup.find_all('a'):
             if a_tag.has_attr('href'):
                if a_tag.parent is None:
                    continue
                else:
                    parent = a_tag.parent
                    count=0
                    for each in parent.find_all('a'):
                        count=count+1
                    if (count>2):
                        continue  
                    tag= a_tag.parent
                    code=''
                    name  = tag.name
                    code = code+name
                    a_dict = tag.attrs
                    for each in list(a_dict.keys()):
                        code= code + '+' + each  
                        for one in a_dict[each]:
                            code= code + ','+one 
                    if code not in list(tag_map.keys()):
                        tag_map[code]=1
                    else :
                        key_num = tag_map[code]+1
                        tag_map[code]=key_num 
        max = 0     
        my_list = list(tag_map.keys())
        max_tag='h3'
        for tags in my_list:
            if tags == my_list[0] or tags == my_list[-1]:
                continue
            if tag_map[tags]>max:
                max=tag_map[tags]
                max_tag = tags
        #print(tag_map)
        if ("uet" in url):
            key_tag= 'h3'
        else: 
            count=0
            for tags in my_list:
                if tag_map[tags]== max:
                    count= count+1
            if count==1:
                key_tag = max_tag
            else:
                maxspace=0
                for tags in my_list:
                    if tags == my_list[0] or tags ==my_list[-1]:
                        continue
                    if tag_map[tags]==max:
                        print(tags)
                        temp_list = tags.split("+")
                        if len(temp_list)>maxspace:
                            maxspace=len(temp_list)
                            key_tag = tags
        #print(key_tag)
        #print(tag_map) 
        sections = key_tag.split("+")
        tag_name = sections[0]
        attr_key=[]
        attr_value=[]
        for each in sections[1:]:
            temp = each.split(",")
            attr_key.append(temp[0])
            attr_value.append(temp[1])  
        if len(attr_key)==0:
            my_list= soup.find_all(tag_name)
            urls=[]
            for each in my_list:
                    if each.a is None:
                        continue
                    if each.a.has_attr('href'):
                        url = each.a['href']
                        if "https" not in url:
                            url = "https://"+url
                        if url not in urls:
                            urls.append(url)
            return urls
        else:
            my_list = soup.find_all(tag_name,attrs = {attr_key[0]:attr_value[0]})
            urls=[]
            for each in my_list:
                if each.a is None:
                    continue
                if each.a.has_attr('href'):
                    url = each.a['href']
                    if "https" not in url:
                            url = "https://"+url
                    if url not in urls:
                        urls.append(url)
            return urls           
        
#instance = Task5.extract("https://www.iefa.org/scholarships?page=2")           
#print(instance) 
#extract = ExtractURL.extract_info("https://www.hust.edu.vn/vi/su-kien-noi-bat/hop-tac-doi-ngoai-truyen-thong/thong-bao-hoc-bong-erasmus-key-action-1-truong-dh-porto-bo-dao-nha-654608.html")
#print(extract)


router = APIRouter()
@router.get("/task5(path_type)/{full_path:path}")
def task_5(full_path:str):
    result=[]
    result = result+ Task5.extract(full_path+"page/1")
    for i in range(1,11):
        result = result + Task5.extract(full_path+ f"page/{i}")
    return {"result":result}

@router.get("/task5(query_type)/{full_path:path}")
def task_5(full_path:str):
    result=[]
    result = result+ Task5.extract(full_path+"?page=1")
    for i in range(1,11):
        result = result + Task5.extract(full_path+ f"?page={i}")
    return {"result":result}


