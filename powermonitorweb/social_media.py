import oauth2 as oauth
import time
import urlparse

class SocialMedia():
    """Social media class for connecting and posting to social media websites like facebook and twitter"""
    callBackUrl = "http://example.com/photos"
    tokenKey = "tok-test-key"
    tokenSecret = "tok-test-secret"
    consumerKey = "con-test-key"
    consumerSecret = "con-test-secret"
    request_token_url = "http://twitter.com/oauth/request_token"
    request_token_url = 'http://twitter.com/oauth/request_token'
    access_token_url = 'http://twitter.com/oauth/access_token'
    authorize_url = 'http://twitter.com/oauth/authorize'

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
        """ We need the client access as part of the connection process for the pin, also provides
         us with the response that allows us to know that connection with twitter was successful
         The content part allows us to get a request token to intiatiate the three legged oauth"""
        # Create your consumer with the proper key/secret.
        consumer = oauth.Consumer(key=self.consumerKey, secret=self.consumerSecret)

        # Request token URL for Twitter.
        # Create our client.
        client = oauth.Client(consumer)

        # The OAuth Client request works just like httplib2 for the most part.
        resp, content = client.request(self.request_token_url, "GET")
        print resp #testing purposes
        print content #testing purposes
        return resp, content

    def three_legged_auth_part1_getrequesttoken(self):
        """ This basically ensures that we did receive a access token, a success  would mean the response is 200
        then we can get a request token"""
        # Step 1: Get a request token. This is a temporary token that is used for
        # having the user authorize an access token and to sign the request to obtain
        # said access token.

        resp, content = self.using_the_client
        if resp['status'] != '200':
            raise EnvironmentError("The request failed")
        request_token = dict(urlparse.parse_qsl(content))
        return request_token

    def three_legged_auth_part2_initiate_redirect(self, request_token):
        # Step 2: Redirect to the provider. Since this is a CLI script we do not
        # redirect. In a web application you would redirect the user to the URL
        # below.

        # we need to figure out how to go to the link, you guys need to sort this out
        print "Go to the following link in your browser:"
        print "%s?oauth_token=%s" % (self.authorize_url, request_token['oauth_token'])

    def three_legged_auth_part3_accept_pin(self):
        # After the user has granted access to you, the consumer, the provider will
        # redirect you to whatever URL you have told them to redirect to. You can
        # usually define this in the oauth_callback argument as well.

        # Okay guys, so here we need to figure out how to accept the pin that they have received
        # This will probably via our website
        # we will probably have to create another temporary link that will accept this pin
        accepted = 'n'
        while accepted.lower() == 'n':
            accepted = raw_input('Have you authorized me? (y/n) ')
        oauth_verifier = raw_input('What is the PIN? ')
        return oauth_verifier

    def three_legged_auth_part4_get_access_token(self, request_token, oauth_verifier):
        # Step 3: Once the consumer has redirected the user back to the oauth_callback
        # URL you can request the access token the user has approved. You use the
        # request token to sign this request. After this is done you throw away the
        # request token and use the access token returned. You should store this
        # access token somewhere safe, like a database, for future use.

        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
        token.set_verifier(oauth_verifier) # got this pin from the user!
        client = oauth.Client(consumer, token)

        resp, content = client.request(self.access_token_url, "POST")
        access_token = dict(urlparse.parse_qsl(content))
        return access_token

    def make_a_tweet(self, access_token):
        """
        hopefully make a tweet!
        :return:
        """
        pass
        # I think this is done via url generation, I'm not sure

        # example
        # status=Maybe%20he%27ll%20finally%20find%20his%20keys.%20%23peterfalk&trim_user=true&include_entities=true
        # So i really definitely think you create a link from the https://api.twitter.com/1/statuses/update.json
        # add all the codes and authentication secrets and keys with the token for his to post, can add hash tags!







