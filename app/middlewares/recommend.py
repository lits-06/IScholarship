from recbole.data import create_dataset, data_preparation
from recbole.utils.case_study import full_sort_topk
import pandas as pd
from recbole.data import create_dataset, data_preparation
from recbole.trainer import Trainer
from sklearn.feature_extraction.text import TfidfVectorizer
from recbole.config import Config
from recbole.model.general_recommender import BPR, RaCT, Pop, FISM, NAIS, LINE
from recbole.model.context_aware_recommender import FNN, LR, FM, NFM, DeepFM, PNN
import os

import pandas as pd
import numpy as np
import nltk
from nltk import word_tokenize, pos_tag
from nltk.stem import  WordNetLemmatizer
from nltk.corpus import stopwords
from recbole.data.interaction import Interaction
import torch

model_dict = {
  "BPR": BPR,
  "RaCT": RaCT,
  "FNN": FNN,
  "Pop": Pop,
  "FISM": FISM,
  "NAIS": NAIS,
  "LINE": LINE,
  "LR": LR,
  "FM": FM, 
  "NFM": NFM, 
  "DeepFM": DeepFM, 
  "PNN": PNN
}

config_dict_context_aware = {
    'load_col': {
        'inter': ['user_id', 'item_id', 'label', 'status'],
        "user": ['user_id', 'email'],
        "item": ['item_id', 'deadline', 'type', 'education_level', 'word_vec']
    },
    'embedding_size': 10,

    'epochs': 5,
    'train_batch_size': 4096,
    'eval_batch_size': 4096,
    'eval_args':{
        'split': {'RS':[0.8,0.1,0.1]},
        'order': 'RO',
        'group_by': None,
        'mode': 'labeled'
    },
    'train_neg_sample_args': None,
    'metrics': ['AUC', 'LogLoss'],
    'valid_metric': 'AUC'
}

config_dict_general = {
    'load_col': {
        'inter': ['user_id', 'item_id', 'label', 'status'],
    },
    'save_dataset': True,
    'save_dataloaders': True,
    'embedding_size': 64,
    'epochs': 5,
    'train_batch_size': 4096,
    'eval_batch_size': 4096,
    'train_neg_sample_args': {
        'distribution': 'uniform',
        'sample_num': 1,
        'alpha': 1.0,
        'dynamic': False,
        'candidate_num': 0
    },
    'eval_args': {
        'group_by': 'user',
        'order': 'RO',
        'split': {'RS': [0.8,0.1,0.1]},
        'mode': 'full'
    },
    'metrics': ['Recall', 'MRR', 'NDCG', 'Hit', 'Precision'],
    'topk': 10,
    'valid_metric': 'MRR@10',
    'metric_decimal_place': 4
}

def pretreatment(comment):
    '''
    remove punctuations, numbers and urls
    lower case conversion
    remove stop words
    lemmatization
    '''
    punctuation=list('。，？！：%&~（）、；“”&|,.?!:%&~();""#@【】/-\'$+*`[]{}()')
    stop_words = stopwords.words("english")
    stop_words.extend(["n't","wo","'m","'s","'ve", "'d", "'ll", "``", "''", "--", "..."])
    stop_words.extend(punctuation)
    wordnet_lematizer = WordNetLemmatizer()
    token_words = word_tokenize(comment)
    token_words = [w.lower() for w in token_words]
    token_words = [w for w in token_words if w not in stop_words]
    token_words =  pos_tag(token_words) 
    cleaned_word = []
    for word, tag in token_words:
        if word.isdigit():
            continue
        if tag.startswith('NN'):
            word_lematizer =  wordnet_lematizer.lemmatize(word, pos='n')  # n for noun
        elif tag.startswith('VB'): 
            word_lematizer =  wordnet_lematizer.lemmatize(word, pos='v')   # v for verb
        elif tag.startswith('JJ'): 
            word_lematizer =  wordnet_lematizer.lemmatize(word, pos='a')   # a for adjective
        elif tag.startswith('R'): 
            word_lematizer =  wordnet_lematizer.lemmatize(word, pos='r')   # r for pronoun
        else: 
            word_lematizer =  wordnet_lematizer.lemmatize(word)
        cleaned_word.append(word_lematizer)
    
    return cleaned_word

def text_to_vector(features, data):
  data["word_sum"] = data[features].apply(lambda row: ' '.join(row), axis=1)
  segment=[]
  for content in data["word_sum"].values:
      segment.append(' '.join(pretreatment(content)))
  data["text"] = segment
  data_tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0.0, max_features=50, stop_words='english')
  data_matrix = data_tf.fit_transform(data["text"])
  data['word_vec'] = data.apply(lambda row: data_matrix[row.name].toarray(), axis=1)
  df = data.drop(["text", "word_sum"] + features, axis=1)
  return df

