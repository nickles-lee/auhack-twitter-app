import tweepy

class TwitterPool():
    def __init__(self, consumer_key, consumer_secret, access_token, access_secret, name):
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.set_access_token(access_token, access_secret)
        self.api = tweepy.API(self.auth)
        self.is_disabled = False
        self.was_disabled_at = None
        self.name = name
