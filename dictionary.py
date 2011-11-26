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
		definition_data = dict()
		definitions = list()

		# grab the pronunciation and part of speech
		if lookup.has_key("primaries"):
			definition_heads = lookup["primaries"]
			terms = definition_heads[0]['terms']
			definition_data['part_of_speech'] = terms[0]['labels'][0]['text']
			definition_data['pronunciation_phonetic'] = terms[1]['text']
			definition_data['pronunciation_audio'] = terms[2]['text']
		
		# grab all the defnitions associated with the word
		if lookup.has_key("webDefinitions"):
			definition_entries = lookup["webDefinitions"][0]["entries"]
			for entry in definition_entries:	
				if entry["type"] == "meaning":
					definition_entry = urllib.unquote(entry['terms'][counter]['text'])
					definitions.append(definition_entry)
					++counter
				else:
					return "=("
			definition_data['definitions'] = definitions
			return definition_data

	except URLError, e:
		print e.code
		print e.read()
