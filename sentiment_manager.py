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
        """
        Called externally to buffer incoming tweets from X in memory.
        """
        self.realtime_tweets.append(tweet_text)
        # Limit the buffer size
        if len(self.realtime_tweets) > 1000:
            self.realtime_tweets = self.realtime_tweets[-1000:]  # keep last 1000

    def analyze_texts(self, texts):
        """
        Return an average sentiment score (0-1) for a list of texts.
        0 = very negative, 1 = very positive
        """
        if not texts:
            return 0.5  # neutral if no data
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1).numpy()
        scores = probs[:, 1]  # probability of positive
        return float(np.mean(scores))

    def get_market_sentiment(self):
        """
        Combine the average sentiment of the real-time tweet buffer
        with other potential news sources (stubbed out for now).
        """
        if not self.realtime_tweets:
            return 0.5  # neutral if no tweets yet

        # Analyze last N tweets (say 50)
        sample_tweets = self.realtime_tweets[-50:]
        tweet_score = self.analyze_texts(sample_tweets)

        # Weighted average with other sources if desired
        # e.g., combine with crypto headlines or other data
        # For now, we just use tweet_score
        return tweet_score
