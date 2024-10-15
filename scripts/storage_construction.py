import json
import os
import time
import warnings
import argparse
from sys import exit
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from utils import VectorStore, load_logger
logger = load_logger(__file__)

root = Path(__file__).parent.parent.absolute()
with open(os.path.join(Path(__file__).parent.absolute(), 'config.json')) as f:
    config = json.load(f)
    
warnings.filterwarnings("ignore")
os.environ['TZ'] = config['timezone']
time.tzset()

with open(os.path.join(Path(__file__).stem, 'config.json')) as f:
    config = json.load(f)
data_root = os.path.join(Path(__file__).parent.parent.absolute(), 'data')
embed_dimension = 768

with open(os.path.join(data_root, 'preprocessing', config['dataset_split_file_name']), 'r') as f:
    split = json.load(f)

# mode = config['mode']
mode = 'val'
assert mode in ['train', 'val', 'test'], '`mode` should be `train`, `val` or `test`'
with open(os.path.join(data_root, 'preprocessing', 'text_image_list-2024_09_23.json'), 'r') as f:
    text_image_list = json.load(f)
images_raw = pd.read_csv(os.path.join(data_root, 'preprocessing', 'image_summary-wo_q-w_soft_titles-gpt_4o.csv'))
texts_raw = pd.read_json(os.path.join(data_root, 'MultiModalQA', 'MMQA_texts.jsonl'), lines=True)
selected_texts = texts_raw[texts_raw['id'].isin(text_image_list[f'{mode}_text_ids'])]
selected_images = images_raw[images_raw['path'].isin(text_image_list[f'{mode}_image_file_list'])]
    
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, default='train', choices=['train', 'val', 'test'], dest='mode')
    if mode == 'train':
        model_name = config['vanilla_bge_model']
    if mode in ['val',  'test'] and 'ft_bge_model' in config:
        model_name = config['ft_bge_model']
    else:
        logger.info('- No finetuning BGE model found, exit.')
        exit(1)
        
    device = config['device']
    embed_model_path = os.path.join(Path(__file__).parent.parent.absolute(), 'models', config['ft_bge_model'])
    logger.info(f'- mode: {mode}\n- embedding model path: {embed_model_path}')
    vector_store = VectorStore(model_name_path=embed_model_path, device=device)
    logger.info('- embedding model loaded.')
    logger.info('- data and embedding model reday for ingestion.')
    
    logger.info(f'- start ingstion: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
        
    for _, row in tqdm(selected_texts.iterrows(), desc='ingest text'):
        row = row.to_dict()
        row['type'] = 'text'
        vector_store.add_data(row)
        
    for _, row in tqdm(selected_images.iterrows(), desc='ingest image'):
        row = row.to_dict()
        row['type'] = 'image'
        vector_store.add_data(row)
        
    logger.info('- text node:', vector_store.vector_store[0]['metadata'], '\n')
    logger.info('- image node:', vector_store.vector_store[-1]['metadata'])
    
    vector_store_file_name = config[f'{mode}_vector_store_file_name'] = f'storage-{mode}-ft_bge-{time.strftime("%Y_%m_%d", time.localtime())}.pkl'
    vector_store_path = os.path.join(Path(__file__).parent.parent.absolute(), 'storage', vector_store_file_name)
    vector_store.save_vector_store(vector_store_path)
    logger.info(f'- save vector store to {vector_store_path}')
    
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json'), 'w') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)