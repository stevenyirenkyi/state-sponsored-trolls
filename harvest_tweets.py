from tweepy import Client, Paginator, User, Tweet
from os import environ
from dotenv import load_dotenv
from random import randint

load_dotenv()


def run(user: User):
    tweepy_client = get_tweepy_client()
    tweets = get_user_tweets(tweepy_client, user.id)

    records = []
    for tweet in tweets:
        user_features = extract_user_features(user)
        user_features.update(extract_tweet_features(tweet))

        records.append(user_features)

    return records


def extract_user_features(user: User) -> dict:
    user_dict = {}
    user_dict["userid"] = user.id
    user_dict["user_display_name"] = user.name
    user_dict["user_screen_name"] = user.username
    user_dict["user_reported_location"] = user.location
    user_dict["user_profile_description"] = user.description
    # user_dict["follower_count"] = user.public_metrics["follower_count"]
    # user_dict["following_count"] = user.public_metrics["following_count"]
    user_dict["tweet_count"] = user["public_metrics"]["tweet_count"]
    user_dict["account_creation_date"] = user.created_at

    return user_dict


def get_tweepy_client() -> Client:
    bearer_token_1 = environ["ACADEMIC_BEARER_TOKEN"]
    bearer_token_2 = environ["ACADEMIC_BEARER_TOKEN_2"]

    bearer_token = bearer_token_1 if randint(0, 9) <= 4 else bearer_token_2

    return Client(bearer_token=bearer_token, wait_on_rate_limit=True)


def get_user_tweets(client: Client, user_id: int) -> list[Tweet]:
    tweets = []

    # TODO: remove limit. set max_results
    for response in Paginator(client.get_users_tweets,
                              user_id,
                              tweet_fields=["author_id", "created_at", "lang",
                                            "source", "entities", "conversation_id",
                                            "in_reply_to_user_id", "referenced_tweets"], limit=1):

        if response.data is None:
            continue

        tweets.extend(response.data)

    return tweets


def extract_tweet_features(tweet: Tweet) -> dict:
    features = {}
    features["tweet_id"] = tweet.id
    features["tweet_text"] = tweet.text
    features["tweet_language"] = tweet.lang
    features["tweet_time"] = tweet.created_at
    features["tweet_client_name"] = tweet.source
    features["in_reply_to_userid"] = tweet.in_reply_to_user_id
    features["in_reply_to_tweetid"] = tweet.conversation_id
    features["is_quote"] = check_if_quote(tweet)
    features["is_retweet"] = check_if_retweet(tweet)
    features.update(get_hashtags(tweet))
    features.update(get_urls(tweet))

    return features


def check_if_quote(tweet: Tweet) -> bool:
    referenced_tweets = tweet.referenced_tweets

    if referenced_tweets is None:
        return False

    for referenced_tweet in referenced_tweets:
        if referenced_tweet["type"] == "quoted":
            return True

    return False


def check_if_retweet(tweet: Tweet) -> bool:
    referenced_tweets = tweet.referenced_tweets

    if referenced_tweets is None:
        return False

    for referenced_tweet in referenced_tweets:
        if referenced_tweet["type"] == "retweeted":
            return True

    return False


def get_hashtags(tweet: Tweet) -> dict:
    entities = tweet.entities
    if entities is None:
        return dict(hashtag_count=0, hashtags="")

    hashtag_list = entities.get("hashtags")
    if hashtag_list is None:
        return dict(hashtag_count=0, hashtags="")

    hashtags = []
    for hashtag_dict in hashtag_list:
        hashtags.append(hashtag_dict["tag"])

    return dict(hashtag_count=len(hashtags), hashtags=" ".join(hashtags))


def get_urls(tweet: Tweet) -> dict:
    entities = tweet.entities
    if entities is None:
        return dict(url_count=0, urls="")

    url_list = entities.get("urls")
    if url_list is None:
        return dict(url_count=0, urls="")

    urls = []
    for url_dict in url_list:
        url = url_dict.get("unwound_url") or url_dict.get("expanded_url")
        urls.append(url)

    return dict(url_count=len(urls), urls=" ♠ ".join(urls))
