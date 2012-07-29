#!/usr/bin/env python
import os.path, os, sys
from urlparse import urlparse
import tornado
import redis

# snag the login and all that
import configs

''' 
this is kind of stupid to have in the first palce
but it's basically required because i implemented keys wrong
woooo
'''

# grab a list of all keys, and delete all over 99
def trim_redis_keys():
	db = configs.get_redis_conn()
	keys = db.keys('*')

	print "I hear tell it's time to clean out some keys"

	print "key length: %s" % len(keys)

	if (len(keys) > 99):
		keys.sort()
		keys.reverse()
		keys_to_delete = keys[99:len(keys)]
		for key in keys_to_delete:
			print ('deleting key: %s' % key)
			db.delete(key)
	else:
		print "all good here. as you were."

if __name__ == "__main__":
	trim_redis_keys()