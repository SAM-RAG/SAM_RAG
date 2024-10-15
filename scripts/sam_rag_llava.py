import argparse
import json
import os
import time
import warnings
from collections import Counter
from pathlib import Path

import pandas as pd
import torch
from PIL import Image
from prompt import (image_isRel_instruction, isSup_instruction,
                    isUse_instruction, qa_instruction, text_isRel_instruction)
from tqdm import tqdm
from transformers import AutoProcessor, LlavaForConditionalGeneration
from utils import VectorStore, load_logger

root = Path(__file__).parent.parent.absolute()
with open(os.path.join(Path(__file__).parent.absolute(), 'config.json')) as f:
    config = json.load(f)
logger = load_logger(__file__)
    
warnings.filterwarnings("ignore")
os.environ['TZ'] = config['timezone']
time.tzset()

config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
with open(config_path) as f:
    config = json.load(f)

class BatchAnalyzer:
    def __init__(self, model, processor, self_consistency=False, verbose=False):
        self.model = model
        self.processor = processor
        self.self_consistency = self_consistency
        self.verbose = verbose
        self.contents = []
        self.ids = []
        self.found = False
        self.cur_batch_index = 0
        
    def vlm_image_inference(self, prompt, image_file_path):
        raw_image = Image.open(image_file_path)
        conversation = [
            {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image"},
                ],
            },
        ]
        
        prompt_ = processor.apply_chat_template(conversation, add_generation_prompt=True)
        inputs = processor(images=raw_image, text=prompt_, return_tensors='pt').to(0, torch.float16)
        output = self.model.generate(**inputs, max_new_tokens=1024, do_sample=False)
        response = processor.decode(output[0][2:], skip_special_tokens=True)
        response = '{' + ''.join(response.split('{')[-1])
        response = ''.join(response.rsplit('}')[:-1]) + '}'
        response = response.replace('true', 'True').replace('false', 'False')
        if self.verbose:
            logger(response)
            
        try:
            return eval(response)
        except KeyError as e:
            return {'Reasoning': e, 'Response': 'error'}
        except SyntaxError as e:
            return {'Reasoning': e, 'Response': 'error'}
        except TypeError as e:
            return {'Reasoning': e, 'Response': 'error'}

    def vlm_text_inference(self, prompt):
        conversation = [
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    ],
                },
            ]
        
        prompt_ = processor.apply_chat_template(conversation, add_generation_prompt=True)
        inputs = processor(text=prompt_, return_tensors='pt').to(0, torch.float16)
        output = self.model.generate(**inputs, max_new_tokens=1024, do_sample=False)
        response = processor.decode(output[0][2:], skip_special_tokens=True)
        response = '{' + response.split('{')[-1]
        response = response.rsplit('}')[0] + '}'
        response = response.replace('true', 'True').replace('false', 'False')
        if self.verbose:
            logger(response)
            
        try:
            return eval(response)
        except KeyError as e:
            return {'Reasoning': e, 'Response': 'error'}
        except SyntaxError as e:
            return {'Reasoning': e, 'Response': 'error'}
        except TypeError as e:
            return {'Reasoning': e, 'Response': 'error'}
        except NameError as e:
            return {'Reasoning': e, 'Response': 'error'}
    
    def text_inference_wrapper(self, prompt, self_consistency=False):
        if self_consistency:
            vote = []
        
        for _ in range(5):
            conclusion = self.vlm_text_inference(prompt)
            
            if not self_consistency:
                return conclusion['Response']
            vote.append(conclusion['Response'])
                
        count = Counter(vote)
        selected= count.most_common(1)[0][0]
        return selected
    
    def analyze_batch(self, docs, start_index, batch_size, question):
        end_index = min(start_index + batch_size, len(docs))
        batch_data = docs[start_index:end_index]
        
        for i, doc in enumerate(batch_data):
            logger(f'\nAnalyzing {i + start_index}...')
            
            if doc['metadata']['type'] == 'text':
                text = doc['content']
                title = doc['metadata']['title']
                text_isRel_prompt = text_isRel_instruction + '1. Title: {}\n2. Content: {}\n3. Question: {}\n\nOutput:\n'.format(text, title, question)
                
                isRel_response = self.text_inference_wrapper(text_isRel_prompt, self_consistency = self.self_consistency)
                if self.verbose:
                    logger(f'- text:', text)
                    logger('- text isRel:', isRel_response)
                    
                if isRel_response == True or isRel_response == 'True':
                    if self.verbose:
                        logger('- content matched')
                    self.ids.append(doc['metadata']['doc_id'])
                    self.contents.append('.\n'.join([title, text]))
                    self.found = True
                    
            if doc['metadata']['type'] == 'image':
                if self.verbose:
                    logger(f'- image: {doc["metadata"]["path"]}')
                title = doc['metadata']['title']
                file_name = doc['metadata']['path']
                file_path = os.path.join(root_path, 'data', 'MultiModalQA', 'final_dataset_images', file_name)
                image_isRel_prompt = '1. Title: {}\n2. Question: {}\n\nOutput:\n'.format(title, question)
                
                isRel_response = self.vlm_image_inference(
                    image_isRel_instruction + image_isRel_prompt,
                    file_path
                )
                if self.verbose:
                    logger('\n', title)
                    try:
                        logger('- image caption:', isRel_response['Reasoning'])
                        logger('- image isRel:', isRel_response['Response'], '\n')
                    except:
                        logger('- image caption: error')
                        
                try:
                    if isRel_response['Response'] == True or isRel_response['Response'] == 'True':
                        if self.verbose:
                            logger('- content matched')
                        self.contents.append(isRel_response['Reasoning'])
                        self.ids.append(doc['metadata']['doc_id'])
                        self.found = True
                except:
                    continue
            
    def analyze(self, row, batch_size, sample_num=None):
        '''
        batch_size: number of images to be processed in one batch
        sample_num: number of documents to be analyzed
        '''
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
                    logger('\n- related contexts found in this batch\n')

                qa_prompt = '1. Question: {}\n2. Content: {}'.format(question, ' '.join(self.contents))
                answer = self.text_inference_wrapper(qa_instruction + qa_prompt, self_consistency=True) # self consistency always sets to 'True' for answering
                
                if self.verbose:
                    logger('- answer:', answer, '\n')
                    
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
                is_use = self.text_inference_wrapper(isUse_instruction + isUse_prompt, self_consistency=self.self_consistency)
                if self.verbose:
                    logger('- isUse:', is_use)
                
                if is_use == False or is_use == 'False':
                    logger('- isUse is False, regenerate answer')
                    answer = self.text_inference_wrapper(qa_instruction + qa_prompt, self_consistency=True)
                    is_use = self.text_inference_wrapper(isUse_instruction + isUse_prompt, self_consistency=self.self_consistency)
                    logger(f'- new answer: {answer}')
                
                isSup_prompt = '1. Content: {}\n2. Question: {}\n3. Answer: {}'.format(' '.join(self.contents), question, answer)
                is_sup = self.text_inference_wrapper(isSup_instruction + isSup_prompt, self_consistency=self.self_consistency)
                if self.verbose:
                    logger('- isSup:', is_sup, '\n')
                
                if is_sup == 'True' or is_sup == True:
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
                if is_sup == 'partial':
                    self.found = False
                    continue
                if is_sup == 'False' or is_sup == False:
                    self.found = False
                    self.contents = []
                    self.ids = []
                    continue
                    
        qa_prompt = '1. Question: {}\n2. Content: {}'.format(question, '\n'.join(self.contents))
        answer = self.text_inference_wrapper(qa_instruction + qa_prompt, self_consistency=True)
            
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
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--output_dir', type=str, dest='output_dir', required=True)
    args = argparser.parse_args()
    
    root_path = Path(__file__).parent.parent.absolute()
    dataset = pd.read_json(os.path.join(root_path, 'data', 'MultiModalQA', 'MMQA_train.jsonl'), lines=True)
    
    vlm_model_name = ''
    vlm_model_path = os.path.join(root_path, 'models', vlm_model_name)
    vlm_model = LlavaForConditionalGeneration.from_pretrained(
        vlm_model_path, 
        torch_dtype=torch.float16, 
        low_cpu_mem_usage=True, 
    ).to(0)
    processor = AutoProcessor.from_pretrained(vlm_model_path)
    
    embed_model = ''
    embed_model_path = os.path.join(root_path, 'models', embed_model)
    logger(f'- embedding model: {embed_model_path}')
    
    storage_name = ''
    storage_path = os.path.join(root_path, 'storages', storage_name)
    vector_store = VectorStore(embed_model_path, storage_path)
    
    output_dir = os.path.join('/root/mmRAG', 'output', f'{time.strftime("%Y_%m_%d")}', args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    for (idx, row) in tqdm(dataset.iterrows()):
        start = time.time()
        logger('=====\nline index:', idx)
        output_path = os.path.join(os.path.join(output_dir, f"{(row['qid'])}.json"))
        if os.path.exists(output_path):
            continue
        analyzer = BatchAnalyzer(vlm_model, processor, verbose=True)
        response = analyzer.analyze(row, batch_size=7, sample_num=14)
        with open(output_path, 'w') as f:
            f.write(json.dumps(response) + '\n')
        
        logger(f'- full result:\t{response}')
        