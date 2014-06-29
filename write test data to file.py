#!/usr/local/bin/python
# coding: UTF-8
from hyphen import Hyphenator, dict_info
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import csv
import os

x = []

class listenr(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def on_data(self, data):
        # print data
        x.append(data)
        return True
        
    def on_error(self, status):
        print status

CONS_KEY = os.environ.get('AH_CONS_KEY')
CONS_SECRET = os.environ.get('AH_CONS_SECRET')
AXS_TKN = os.environ.get('AH_AXS_TKN')
AXS_TKN_SECRET = os.environ.get('AH_AXS_TKN_SECRET')

auth = OAuthHandler(CONS_KEY, CONS_SECRET)
auth.set_access_token(AXS_TKN, AXS_TKN_SECRET)

stream = Stream(auth, listenr())
stream.filter(track=['Olympics', 'Sochi', 'Putin','Flappy'])

with open('testdata10.txt', 'wb') as f:
	for line in x:
		f.write(line)