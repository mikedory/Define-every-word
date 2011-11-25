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
import tweet_grabber
import dictionary

# import and define tornado-y things
from tornado.options import define, options
define("port", default=5000, help="run on the given port", type=int)
define("redis_host", help="hostname for redis", default="localhost", type=str) # set to localhost for local use
define("redis_port", help="port number for redis", default=6379, type=int) # set to 6379 for local use
define("redis_pass", help="password number for redis", default=None, type=int) # set to None for local use


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
		url = urlparse(os.environ.get('REDISTOGO_URL'))
		return redis.Redis(host=url.hostname, port=url.port, password=url.password)


# the main page
class MainHandler(BaseHandler):
	def get(self, q):
		if os.environ.has_key('GOOGLEANALYTICSID'):
			google_analytics_id = os.environ['GOOGLEANALYTICSID']
		else:
			google_analytics_id = False

		# update the twittorz
		# just to check it's all up to date, really
		tweet_grabber.grab_all_the_things()

		# oh hai redis
		db = self.get_redis_conn()
		lastTweetID = db.lindex("tweets:tweet_ids", 0)
		lastUpdateJSON = db.get("tweets:%s" % lastTweetID)
		lastUpdate = json.loads(lastUpdateJSON)
		lastUpdateDefinitions = dictionary.define_word(lastUpdate["text"])

		self.render(
			"home.html",
			page_heading='Hi!',
			google_analytics_id=google_analytics_id,
			lastUpdate=lastUpdate
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


