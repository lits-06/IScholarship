import pandas as pd
import os
from rank_bm25 import BM25Okapi

def create_string_list(data):
    features = ["_id", "title", "organization", "benefits/value", "requirements", "majors"]
    data_frame = pd.DataFrame(data)
    selected_columns = data_frame[features]
    string_list = selected_columns.apply(lambda row: ' '.join(row), axis=1)

    result_list = string_list.tolist() 
    directory = os.path.dirname('app/middlewares/bm25/')
    if not os.path.exists(directory):
      os.makedirs(directory)
      print(f"Folder '{directory}' created successfully in '{directory}'")
    else:
        print(f"Folder '{directory}' already exists in '{directory}'")
    file_path = os.path.join(directory, 'scholarship.txt')
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in result_list:
            file.write(item + '\n')
    return result_list

def get_top_k_item_bm25(users, file_path, k):
  user_corpus = ""
  for user in users:
    user_corpus += user['title'] + ' ' + user['role'] + ' ' + user['description']
  tokenized_query = user_corpus.split(" ")
  
  read_list = []
  with open(file_path, 'r', encoding='utf-8') as file:
      for line in file.readlines():
          read_list.append(line.strip())
  id_list = [doc.split(" ")[0] for doc in read_list]
  tokenized_corpus = [doc.split(" ") for doc in read_list]
  bm25 = BM25Okapi(tokenized_corpus)
  doc_scores = bm25.get_scores(tokenized_query)
  combined_list = zip(id_list, doc_scores)
  result_dict = dict(combined_list)
  sorted_items = sorted(result_dict.items(), key=lambda x: x[1], reverse=True)
  top_k_values = [item[0] for item in sorted_items[:k]]
  return top_k_values