#!/usr/bin/env python
import os.path, os, sys
from urlparse import urlparse
import datetime, time
import redis
import json

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

def grab_twitter_updates():
	from twitter import Twitter, NoAuth
	# twitter
	noauth = NoAuth()
	twitter_na = Twitter(domain='api.twitter.com', auth=noauth, api_version='1')
	return twitter_na.statuses.user_timeline(screen_name="everyword")
	
def grab_all_the_things():
	# oh hai redis
	db = get_redis_conn()
	defaults = set_db_defaults(db)

	# teh twitter
	updates = grab_twitter_updates()
	lastUpdate = updates[0]
	timestampsting = lastUpdate["created_at"] + ' UTC'
	timestamp = time.mktime(time.strptime(timestampsting,  '%a  %b %d %H:%M:%S +0000 %Y %Z'))
	lastUpdate["timestamp"] = timestamp

	print ("Last update created_at: %s" % lastUpdate["created_at"])
	print ("Last update timestamp: %s" % lastUpdate["timestamp"])
	print ("Last update id: %s" % lastUpdate["id"])
	print ("Last update text: %s" % lastUpdate["text"])

	'''
	This should look like:

	Last update created_at: Sat Nov 26 16:30:03 +0000 2011
	Last update timestamp: 1322343003.0
	Last update id: 140467359902203906
	Last update text: optioning
	'''


	datters = db.get("tweets:%s" % lastUpdate["id"])
	if datters:
		print("Same tweet. Carry on.")
	else:
		print("NEW TWEET!")
		db.set(("tweets:%s" % lastUpdate["id"]), json.dumps(lastUpdate))
		db.lpush("tweets:tweet_ids", lastUpdate["id"])
		db.ltrim("tweets:tweet_ids", 0, 99)
		print("Tweet saved at %s" % datetime.datetime.now())

if __name__ == "__main__":
	grab_all_the_things()

def send_tweet(word):
	from twitter import Twitter, OAuth

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
