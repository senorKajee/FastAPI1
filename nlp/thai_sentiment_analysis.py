from transformers import (
    CamembertTokenizer,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline
)
import numpy as np
from scipy.special import softmax
from nlp.preprocessor import process_transformers
import torch



class ThaiSentimentAnalysis:

    def __init__(self):
        self.tokenizer = CamembertTokenizer.from_pretrained(
            './nlp/thai_tokenizer')
        self.model:torch.nn.Module = torch.jit.load('./nlp/model_thai_sentiment.pt')

        

    def id2label(self, id):
        if id == 0:
            return "negative"
        elif id == 1:
            return "neutral"
        elif id == 2:
            return "positive"
        
    def infer(self, text):
        # processed_text = process_transformers(text)
        encoded_input = self.tokenizer(text, return_tensors='pt')
        output = self.model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)

        scores = scores[:-1]
        scores = scores[::-1]
        sentiment = self.id2label(np.argmax(scores))
        # print(scores)
        # print(scores[np.argmax(scores)])

        return sentiment, scores[np.argmax(scores)]