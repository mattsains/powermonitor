import oauth2 as oauth
import time

class SocialMedia():
    """Social media class for connecting and posting to social media websites like facebook and twitter"""
    callBackUrl = "http://example.com/photos"
    tokenKey = "tok-test-key"
    tokenSecret = "tok-test-secret"
    consumerKey = "con-test-key"
    consumerSecret = "con-test-secret"
    request_token_url = "http://twitter.com/oauth/request_token"

    def __init__(self):
        pass

    """The following methods are directly linked to Facebook"""
    def signing_a_request(self):
        """This will be the method that allows our app to be connected to the twitter development"""
        params = {
            'oauth_version': "1.0",
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': int(time.time()),
            #'user': 'joestump', # not sure if we need this
            #'photoid': 555555555555 # not sure if we need this
            }
        # Set up instances of our Token and Consumer. The Consumer.key and
        # Consumer.secret are given to you by the API provider. The Token.key and
        # Token.secret is given to you after a three-legged authentication.
        token = oauth.Token(key=self.tokenKey, secret=self.tokenSecret)
        consumer = oauth.Consumer(key=self.consumerKey, secret=self.consumerSecret)
        # Set our token/key parameters
        params['oauth_token'] = token.key
        params['oauth_consumer_key'] = consumer.key

        # Create our request. Change method, etc. accordingly.
        req = oauth.Request(method="GET", url=self.callBackUrl, parameters=params)

        # Sign the request.
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, consumer, token)

    def using_the_client(self):
        """"""
        # Create your consumer with the proper key/secret.
        consumer = oauth.Consumer(key=self.consumerKey, secret=self.consumerSecret)

        # Request token URL for Twitter.
        # Create our client.
        client = oauth.Client(consumer)

        # The OAuth Client request works just like httplib2 for the most part.
        resp, content = client.request(self.request_token_url, "GET")
        print resp #testing purposes
        print content #testing purposes
    
