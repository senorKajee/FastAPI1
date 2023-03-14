from typing import Any, Literal, Tuple, Union

import numpy as np
import torch
from scipy.special import softmax
from transformers import CamembertTokenizer


class ThaiSentimentAnalysis:

    """
    A class to handle the Thai sentiment analysis model.

    Attributes
    ----------
    tokenizer : transformers.CamembertTokenizer
        The tokenizer of the model.
    model : torch.nn.Module
        The thai sentiment analysis model in evaluate mode.
    id2label : dict
        The mapping from the label id to the label name.

    Methods
    -------
    infer(text:str)->Tuple[Union[Literal['negative', 'neutral', 'positive'] ,None, Any]]
        Infer the sentiment of the given text.
    """

    def __init__(self) -> None:
        """Load the tokenizer and model. and seting up the defination of the infer result."""
        self.tokenizer = CamembertTokenizer.from_pretrained(
            './nlp/thai_tokenizer')
        self.model:torch.nn.Module = torch.jit.load('./nlp/model_thai_sentiment.pt')
        self.id2label = {
        0: "negative",
        1: "neutral",
        2: "positive"
        }


    def infer(self, text:str)->Tuple[Union[Literal['negative', 'neutral', 'positive'] ,None, Any]]:
        """Infer the sentiment of the given text."""
        encoded_input = self.tokenizer(text, return_tensors='pt')
        output = self.model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)

        scores = scores[:-1]
        scores = scores[::-1]
        sentiment = self.id2label[np.argmax(scores)]

        return sentiment, scores[np.argmax(scores)]
