from typing import List, Tuple

import numpy as np
import torch
from scipy.special import softmax
from transformers import AutoTokenizer


class EnSentimentAnalysis:

    """
    A class to handle the English sentiment analysis model.

    Attributes
    ----------
    tokenizer : transformers.AutoTokenizer
        The tokenizer of the model.
    model : torch.nn.Module
        The english sentiment analysis model in evaluate mode.
    id2label : dict
        The mapping from the label id to the label name.


    Methods
    -------
    infer(text:str)->Tuple[str,float]
        Infer the sentiment of the given text.s
    """

    def __init__(self) -> None:
        """Load the tokenizer and model. and seting up the defination of the infer result."""
        self.tokenizer = AutoTokenizer.from_pretrained(
            './nlp/en_tokenizer')
        self.model:torch.nn.Module = torch.jit.load('./nlp/model_eng_sentiment.pt')
        self.id2label = {
        0: "negative",
        1: "neutral",
        2: "positive"
    }

    def _format_output(self, scores:List[float])->Tuple[str,float]:
        """Format the output of the model."""
        sentiment = self.id2label[np.argmax(scores)]
        return sentiment, scores[np.argmax(scores)]

    def infer(self, text:str)->Tuple[str,float]:
        """Infer the sentiment of the given text."""
        encoded_input = self.tokenizer(text, return_tensors='pt')
        output = self.model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)

        return self._format_output(scores)
