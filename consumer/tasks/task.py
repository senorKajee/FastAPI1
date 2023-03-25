
from typing import Any, Literal, Tuple, Union

import snscrape.modules.twitter as sntwitter
from langdetect import detect

from nlp.preprocessor import process_transformers

from ..celery import celery, db, en_sentiment_analysis, thai_sentiment_analysis
from bson.objectid import ObjectId
from typing import List, Tuple
import datetime
from datetime import date
from celery.result import AsyncResult
from dateutil import parser

@celery.task(name="infer_thai_text",acks_late=True)
def infer_thai_text(keyword:str,text:str,tweet_date:date,analysisJobId:str=None)-> Tuple[Union[Literal['negative', 'neutral', 'positive'] , None, Any]]:
    """
    Infer the sentiment of the given thai text using the Thai sentiment analysis model.

    Parameters
    ----------
    text : str
        The text to infer.
    request_id : str
        The request id of the request.
    """
    #publishData

    preprocess_text = process_transformers(text)
    print(preprocess_text)
    result = thai_sentiment_analysis.infer(preprocess_text)
    # if(result[1].item() < 0.6): # if the score is less than 0.6 then it mean model is confused to the result it probably a false positive
    #     db['SentimentResult'].insert_one({"request_id":analysisJobId,"analysisJobId":ObjectId(analysisJobId),"raw_text":text,"text":preprocess_text,"sentiment":result[0],"score":result[1].item(),"process_lang":"th","meta":"false_positive_infering_thai"}).inserted_id
    # else:
    #     db['SentimentResult'].insert_one({"request_id":analysisJobId,"analysisJobId":ObjectId(analysisJobId),"raw_text":text,"text":preprocess_text,"sentiment":result[0],"score":result[1].item(),"process_lang":"th"}).inserted_id

    db['SentimentResult'].insert_one({"analysisJobId":ObjectId(analysisJobId),"publishData":tweet_date,"keyword":keyword,"raw_text":text,"text":preprocess_text,"sentiment":result[0],"score":result[1].item(),"process_lang":"th"}).inserted_id
    
    return result

@celery.task(name="infer_en_text",acks_late=True)
def infer_en_text(keyword:str,text:str,tweet_date:date,analysisJobId:str=None,lang:str=None)->Tuple[Union[Literal['negative', 'neutral', 'positive'] , None, Any]]:
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
    # if(result[1].item() < 0.6):
    #     db['SentimentResult'].insert_one({"request_id":analysisJobId,"analysisJobId":analysisJobId,"raw_text":text,"text":preprocess_text,"sentiment":result[0],"score":result[1].item(),"process_lang":lang,"meta":"false_positive_infering_other"}).inserted_id
    # else:
    #     db['SentimentResult'].insert_one({"request_id":analysisJobId,"analysisJobId":analysisJobId,"raw_text":text,"text":preprocess_text,"sentiment":result[0],"score":result[1].item(),"process_lang":lang}).inserted_id
    db['SentimentResult'].insert_one({"analysisJobId":ObjectId(analysisJobId),"publishData":tweet_date,"keyword":keyword,"raw_text":text,"text":preprocess_text,"sentiment":result[0],"score":result[1].item(),"process_lang":lang}).inserted_id
   
    return result


@celery.task(name="get_twitter_scape",bind=True,acks_late=True)
def get_twitter_scape(self,text_lst:List[str],number_of_tweets:int,analysisJobId:str,since:str,until:str)->bool:
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
    bson_obj = ObjectId(analysisJobId)
    db['AnalysisJob'].update_one({"_id":bson_obj},{"$set":{"status":"RUNNING"}}) 
    # Polyglot is not stable in dependency so we will make it optional here (WIP Module).
    # start_date = datetime.date(2022, 1, 1)
    # end_date = datetime.date.today()
    start_date = parser.parse(since)
    end_date = parser.parse(until)
    since_str = start_date.strftime('%Y-%m-%d')
    until_str = end_date.strftime('%Y-%m-%d')
    print(since_str,until_str)
    task_count = 0
    task_ids = []

    for search_text in text_lst:
         
        for i,tweet in enumerate(sntwitter.TwitterSearchScraper(search_text+f' since:{since_str} until:{until_str}').get_items()):
            if i>number_of_tweets:
                break

            try :
                buff = detect(tweet.rawContent)
                
                if buff == 'th':
                    print(f"tweet: {tweet.rawContent} is thai")
                    task_id = celery.send_task('infer_thai_text', args=[search_text,f"{tweet.rawContent}",tweet.date,analysisJobId]).task_id
                elif buff == 'en':
                    print(f"tweet: {tweet.rawContent} is english")
                    task_id = celery.send_task('infer_en_text', args=[search_text,f"{tweet.rawContent}",tweet.date,analysisJobId,"en"]).task_id
                else:
                    print(f"tweet: {tweet.rawContent} is other")
                    task_id = celery.send_task('infer_en_text', args=[search_text,f"{tweet.rawContent}",tweet.date,analysisJobId,"other"]).task_id
                task_count += 1
            except Exception:
                    task_id = celery.send_task('infer_en_text', args=[search_text,f"{tweet.rawContent}",tweet.date,analysisJobId,"unknow_detected"]).task_id
                    task_count += 1
            
            task_ids.append(task_id)

    if task_count == 0:
        db['AnalysisJob'].update_one({"_id":bson_obj},{"$set":{"status":"DONE"}})

    for task_id in task_ids:
        result = AsyncResult(task_id)
        if result.ready():
             pass
        
    db['AnalysisJob'].update_one({"_id":ObjectId(analysisJobId)},{"$set":{"status":"DONE"}})

    print(f"Task id: {self.request.id} is done")
    return True



