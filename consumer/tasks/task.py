
from typing import Any, Literal, Tuple, Union

import snscrape.modules.twitter as sntwitter
from polyglot.detect import Detector
from polyglot.detect.base import UnknownLanguage
import regex

from nlp.preprocessor import process_transformers

from ..celery import celery, db, en_sentiment_analysis, thai_sentiment_analysis

RE_BAD_CHARS = regex.compile(r"[\p{Cc}\p{Cs}]+")
def remove_bad_chars(text):
    return RE_BAD_CHARS.sub("", text)

@celery.task(name="infer_thai_text")
def infer_thai_text(text:str,request_id:str=None)-> Tuple[Union[Literal['negative', 'neutral', 'positive'] , None, Any]]:
    """
    Infer the sentiment of the given thai text using the Thai sentiment analysis model.

    Parameters
    ----------
    text : str
        The text to infer.
    request_id : str
        The request id of the request.
    """
    print(text)

    preprocess_text = process_transformers(text)
    print(preprocess_text)
    result = thai_sentiment_analysis.infer(preprocess_text)
    if(result[1].item() < 0.6): # if the score is less than 0.6 then it mean model is confused to the result it probably a false positive
        db['test-collection'].insert_one({"request_id":request_id,"raw_text":text,"text":preprocess_text,"sentiment":result[0],"score":result[1].item(),"process_lang":"th","meta":"false_positive_infering_thai"}).inserted_id
    else:
        db['test-collection'].insert_one({"request_id":request_id,"raw_text":text,"text":preprocess_text,"sentiment":result[0],"score":result[1].item(),"process_lang":"th"}).inserted_id

    return result

@celery.task(name="infer_en_text")
def infer_en_text(text:str,request_id:str=None,lang:str=None)->Tuple[Union[Literal['negative', 'neutral', 'positive'] , None, Any]]:
    """
    Infer the sentiment of the given english text using the English sentiment analysis model.

    Parameters
    ----------
    text : str
        The text to infer.
    request_id : str
        The request id.
    lang : str
        The language of the text.
    """
    print("infer_en_text")
    preprocess_text = process_transformers(text)
    result = en_sentiment_analysis.infer(preprocess_text)
    if(result[1].item() < 0.6):
        db['test-collection'].insert_one({"request_id":request_id,"raw_text":text,"text":preprocess_text,"sentiment":result[0],"score":result[1].item(),"process_lang":lang,"meta":"false_positive_infering_other"}).inserted_id
    else:
        db['test-collection'].insert_one({"request_id":request_id,"raw_text":text,"text":preprocess_text,"sentiment":result[0],"score":result[1].item(),"process_lang":lang}).inserted_id

    return result


@celery.task(name="get_twitter_scape",bind=True)
def get_twitter_scape(self,text:str,number_of_tweets:int)->bool:
    """
    Get twitter scape for given text and number of tweets.

    Scapes text then check the language of the tweet and send it to the correct inference task.



    Parameters
    ----------
    text : str
        The text to search for.
    number_of_tweets : int
        The number of tweets to scrape.
    
    

    """
    for i,tweet in enumerate(sntwitter.TwitterSearchScraper(text).get_items()):
        if i>number_of_tweets:
            break
        try :
            celery.send_task('infer_thai_text', args=[f"{tweet.rawContent}",self.request.id])
        #     if Detector(tweet.rawContent).language.code == 'th':
        #         print(f"tweet: {tweet.rawContent} is thai")
        #         celery.send_task('infer_thai_text', args=[f"{tweet.rawContent}",self.request.id])
        #     elif Detector(tweet.rawContent).language.code == 'en':
        #         print(f"tweet: {tweet.rawContent} is english")
        #         celery.send_task('infer_en_text', args=[f"{tweet.rawContent}",self.request.id,"en"])
        #     else:
        #         print(f"tweet: {tweet.rawContent} is other")
        #         celery.send_task('infer_en_text', args=[f"{tweet.rawContent}",self.request.id,"other"])
        except UnknownLanguage:
                celery.send_task('infer_en_text', args=[f"{tweet.rawContent}",self.request.id,"unknow_detected"])

    print(f"Task id: {self.request.id} is done")
    return True