def turn_json_to_df(inter_json, user_json, item_json):
  inter = pd.DataFrame(inter_json)
  user = pd.DataFrame(user_json)
  item = pd.DataFrame(item_json)
  item_final = text_to_vector(["title", "organization", "benefits/value", "requirements", "majors"], item)
  return inter, user, item_final

def cast_to_atomic_file(inter, user, item):
  inter['label'] = inter['label'].astype(float)
  inter_temp = inter[['user_id', 'scholarship_id', 'label', 'status']].rename(
    columns={'user_id': 'user_id:token', 'scholarship_id': 'item_id:token', 'label': 'label:float', 'status': 'status:float'})

  user_temp = user[['_id', 'email']].rename(
    columns={'_id': 'user_id:token', 'email': 'email:token_seq'})

  item_temp = item[['_id', 'deadline', 'type', 'education_level', 'word_vec']].rename(
    columns={'_id': 'item_id:token', 'deadline': 'deadline:token_seq', 'type': 'type:float', 'education_level': 'education_level:token_seq', 'word_vec': 'word_vec:float_seq'})

  directory = os.path.dirname(os.path.abspath(__file__))
  folder_name = 'pjf'
  folder_path = os.path.join(directory, folder_name)
  if not os.path.exists(folder_path):
      os.makedirs(folder_path)
      print(f"Folder '{folder_name}' created successfully in '{directory}'")
  else:
      print(f"Folder '{folder_name}' already exists in '{directory}'")
  inter_path = os.path.join(directory, folder_name, 'pjf.inter')
  user_path = os.path.join(directory, folder_name, 'pjf.user')
  item_path = os.path.join(directory, folder_name, 'pjf.item')
  inter_temp.to_csv(inter_path, index=False, sep='\t')
  user_temp.to_csv(user_path, index=False, sep='\t')
  item_temp.to_csv(item_path, index=False, sep='\t')

def load_dataset(config):
  dataset = create_dataset(config)
  ref = dataset
  train_data, valid_data, test_data = data_preparation(config, dataset)
  return ref, train_data, valid_data, test_data

def train_model(scholarshipuser, user, scholarship, type, model_name):
  inter, user, item = turn_json_to_df(scholarshipuser, user, scholarship)
  cast_to_atomic_file(inter, user, item)
  file_dir = os.path.dirname(os.path.abspath('app/middlewares/pjf'))
  if type == "general":
      config_dict_general['data_path'] = file_dir
      config = Config(model=model_name, dataset='pjf', config_dict=config_dict_general)
      data_set, train_data, valid_data, test_data = load_dataset(config)
      model = model_dict[model_name](config, train_data.dataset)
      trainer = Trainer(config, model)
      trainer.fit(train_data, valid_data)
  else:
      config_dict_context_aware['data_path'] = file_dir
      config = Config(model=model_name, dataset='pjf', config_dict=config_dict_context_aware)
      data_set, train_data, valid_data, test_data = load_dataset(config)
      model = model_dict[model_name](config, train_data.dataset)
      trainer = Trainer(config, model)
      trainer.fit(train_data, valid_data)

def get_top_k_item(uid_series, data_set, model, test_data, config, k):
  uids = data_set.token2id(data_set.uid_field, uid_series)
  topk_score, topk_iid_list = full_sort_topk(uids, model, test_data, k, device=config['device'])
  return topk_score, topk_iid_list

def get_top_k_item_context(uid_series, data_set, model, config, user_index, index_item, k):
  uid_series = np.vectorize(user_index.get)(uid_series)
  uid_list = torch.tensor(uid_series)
  input_inter = Interaction({'user_id': torch.tensor(uid_list)})
  input_inter = data_set.join(input_inter)
  with torch.no_grad():
    try:  # if model have full sort predict
        input_inter = input_inter.to(config['device'])
        scores = model.full_sort_predict(input_inter)
    except NotImplementedError:  # if model do not have full sort predict
        len_input_inter = len(input_inter)
        input_inter = input_inter.repeat(data_set.item_num)
        input_inter.update(data_set.get_item_feature().repeat(len_input_inter))  # join item feature
        input_inter = input_inter.to(config['device'])
        scores = model.predict(input_inter)
    scores = scores.view(-1, data_set.item_num)
    topk_score, topk_iid_list = torch.topk(scores, k)
    top_id = np.vectorize(index_item.get)(topk_iid_list)
  return topk_score, top_id