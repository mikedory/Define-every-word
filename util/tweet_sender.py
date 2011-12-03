#!/usr/bin/env python
import os.path, os, sys
from urlparse import urlparse
import datetime, time
import redis
import json
import tornado

import configs
import tweet_shortener
import tweet_grabber
from twitter import Twitter, OAuth


# actually send a tweet
def send_tweet(word, definition, consumer_key, consumer_secret, oauth_token, token_secret):

	print 'trying a tweet here...'

	# set them credentials
	oauth = OAuth(oauth_token, token_secret, consumer_key, consumer_secret)

	# intialize things
	twitter = Twitter(domain='api.twitter.com',
					  auth=oauth,
					  api_version='1')

	# something about url shortening here, I guess?
	tweet_shortener.shorten(definition)

	# Souljaboytellem!
	tweet_string = ("%s: %s" % (word, definition))
	try:
		twitter.statuses.update(status=tweet_string)
	except twitter.api.TwitterHTTPError as oops:
		print oops["details"]

	time.sleep(2)
	print "tweeted!"

	# this is where I should probably make sure it worked, or re-loop?
	time.sleep(2)
	recent = twitter.statuses.user_timeline()
	print recent[0]['text']
	
	# rate_limiting = isinstance(recent.rate_limit_remaining, int)
	# isinstance(recent.rate_limit_reset, int)
	
	print "tweet successful!"


# run dis!
if __name__ == "__main__":
	# hacky way to get around the "tweet is a duplicate" issue in testing
	import random
	word = 'testing: %d' % (random.random()*1000)
	definition = 'jkdsljkls'

	# try tweeting
	vars = configs.get_twitter_vars()
	tweet_attempt = send_tweet(word, definition, vars["consumer_key"], vars["consumer_secret"], vars["oauth_token"], vars["token_secret"])
	if (tweet_attempt != ""):
		print tweet_attempt
	else:
		print "ARRRRGH sorry that didn't quite work."

