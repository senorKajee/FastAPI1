from transformers import (
    CamembertTokenizer,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline,
    AutoConfig
)
import numpy as np
from scipy.special import softmax
import torch


class EnSentimentAnalysis:

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            './nlp/en_tokenizer')
        self.model:torch.nn.Module = torch.jit.load('./nlp/model_eng_sentiment.pt')
        self.id2label = {
        0: "negative",
        1: "neutral",
        2: "positive"
    }
    def preprocess(self,text):
        new_text = []
        for t in text.split(" "):
            t = '@user' if t.startswith('@') and len(t) > 1 else t
            t = 'http' if t.startswith('http') else t
            new_text.append(t)
            
        return " ".join(new_text)

    def format_output(self, scores):
        
        
        sentiment = self.id2label[np.argmax(scores)]
        # print(scores)
        # print(scores[np.argmax(scores)])

        return sentiment, scores[np.argmax(scores)]

    def infer(self, text):
        print('infering process')
        # processed_text = self.preprocess(text)
        encoded_input = self.tokenizer(text, return_tensors='pt')
        output = self.model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
    

        return self.format_output(scores)