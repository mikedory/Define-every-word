#!/usr/bin/env python
import os.path, os, sys
from urlparse import urlparse
from datetime import datetime, date, time
import redis
import json

def get_redis_conn():
	url = urlparse(os.environ.get('REDISTOGO_URL'))
	return redis.Redis(host=url.hostname, port=url.port, password=url.password)

def set_db_defaults(db):
	count = db.setnx("user:checkcount",0)
	lastcheck = db.setnx("user:lastcheck",datetime.now())
	checks = db.setnx("checks",0)
	return checks

def grab_twitter_updates():
	from twitter import Twitter, NoAuth, OAuth, read_token_file
	# twitter
	noauth = NoAuth()
	twitter_na = Twitter(domain='api.twitter.com', auth=noauth, api_version='1')
	return twitter_na.statuses.user_timeline(screen_name="everyword")
	

# oh hai redis
db = get_redis_conn()
defaults = set_db_defaults(db)

# teh twitter
updates = grab_twitter_updates()
lastUpdate = updates[0]

print ("Last update timestamp: %s" % lastUpdate["created_at"])
print ("Last update id: %s" % lastUpdate["id"])
print ("Last update text: %s" % lastUpdate["text"])


datters = db.get("tweets:%s" % lastUpdate["id"])
if datters:
	print("Same tweet. Carry on.")
else:
	print("NEW TWEET!")
	db.set(("tweets:%s" % lastUpdate["id"]), json.dumps(lastUpdate))
	db.lpush("tweets:tweet_ids", lastUpdate["id"])
	db.ltrim("tweets:tweet_ids", 0, 99)
	print("Tweet saved at %s" % datetime.now())
