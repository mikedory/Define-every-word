#!/usr/bin/env python
import os.path, os, sys
from urlparse import urlparse
from datetime import datetime, date, time

import redis

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
print lastUpdate["created_at"]
print lastUpdate["id"]
print lastUpdate["text"]
