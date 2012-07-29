#!/usr/bin/env python
import os.path, os, sys
from urlparse import urlparse
from datetime import datetime, date, time

import json
import redis
import logging

import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata

# mah files
import util.tweet_grabber
import util.word_grabber

# import and define tornado-y things
from tornado.options import define, options
define("port", default=5000, help="run on the given port", type=int)
define("redis_host", help="hostname for redis", default="localhost", type=str) # set to localhost for local use
define("redis_port", help="port number for redis", default=6379, type=int) # set to 6379 for local use
define("redis_pass", help="password for redis", default=None, type=int) # set to None for local use
define("redis_db", help="default redis db number", default=0, type=int) # set to whatever for local use
define("watched_bot", help="the name of the bot to watch", default=None)
define("consumer_key", default=None, help="twitter app consumer key", type=str)
define("consumer_secret", default=None, help="twitter app consumer secret", type=str)
define("oauth_token", default=None, help="twitter app consumer key", type=str)
define("token_secret", default=None, help="twitter app consumer secret", type=str)


# application settings and handle mapping info
class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/([^/]+)?", MainHandler)
		]
		settings = dict(
			template_path=os.path.join(os.path.dirname(__file__), "templates"),
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			debug=True,
		)
		tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
	def get_redis_conn(self):
		if os.environ.has_key('REDISTOGO_URL'):
			url = urlparse(os.environ.get('REDISTOGO_URL'))
			return redis.Redis(host=url.hostname, port=url.port, password=url.password)
		else:
			return redis.Redis(host=options.redis_host, port=options.redis_port, db=options.redis_db)

# the main page
class MainHandler(BaseHandler):
	def get(self, def_id):
		# oh hai redis
		db = self.get_redis_conn()
		
		if def_id is not None:
			lastUpdateJSON = db.get("tweets:%s" % def_id)
			if lastUpdateJSON is None:
				lastUpdate = util.tweet_grabber.grab_twitter_updates(def_id)
				logging.info('last update:')
				logging.info(lastUpdate)
		else: 
			lastTweetID = db.lindex("tweets:tweet_ids", 0)
			lastUpdateJSON = db.get("tweets:%s" % lastTweetID)
		lastUpdate = json.loads(lastUpdateJSON)

		# define that word!
		lastDefinition = util.word_grabber.define_word(lastUpdate["text"])

		# which bot are we talking about, anyway?
		watched_bot = util.configs.get_watched_bot(options)

		# analytics, eh
		google_analytics_id = util.configs.get_google_analytics_id()

		# render it up!
		self.render(
			"main.html",
			page_heading = 'define(everyword)',
			google_analytics_id = google_analytics_id,
			watched_bot = watched_bot,
			lastUpdate = lastUpdate,
			lastDefinition = lastDefinition
		)



# RAMMING SPEEEEEEED!
def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(os.environ.get("PORT", 5000))

	# start it up
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()


