import os
import time
import snscrape.modules.twitter as sntwitter
import pandas as pd
from ..celery import celery,thai_sentiment_analysis,en_sentiment_analysis,db
from polyglot.detect import Detector
from polyglot.detect.base import UnknownLanguage
from nlp.preprocessor import process_transformers
import datetime
@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True

@celery.task(name="infer_thai_text")
def infer_thai_text(text,request_id=None):
    print(text)

    preprocess_text = process_transformers(text)
    print(preprocess_text)
    result = thai_sentiment_analysis.infer(preprocess_text)
    if(result[1].item() < 0.6):
        r = db['test-collection'].insert_one({"request_id":request_id,"raw_text":text,"text":preprocess_text,"sentiment":result[0],"score":result[1].item(),"process_lang":"th","meta":"false_positive_infering_thai"}).inserted_id
    else:
        r = db['test-collection'].insert_one({"request_id":request_id,"raw_text":text,"text":preprocess_text,"sentiment":result[0],"score":result[1].item(),"process_lang":"th"}).inserted_id

    return result

@celery.task(name="infer_en_text")
def infer_en_text(text,request_id=None,lang=None):

    print("infer_en_text")
    preprocess_text = process_transformers(text)
    result = en_sentiment_analysis.infer(preprocess_text)
    if(result[1].item() < 0.6):
        r = db['test-collection'].insert_one({"request_id":request_id,"raw_text":text,"text":preprocess_text,"sentiment":result[0],"score":result[1].item(),"process_lang":lang,"meta":"false_positive_infering_other"}).inserted_id
    else:  
        r = db['test-collection'].insert_one({"request_id":request_id,"raw_text":text,"text":preprocess_text,"sentiment":result[0],"score":result[1].item(),"process_lang":lang}).inserted_id

    return result


@celery.task(name="get_twitter_scape",bind=True)
def get_twitter_scape(self,text,number_of_tweets):
    attributes_container = []

    # Using TwitterSearchScraper to scrape data and append tweets to list

    for i,tweet in enumerate(sntwitter.TwitterSearchScraper(text).get_items()):
        if i>number_of_tweets:
            break
        try :
            if Detector(tweet.rawContent).language.code == 'th':
                print(f"tweet: {tweet.rawContent} is thai")
                celery.send_task('infer_thai_text', args=[f"{tweet.rawContent}",self.request.id])
            elif Detector(tweet.rawContent).language.code == 'en':
                print(f"tweet: {tweet.rawContent} is english")
                celery.send_task('infer_en_text', args=[f"{tweet.rawContent}",self.request.id,"en"])
            else:
                print(f"tweet: {tweet.rawContent} is other")
                # preprocess_text = process_transformers(tweet.rawContent)
                celery.send_task('infer_en_text', args=[f"{tweet.rawContent}",self.request.id,"other"])
        except UnknownLanguage:
                celery.send_task('infer_en_text', args=[f"{tweet.rawContent}",self.request.id,"unknow_detected"])




        # attributes_container.append([tweet.date, tweet.likeCount, tweet.sourceLabel, tweet.rawContent,tweet.replyCount])

    print(f"Task id: {self.request.id} is done")
    return True
    # Creating a dataframe from the tweets list above 
    


