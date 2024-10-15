import json
import os
import time
import requests
import base64
import warnings
from collections import Counter
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from urllib3.exceptions import ProtocolError
from http.client import RemoteDisconnected

from utils import VectorStore, load_logger
from prompt import (text_isRel_instruction, qa_instruction, isSup_instruction, isUse_instruction,
                    image_isRel_instruction)
logger = load_logger(__file__)

root = Path(__file__).parent.parent.absolute()
with open(os.path.join(Path(__file__).parent.absolute(), 'config.json')) as f:
    config = json.load(f)
    
warnings.filterwarnings("ignore")
os.environ['TZ'] = config['timezone']
time.tzset()

config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
with open(config_path) as f:
    config = json.load(f)
    
key = config['gpt_key']
url = config['gpt_url']
model = config['gpt_model']

class BatchAnalyzer:
    def __init__(self, key, url, model, self_consistency=False, verbose=False):
        self.key = key
        self.url = url
        self.model = model
        self.self_consistency = self_consistency
        self.verbose = verbose
        self.contents = []
        self.ids = []
        self.found = False
        self.cur_batch_index = 0
        
    # Function to encode the image
    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def gpt_image_inference(self, instruction, prompt, image_file_path):
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.key}"
            }
            
            # Getting the base64 string
            base64_image = self.encode_image(image_file_path)
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system", 
                        "content": [
                            {
                                "type": "text",
                                "text": instruction
                            }
                        ]
                    },
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },{
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1024,
                "temperature": 1.2,
                'response_format': {"type": "json_object"},
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload)
                response = response.json()['choices'][0]['message']['content']
                response = '{' + ''.join(response.split('{')[-1])
                response = ''.join(response.rsplit('}')[:-1]) + '}'
                logger(response)
                return eval(response)
            except requests.exceptions.ConnectionError as e:
                logger("ConnectionError: 网络连接问题", e)
                return {'Reasoning': e, 'Response': 'error'}
            except RemoteDisconnected as e:
                logger("RemoteDisconnected: 远端关闭了连接", e)
                return {'Reasoning': e, 'Response': 'error'}
            except ProtocolError as e:
                logger("ProtocolError: 协议错误", e)
                return {'Reasoning': e, 'Response': 'error'}
            except requests.exceptions.RequestException as e:
                logger("其他请求相关异常", e)
                return {'Reasoning': e, 'Response': 'error'}
            except KeyError as e:
                logger("KeyError: 键值错误", e)
                return {'Reasoning': e, 'Response': 'error'}
            except SyntaxError as e:
                logger("SyntaxError: 语法错误", e)
                return {'Reasoning': e, 'Response': 'error'}
            except TypeError as e:
                logger("TypeError: 类型错误", e)
                return {'Reasoning': e, 'Response': 'error'}
            except AttributeError as e:
                logger("AttributeError: 属性错误", e)
                return {'Reasoning': e, 'Response': 'error'}
    
    def gpt_text_inference(self, instruction, prompt):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": instruction},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1024,
            "temperature": 1.2,
            'response_format': {"type": "json_object"},
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response = response.json()['choices'][0]['message']['content']
            response = '{' + ''.join(response.split('{')[-1])
            response = ''.join(response.rsplit('}')[:-1]) + '}'
            if self.verbose:
                logger(response)
            return eval(response)
        except requests.exceptions.ConnectionError as e:
            return {'Reasoning': e, 'Response': 'error'}
        except RemoteDisconnected as e:
            return {'Reasoning': e, 'Response': 'error'}
        except ProtocolError as e:
            return {'Reasoning': e, 'Response': 'error'}
        except requests.exceptions.RequestException as e:
            return {'Reasoning': e, 'Response': 'error'}
        except KeyError as e:
            return {'Reasoning': e, 'Response': 'error'}
        except SyntaxError as e:
            return {'Reasoning': e, 'Response': 'error'}
        except TypeError as e:
            return {'Reasoning': e, 'Response': 'error'}
        except AttributeError as e:
            return {'Reasoning': e, 'Response': 'error'}
    
    def text_inference_wrapper(self, instruction, prompt, self_consistency=False):
        if self_consistency:
            vote = []
        
        for _ in range(5):
            conclusion = self.gpt_text_inference(instruction, prompt)
            response = conclusion['Response']
            
            if not self_consistency:
                return response
            vote.append(response)
                
        count = Counter(vote)
        selected= count.most_common(1)[0][0]
        return selected
    
    def analyze_batch(self, docs, start_index, batch_size, question):
        end_index = min(start_index + batch_size, len(docs))
        batch_data = docs[start_index:end_index]
        
        for i, doc in enumerate(batch_data):
            logger(f'\rAnalyzing {i + start_index}...', end='')
            
            if doc['metadata']['type'] == 'text':
                text = doc['content']
                title = doc['metadata']['title']
                text_isRel_prompt = "1. Title: {}\n2. Content: {}\nQuestion: {}".format(title, text, question)
                
                isRel_response = self.text_inference_wrapper(text_isRel_instruction, text_isRel_prompt, self_consistency = self.self_consistency)
                if self.verbose:
                    logger(f'text:', text)
                    logger('isRel:', isRel_response, '\n')
                    
                if isRel_response == 'True':
                    if self.verbose:
                        logger('content matched')
                    self.ids.append(doc['metadata']['doc_id'])
                    self.contents.append('.\n'.join([title, text]))
                    self.found = True
                    
            if doc['metadata']['type'] == 'image':
                if self.verbose:
                    logger(f'image: {doc["metadata"]["path"]}')
                title = doc['metadata']['title']
                file_name = doc['metadata']['path']
                file_path = os.path.join(root, 'mmRAG', 'data', 'MultiModalQA', 'final_dataset_images', file_name)
                image_isRel_prompt = '1. Title: {}\n2. Question: {}'.format(title, question)
                
                response = self.gpt_image_inference(
                    image_isRel_instruction,
                    image_isRel_prompt,
                    file_path
                )
                if self.verbose:
                    logger('\n', title)
                    logger(response, '\n')
                    time.sleep(10)
                    
                if response['Response'] == 'True':
                    self.contents.append(response['Reasoning'])
                    self.ids.append(doc['metadata']['doc_id'])
                    self.found = True
        
    def analyze(self, row, batch_size, sample_num=None):
        qid = row['qid']
        question = row['question']
        if not sample_num:
            docs = vector_store.query(question)
        else:
            docs = vector_store.query(question)[:sample_num]
            
        gold_ref = [context['doc_id'] for context in row['supporting_context'] if context['doc_part'] in ['image', 'text']]
        gold_answers = [ans['answer'] for ans in row['answers']]
        is_sup = None
        is_use = None
        
        if self.verbose:
            logger(question, '\n')
        
        for i in range(len(docs) // batch_size + 1):
            self.analyze_batch(docs, i*batch_size, batch_size, question)
            
            if self.found:
                if self.verbose:
                    logger('found:', self.found)
                    logger('------------------------')
                qa_prompt = '1. Question: {}\n2. Content: {}'.format(question, ' '.join(self.contents))
                answer = self.text_inference_wrapper(qa_instruction, qa_prompt, self_consistency=True)
                
                if self.verbose:
                    logger('answer:', answer)
                    
                # return {
                #     'qid': qid,
                #     'question': question,
                #     'gold_ref': gold_ref,
                #     'gold_answers': gold_answers,
                #     'pred_ref': self.ids,
                #     'pred_answer': answer,
                #     'isSup': is_sup,
                #     'isUse': is_use,
                # }
                
                isUse_prompt = '1. Content: {}\n2. Question: {}\n3. Answer: {}'.format(' '.join(self.contents), question, answer)
                is_use = self.text_inference_wrapper(isUse_instruction, isUse_prompt, self_consistency=self.self_consistency)
                if self.verbose:
                    logger('isUse:', is_use)
                
                if is_use == 'False':
                    answer = self.text_inference_wrapper(qa_instruction, qa_prompt, self_consistency=True)
                    is_use = self.text_inference_wrapper(isUse_instruction, isUse_prompt, self_consistency=self.self_consistency)
                
                # isSup_prompt = '1. Content: {}\n2. Question: {}\n3. Answer: {}'.format(' '.join(self.contents), question, answer)
                # is_sup = self.text_inference_wrapper(isSup_instruction, isSup_prompt, self_consistency=self.self_consistency)
                # if self.verbose:
                #     logger('isSup:', is_sup)
                #     logger('------------------------')
                
                # if is_sup == 'partial':
                #     self.found = False
                #     continue
                # if is_sup == 'False':
                #     self.found = False
                #     self.contents = []
                #     self.ids = []
                #     continue
                    
                # if is_sup == 'True' and is_use == 'True':
                if is_use == 'True':
                    return {
                                'qid': qid,
                                'question': question,
                                'gold_ref': gold_ref,
                                'gold_answers': gold_answers,
                                'pred_ref': self.ids,
                                'pred_answer': answer,
                                'isSup': is_sup,
                                'isUse': is_use,
                            }
                else:
                    self.found = False
                
        if self.contents:
            qa_prompt = '1. Question: {}\n2. Content: {}'.format(question, ''.join(self.contents))
            answer = self.text_inference_wrapper(qa_instruction, qa_prompt, self_consistency=True)
        else:
            answer = ''
            
        return {
                    'qid': qid,
                    'question': question,
                    'gold_ref': gold_ref,
                    'gold_answers': gold_answers,
                    'pred_ref': self.ids,
                    'pred_answer': answer,
                    'isSup': is_sup,
                    'isUse': is_use,
                }
        
        
if __name__ == '__main__':
    root = Path(__file__).parent.parent.absolute()

    dataset = os.path.join(root, 'data', 'MultiModalQA', '...')
    
    embed_model_name = ''
    embed_model_path = os.path.join(root, 'models',  embed_model_name)
    
    storage_name = ''
    storage_path = os.path.join(root, 'stoarges', storage_name)
    
    vector_store = VectorStore(embed_model_path, storage_path)
    
    output_dir = ''
    output_path = os.path.join(root, 'output', output_dir)
    os.makedirs(output_path, exist_ok=True)
    logger(f'making output folder:', output_dir, '\n')

    logger('start inference...')
    for (idx, row) in tqdm(dataset.iterrows()):
        logger('=====\nline index:', idx)
        output_path = os.path.join(os.path.join(output_path, f"{row['qid']}.json"))
        if os.path.exists(output_path):
            continue
        analyzer = BatchAnalyzer(key, url, model, verbose=True)
        response = analyzer.analyze(row, batch_size=6, sample_num=18)
        with open(output_path, 'w') as f:
            f.write(json.dumps(response, ensure_ascii=False, indent=4) + '\n')
        
        logger(response)
        logger('-----')

    logger('done!')