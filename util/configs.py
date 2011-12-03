#!/usr/bin/env python
import os.path, os, sys
from urlparse import urlparse
import tornado
import redis
import datetime, time

def get_twitter_vars():
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
		# 	python util/tweet_sender.py --consumer_key=x --consumer_secret=x --oauth_token=x --token_secret=x
		
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

		return dict(
			consumer_key=consumer_key,
			consumer_secret=consumer_secret,
			oauth_token=oauth_token,
			token_secret=token_secret
		)

def get_redis_conn():
	if os.environ.has_key('REDISTOGO_URL'):
		url = urlparse(os.environ.get('REDISTOGO_URL'))
		return redis.Redis(host=url.hostname, port=url.port, password=url.password)
	else:
		return redis.Redis(host='localhost', port=6379, db=0)

def set_db_defaults(db):
	count = db.setnx("user:checkcount",0)
	lastcheck = db.setnx("user:lastcheck",datetime.datetime.now())
	checks = db.setnx("checks",0)
	return checks