#!/usr/bin/env python
import datetime
import time
import json

import configs
import tweet_sender
import tweet_shortener
import word_grabber
import redis_cleanup


def grab_twitter_updates(tweet_id=None):
    # tweetorz
    from twitter import Twitter, OAuth
    vars = configs.get_twitter_vars()
    oauth = OAuth(vars["oauth_token"], vars["token_secret"], vars["consumer_key"], vars["consumer_secret"])

    # intialize things
    twitter = Twitter(domain='api.twitter.com',
                      auth=oauth,
                      api_version='1.1')
    if tweet_id is not None:
        return twitter.statuses.show(id=tweet_id)
    else:
        return twitter.statuses.user_timeline(screen_name="everyword")


def grab_all_the_things():
    # oh hai redis
    db = configs.get_redis_conn()

    print ("--------------------------------------")

    # teh twitter
    updates = grab_twitter_updates()
    lastUpdate = updates[0]
    timestampstring = lastUpdate["created_at"] + ' UTC'
    timestamp = time.mktime(time.strptime(timestampstring,  '%a  %b %d %H:%M:%S +0000 %Y %Z'))
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

        saved = save_tweet(lastUpdate)
        print 'saved!'

        tweeted = tweet_tweet(lastUpdate)
        print 'tweeted!'

        redis_cleanup.trim_redis_keys()
        print 'cleaned!'

        return tweeted, saved


def save_tweet(lastUpdate):
    # set up the DB
    db = configs.get_redis_conn()

    # save the tweet!
    db.set(("tweets:%s" % lastUpdate["id"]), json.dumps(lastUpdate))
    db.lpush("tweets:tweet_ids", lastUpdate["id"])
    return "Tweet \"%s\"saved at %s" % (lastUpdate["text"], datetime.datetime.now())


def tweet_tweet(lastUpdate):
    # work out the definition
    print("defining %s..." % lastUpdate['text'])

    # define things
    definition_data = word_grabber.define_word(lastUpdate['text'])

    if definition_data is not None:

        word = lastUpdate['text']
        short_def = tweet_shortener.shorten_definition(lastUpdate['text'], definition_data['definitions'][0])

        # set up the link
        link = 'http://defineeveryword.heroku.com/%s' % lastUpdate["id"]

        # set up the tweet string
        tweet_string = "%s: %s %s" % (lastUpdate["text"], short_def, link)
        print "tweeting: %s" % tweet_string

        # get the vars
        vars = configs.get_twitter_vars()
        tweet_attempt = tweet_sender.send_tweet(word, tweet_string, vars["consumer_key"], vars["consumer_secret"], vars["oauth_token"], vars["token_secret"])
        return tweet_attempt
    else:
        return "nothing to tweet =("


if __name__ == "__main__":
    grab_all_the_things()
