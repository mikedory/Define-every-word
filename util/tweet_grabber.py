#!/usr/bin/env python
import os.path, os, sys
from urlparse import urlparse
import datetime, time
import redis
import json

import tweet_sender

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
		# eh, old tweet
		print("Same tweet. Carry on.")
	else:
		# it is a new tweet!
		print("NEW TWEET!")
		
		# save the tweet!
		db.set(("tweets:%s" % lastUpdate["id"]), json.dumps(lastUpdate))
		db.lpush("tweets:tweet_ids", lastUpdate["id"])
		db.ltrim("tweets:tweet_ids", 0, 99)
		print("Tweet saved at %s" % datetime.datetime.now())

		# tweet the tweet!
		tweet_attempt = tweet_sender.send_tweet(lastUpdate["text"])
		print tweet_attempt
		
if __name__ == "__main__":
	grab_all_the_things()
