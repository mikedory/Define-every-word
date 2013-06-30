import urllib
import tornado.auth
import ast


def define_word(word):

    # print 'trying to define...'
    # print word

    # url to snag
    url = "http://www.google.com/dictionary/json?callback=s&q="+word+"&sl=en&tl=en&restrict=pr,de&client=te"

    # have us some variables
    counter = 0
    definition_data = dict()
    definitions = list()

    try:
        # snag the JSON
        http = tornado.httpclient.HTTPClient()
        response = http.fetch(url)

        # thin it out, fix it up, make it valid JSON
        body = response.body
        body = body[2:-10]
        lookup = ast.literal_eval(body)

        # grab the pronunciation and part of speech
        if "primaries" in lookup:
            definition_heads = lookup["primaries"]
            terms = definition_heads[0]['terms']

            print terms
            print len(terms)

            # chunk up the data
            definition_data['part_of_speech'] = urllib.unquote(terms[0]['labels'][0]['text'])
            definition_data['pronunciation_phonetic'] = urllib.unquote(terms[1]['text'])

            # this seems wildly hacky, but it stops the audio from exploding
            if (len(terms) > 2):
                definition_data['pronunciation_audio'] = urllib.unquote(terms[2]['text'])
            else:
                definition_data['pronunciation_audio'] = ""

            # grab all the defnitions associated with the word
            if "webDefinitions" in lookup:
                definition_entries = lookup["webDefinitions"][0]["entries"]
                for entry in definition_entries:
                    if entry["type"] == "meaning":
                        definition_entry = urllib.unquote(entry['terms'][counter]['text'])
                        definitions.append(definition_entry)
                        ++counter
                    else:
                        return "=("

                # add the definitions to the data structure
                definition_data['definitions'] = definitions

                # give it back
                return definition_data

        # lookup failed =(
        else:
            print ">_<"
            return None

    except NameError, e:
        print e

if __name__ == "__main__":
    # print(define_word('outbox'))
    # print(define_word('outbroke'))
    print(define_word('hello'))
