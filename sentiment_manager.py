import re
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import time

class SentimentManager:
    def __init__(self):
        self.model_name = "distilbert-base-uncased-finetuned-sst-2-english"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.realtime_tweets = []

    def add_tweet(self, tweet_text):

        self.realtime_tweets.append(tweet_text)

        if len(self.realtime_tweets) > 1000:
            self.realtime_tweets = self.realtime_tweets[-1000:]  

    def analyze_texts(self, texts):

        if not texts:
            return 0.5  
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1).numpy()
        scores = probs[:, 1] 
        return float(np.mean(scores))

    def get_market_sentiment(self):

        if not self.realtime_tweets:
            return 0.5  # neutral if no tweets yet


        sample_tweets = self.realtime_tweets[-50:]
        tweet_score = self.analyze_texts(sample_tweets)


        return tweet_score
