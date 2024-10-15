import pickle
import torch
import random
import logging
import os
import time
from pathlib import Path

from sentence_transformers import SentenceTransformer
from torch.nn.functional import cosine_similarity

class VectorStore:
    def __init__(self, model_name_path, vector_store_path=None, device='cuda'):
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        if device == 'cuda' and torch.cuda.is_available():
            self.device = 'cuda'
        else:
            self.device = 'cpu'
        print(f'-> using {self.device} to construct vector store')
        
        self.model = SentenceTransformer(model_name_path)
        self.vector_store = []
        if vector_store_path:
            self.load_vector_store(vector_store_path)
            print(f'-> load vector store from {vector_store_path}...')

    def text_to_vector(self, text):
        return self.model.encode(text, normalize_embeddings=True)

    def add_data(self, item):
        if item['type'] == 'text':
            vector = self.text_to_vector(item['text'])
            metadata = {
                'doc_id': item['id'],
                'type': 'text',
                'title': item['title'],
                # 'text': item['text'],
            }
        elif item['type'] == 'image':
            vector = self.text_to_vector(item['summary'])
            metadata = {
                'doc_id': item['id'],
                'type': 'image',
                'title': item['title'],
                # 'summary': item['summary'],
                'path': item['path']
            }
        else:
            raise ValueError("Invalid item type")
        
        self.vector_store.append({
            'vector': vector,
            'metadata': metadata,
            'content': item['text'] if item['type'] == 'text' else item['summary']
        })

    def save_vector_store(self, file_path):
        with open(file_path, 'wb') as f:
            pickle.dump(self.vector_store, f)

    def load_vector_store(self, file_path):
        with open(file_path, 'rb') as f:
            self.vector_store = pickle.load(f)

    def query(self, query_text):
        query_vector = torch.from_numpy(self.text_to_vector(query_text)).to(self.device)
        vectors = torch.stack([torch.from_numpy(item['vector'])for item in self.vector_store]).to(self.device) 
            
        similarity_scores = cosine_similarity(query_vector.unsqueeze(0), vectors).squeeze(0)

        results = [
            {
                'score': score.item(),
                'metadata': item['metadata'],
                'content': item['content']
            }
            for score, item in zip(similarity_scores, self.vector_store)
        ]

        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
def weighted_random_choice_no_replacement(docs:list, sample_num:int):
    if sample_num > len(docs):
        raise ValueError("sample_num cannot be greater than the number of docs.")
    
    chosen_docs = []
    
    # Extract probabilities from the 'metadata' field of each document
    probabilities = [doc['metadata'].get('weight', 0.0) for doc in docs]

    for _ in range(sample_num):
        chosen = random.choices(docs, weights=probabilities, k=1)[0]
        chosen_docs.append(chosen)
        index = docs.index(chosen)
        del docs[index]
        del probabilities[index]

    return chosen_docs
    
def load_logger(script_path):
    root_dir = Path(script_path).parent.parent.absolute()
    log_file_name = f'{Path(script_path).stem}-{time.strftime("%Y_%m_%d", time.localtime())}.log'
    
    logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s - %(lineno)d - %(message)s',  # Added correct placeholders
        datefmt='%Y-%m-%d %H:%M:%S', 
        filename=os.path.join(root_dir, 'logs', log_file_name)
    )
    
    return logging

if __name__ == '__main__':
    embed_model_path = '/Users/wenjiazhai/Downloads/project//autodl-tmp/models/bge-base-en-v1.5'
    
    sentences = [
        'Today is a good day.',
        'I am very happy.'
    ]
    
    vector_store = VectorStore(embed_model_path)
    
    for i, sen in enumerate(sentences):
        vector_store.add_data({
            'id': i,
            'text': sen,
            'type': 'text',
            'title': str(i)
        })
        
    print(vector_store.query('Are you happy?'))
