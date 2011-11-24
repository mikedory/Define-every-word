#!/usr/bin/env python
import os.path, os, sys
from urlparse import urlparse
from datetime import datetime, date, time

import redis

import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata

# import and define tornado-y things
from tornado.options import define, options
define("port", default=5000, help="run on the given port", type=int)
# define("redis_host", help="hostname for redis", default="localhost", type=str) # set to localhost for local use
# define("redis_port", help="port number for redis", default=6379, type=int) # set to 6379 for local use
# define("redis_pass", help="password number for redis", default=6379, type=int) # set to 6379 for local use


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
		# return redis.Redis(host=options.redis_host, port=options.redis_port, db=0)

	def set_db_defaults(self, db):
		# default key-cheking
		db.setnx("user:checkcount",0)
		db.setnx("user:lastcheck",datetime.now())
		db.setnx("checks",0)

	def grab_twitter_updates(self):
		from twitter import Twitter, NoAuth, OAuth, read_token_file
		# twitter
		# from twitter.cmdline import CONSUMER_KEY, CONSUMER_SECRET
		noauth = NoAuth()
		# oauth = OAuth(*read_token_file('tests/oauth_creds')
		#                + (CONSUMER_KEY, CONSUMER_SECRET))

		# twitter = Twitter(domain='api.twitter.com',
		#                   auth=oauth,
		#                   api_version='1')

		twitter_na = Twitter(domain='api.twitter.com', auth=noauth, api_version='1')
		updates = twitter_na.statuses.user_timeline(screen_name="everyword")



# the main page
class MainHandler(BaseHandler):
	def get(self, q):
		if os.environ.has_key('GOOGLEANALYTICSID'):
			google_analytics_id = os.environ['GOOGLEANALYTICSID']
		else:
			google_analytics_id = False

		# oh hai redis
		db = self.get_redis_conn()
		defaults = set_db_defaults()
		
		# teh twitter
		updates = grab_twitter_updates()


		db.sadd("twitter:checks",datetime.now())
		print db.llen("twitter:checks")

		db.incr("twitter:checkcount")

		key = "%s:friends" % (self.current_user['access_token'])
		lastCall = db.get(key)

		self.render(
			"main.html",
			page_heading='Hi!',
			google_analytics_id=google_analytics_id,
			url=url
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


