import tweepy
import queue
import threading
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TwitterStreamListener(tweepy.StreamingClient):
    """
    Uses Tweepy v4.x with the Twitter v2 API for streaming.
    """
    def __init__(self, bearer_token, tweet_queue):
        super().__init__(bearer_token=bearer_token, wait_on_rate_limit=True)
        self.tweet_queue = tweet_queue

    def on_tweet(self, tweet):
        """
        Called when a new tweet arrives.
        """
        # Put the tweet text in the queue
        self.tweet_queue.put(tweet.text)
        print(f"New tweet: {tweet.text}")

    def on_errors(self, errors):
        """
        Called when an error occurs.
        """
        print(f"Error: {errors}")
        self.on_connection_error()

    def on_connection_error(self):
        """
        Handle connection errors and attempt to reconnect.
        """
        print("Connection error. Reconnecting in 10s.")
        time.sleep(10)
        self.restart_stream()

    def restart_stream(self):
        """
        Restart the stream after a connection error.
        """
        try:
            self.disconnect()
        except Exception as e:
            print(f"Error disconnecting: {e}")
        time.sleep(2)
        self.filter_thread()

def start_twitter_stream(keywords, tweet_queue):
    """
    Launch the streaming client in a separate thread.
    """
    # Load Twitter API credentials from .env
    BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

    # Initialize the stream listener
    stream = TwitterStreamListener(bearer_token=BEARER_TOKEN, tweet_queue=tweet_queue)

    # Remove old rules if any
    try:
        old_rules = stream.get_rules()
        if old_rules and old_rules.data:
            rule_ids = [r.id for r in old_rules.data]
            stream.delete_rules(rule_ids)
    except tweepy.errors.TweepyException as e:
        print(f"Error removing old rules: {e}")

    # Add new rules for the keywords
    try:
        for kw in keywords:
            stream.add_rules(tweepy.StreamRule(value=kw))
    except tweepy.errors.TweepyException as e:
        print(f"Error adding rules: {e}")

    # Start filtering in a thread
    t = threading.Thread(target=stream.filter, kwargs={'threaded': True})
    t.start()
    return stream