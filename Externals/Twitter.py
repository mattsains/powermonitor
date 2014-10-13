from rauth import OAuth1Service
import time
import urlparse

class Twitter():
    """Provides the glue between a common social media API and the Twitter API"""

    # statics:
    _twitter_api = OAuth1Service(
        name="twitter",
        consumer_key="VgdIuvcYYe26gYaYigQLbYsAP",
        consumer_secret="IoQoiUumSjBBF1dc708YGCxZ4ZqptCGQS1MNES45cgiXdO97TH",
        request_token_url="https://twitter.com/oauth/request_token",
        access_token_url="https://api.twitter.com/oauth/access_token",
        authorize_url="https://api.twitter.com/oauth/authenticate",
        base_url="https://api.twitter.com/1.1/")
    
    # instance vars:
    request_token = None
    request_token_secret = None
    authorized_verifier = None
    authorized_session = None

    def authorize(self, callback_url):
        """callback_url should forward the request to authorize_receive()"""
        """Returns a URL to redirect to"""
        self.request_token, self.request_token_secret = self._twitter_api.get_request_token(params={'oauth_callback':callback_url})
        return "https://api.twitter.com/oauth/authenticate?oauth_token=%s"%self.request_token
    
    def authorize_receive(self, oauth_token, oauth_verifier):
        if oauth_token != self.request_token:
            raise EnvironmentError("Response from twitter does not match token sent")
        self.authorized_verifier = oauth_verifier
        self.authorized_session = self._twitter_api.get_auth_session(self.request_token, self.request_token_secret, params={'oauth_verifier':self.authorized_verifier})
        return True
    
    def tweet(self, message):
        response = self.authorized_session.post("statuses/update.json", data={'status':message})
        if response.status_code == 200:
            return True
        else:
            raise EnvironmentError("Failed to send tweet")
       
