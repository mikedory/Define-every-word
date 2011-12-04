#!/usr/bin/env python
import os.path, os, sys
from urlparse import urlparse
import datetime, time
import redis
import json

# actually send a tweet
def shorten_definition(word, definition):
	# shrink to allow room for word, shortened url, and spacing
	size = (140-19-2-3-len(word))
	short_def = truncate(definition, size)
	return short_def


def truncate(content, length=100, suffix='...'):
	if len(content) <= length:
		return content
	else:
		return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix


def add_link():
	pass

if __name__ == "__main__":
	# thanks to hipster ipsum | http://hipsteripsum.me/?paras=4&type=hipster-latin
	word = 'hipsterrific'
	definition = '8-bit gentrify elit food truck duis mixtape. Aliqua vinyl magna, sed locavore exercitation deserunt tattooed raw denim assumenda proident odio. Cardigan retro cosby sweater, carles tofu organic wolf master cleanse mustache Austin williamsburg wayfarers single-origin coffee beard. Cillum tofu dolore eu gentrify. Biodiesel carles readymade high life qui tumblr +1 3 wolf moon. Ut dreamcatcher art party, delectus anim sustainable fanny pack sed cred single-origin coffee commodo. Austin carles odio mustache craft beer.'
	print shorten_definition(word, definition)