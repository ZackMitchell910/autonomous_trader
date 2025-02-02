from dotenv import load_dotenv
import os
import tweepy

# Load environment variables from .env file
load_dotenv()

# Fetch Twitter API credentials from the environment
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

def check_twitter_auth():
    try:
        # Set up Tweepy authentication
        auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
        api = tweepy.API(auth)

        # Verify the credentials
        user = api.verify_credentials()
        if user:
            print(f"Authentication Successful! Logged in as: {user.name} (@{user.screen_name})")
        else:
            print("Authentication Failed! Please check your credentials.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_twitter_auth()
