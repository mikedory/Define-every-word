#!/usr/bin/env python
import os.path, os, sys
from urlparse import urlparse
import datetime, time
import redis
import json
import tornado

import configs
import tweet_grabber
from twitter import Twitter, OAuth


# actually send a tweet
def send_tweet(word, tweet_string, consumer_key, consumer_secret, oauth_token, token_secret):

	print 'trying a tweet here...'

	# set them credentials
	oauth = OAuth(oauth_token, token_secret, consumer_key, consumer_secret)

	# intialize things
	twitter = Twitter(domain='api.twitter.com',
					  auth=oauth,
					  api_version='1')

	# Souljaboytellem!
	print tweet_string
	try:
		twitter.statuses.update(status=tweet_string)
	except twitter.api.TwitterHTTPError as oops:
		print oops["details"]

	# this is where I should probably make sure it worked, or re-loop?
	time.sleep(2)
	recent = twitter.statuses.user_timeline()

	# rate_limiting = isinstance(recent.rate_limit_remaining, int)
	# isinstance(recent.rate_limit_reset, int)
	
	if (recent[0]['text'] == tweet_string):
		return "tweet successful!"
	else:
		return "failed to tweet. >_< "


