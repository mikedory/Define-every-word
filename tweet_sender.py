#!/usr/bin/env python
import os.path, os, sys
from urlparse import urlparse
import datetime, time
import redis
import json
import tornado
from twitter import Twitter, OAuth

# define the variables and stuff
if os.environ.has_key('TWITTER_APP_CONSUMER_KEY'):
	# heroku-styles
	consumer_key = urlparse(os.environ.get('TWITTER_APP_CONSUMER_KEY'))
	consumer_secret = urlparse(os.environ.get('TWITTER_APP_CONSUMER_SECRET'))
	oauth_token = urlparse(os.environ.get('TWITTER_USER_OAUTH_TOKEN'))
	token_secret = urlparse(os.environ.get('TWITTER_USER_TOKEN_SECRET'))

else:
	# local use, via tornado command flags
	# run like:
	# 	python tweet_sender.py --consumer_key=x --consumer_secret=x --oauth_token=x --token_secret=x
	
	# snag off the command line
	from tornado.options import define, options
	define("consumer_key", default=None, help="twitter app consumer key", type=str)
	define("consumer_secret", default=None, help="twitter app consumer secret", type=str)
	define("oauth_token", default=None, help="twitter app consumer key", type=str)
	define("token_secret", default=None, help="twitter app consumer secret", type=str)

	# define all the things here
	tornado.options.parse_command_line()
	consumer_key = options.consumer_key
	consumer_secret = options.consumer_secret
	oauth_token = options.oauth_token
	token_secret = options.token_secret

# actually send a tweet
def send_tweet(word, consumer_key, consumer_secret, oauth_token, token_secret):

	print 'trying a tweet here...'

	# set them credentials
	oauth = OAuth(oauth_token, token_secret, consumer_key, consumer_secret)

	# intialize things
	twitter = Twitter(domain='api.twitter.com',
					  auth=oauth,
					  api_version='1')

	# something about url shortening here, I guess?
	# fancyShortner.shorten()

	# Souljaboytellem!
	tweet_string = ("%s: a definition of sorts" % word)
	twitter.statuses.update(status=tweet_string)
	time.sleep(2)
	print "tweeted!"

	# this is where I should probably make sure it worked, or re-loop?
	time.sleep(2)
	recent = twitter.statuses.user_timeline()
	print recent[0]['text']
	print isinstance(recent.rate_limit_remaining, int)
	print isinstance(recent.rate_limit_reset, int)
	print "tweet successful!"


# run dis!
if __name__ == "__main__":
	tweet_attempt = send_tweet('test!', consumer_key, consumer_secret, oauth_token, token_secret)
	if (tweet_attempt != ""):
		print tweet_attempt
	else:
		print "ARRRRGH sorry that didn't quite work."