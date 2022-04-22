import dotenv
import os
import tweepy
import typing as t


dotenv.load_dotenv()


def post_tweet(tweet_txt: str):
    client = _get_client()
    return _post_tweet(client, tweet_txt)


def get_users_tweets(
    user_id: str,
    max_results: int = 100,
) -> t.List[tweepy.tweet.Tweet]:
    """
    Returns Tweets composed by a single user, 
    specified by the requested user ID. 
    By default, the most recent ten Tweets are returned per request. 
    Using pagination, the most recent 3,200 Tweets can be retrieved.
    https://api.twitter.com/2/users/:id/tweets
    """
    client = _get_client()
    tweets_list = []
    tweets = client.get_users_tweets(id=user_id, max_results=max_results)
    while True:
        if not tweets.data:
            break
        tweets_list.extend(tweets.data)
        if not tweets.meta.get('next_token'):
            break
        tweets = client.get_users_tweets(
            id=user_id,
            pagination_token=tweets.meta['next_token'],
            max_results=max_results,
        )
    return tweets
    # tweets_texts = [tweet.text for tweet in tweets_list]
    # with open('test.pickle', 'wb') as f:
    #     pickle.dump(tweets_texts, f, protocol=pickle.HIGHEST_PROTOCOL)


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
