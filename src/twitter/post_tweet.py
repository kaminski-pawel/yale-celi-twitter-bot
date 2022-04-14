import dotenv
import os
import tweepy

dotenv.load_dotenv()


def post_tweet(tweet_txt: str):
    client = _get_client()
    return _post_tweet(client, tweet_txt)


def _get_client():
    return tweepy.Client(
        bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
        consumer_key=os.getenv('TWITTER_API_KEY'),
        consumer_secret=os.getenv('TWITTER_API_KEY_SECRET'),
        access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
        access_token_secret=os.getenv('TWITTER_TOKEN_SECRET'),
    )


def _post_tweet(client: tweepy.Client, tweet_txt: str):
    return client.create_tweet(text=tweet_txt)
