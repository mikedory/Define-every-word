#!/usr/bin/env python
import os.path, os, sys
from urlparse import urlparse
import datetime, time
import redis
import json
from twitter import Twitter, OAuth

def send_tweet(word):

	if os.environ.has_key('TWITTER_APP_CONSUMER_KEY'):
		# heroku-styles
		consumer_key = urlparse(os.environ.get('TWITTER_APP_CONSUMER_KEY'))
		consumer_secret = urlparse(os.environ.get('TWITTER_APP_CONSUMER_SECRET'))
		oauth_token = urlparse(os.environ.get('TWITTER_USER_OAUTH_TOKEN'))
		token_secret = urlparse(os.environ.get('TWITTER_USER_TOKEN_SECRET'))

	else:
		# local use, probably
		from tornado.options import define, options
		define("consumer_key", default=None, help="twitter app consumer key", type=str)
		define("consumer_secret", default=None, help="twitter app consumer secret", type=str)
		tornado.options.parse_command_line()

		# set them credentials
		oauth = OAuth(oauth_token, token_secret, consumer_key, consumer_secret)

		# intialize things
		twitter = Twitter(domain='api.twitter.com',
		                  auth=oauth,
		                  api_version='1')

		# something about url shortening here, I guess?
		# fancyShortner.shorten()

		# Souljaboytellem!
		tweet_string = ('The new @everyword "%s" means: ' % word)
		twitter.statuses.update(status=tweet_string)
		time.sleep(2)
		print "tweeted!"

	    # this is where I should probably make sure it worked, or re-loop?
		time.sleep(2)
		recent = grab_twitter_updates()
		print recent[0]['text']
		print isinstance(recent.rate_limit_remaining, int)
		print isinstance(recent.rate_limit_reset, int)
		print "tweet successful!"

if __name__ == "__main__":
	send_tweet('test!')