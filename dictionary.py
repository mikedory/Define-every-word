import urllib
import tornado.auth
import json
import ast

def define_word(word):
	url="http://www.google.com/dictionary/json?callback=s&q="+word+"&sl=en&tl=en&restrict=pr,de&client=te"
	defined_words = list()
	try:
		http = tornado.httpclient.HTTPClient()
		response = http.fetch(url)
		body = response.body
		body = body[2:-10]
		lookup = ast.literal_eval(body)
		counter = 0
		if lookup.has_key("webDefinitions"):
			definitions = lookup["webDefinitions"][0]["entries"]
			for definition in definitions:	
				if definition["type"] == "meaning":
					string = urllib.unquote(definition['terms'][counter]['text'])
					defined_words.append(string)
					++counter
				else:
					return "=("
			return defined_words
	except URLError, e:
		print e.code
		print e.read()