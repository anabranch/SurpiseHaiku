#!/usr/local/bin/python
# coding: UTF-8
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream, API
from hyphen import Hyphenator, dict_info
from threading import Thread
from time import sleep
import os
import csv
import sys
import re
import string
import json
import random

TWEETS = []
########
# Enter your twitter credentials here
CONS_KEY = os.environ.get('AH_CONS_KEY') # consumer key
CONS_SECRET = os.environ.get('AH_CONS_SECRET') # consumer secret
AXS_TKN = os.environ.get('AH_AXS_TKN') # access token
AXS_TKN_SECRET = os.environ.get('AH_AXS_TKN_SECRET') # access token secret
TWEET_FILE = 'data.txt'
#########

class listenr(StreamListener):
    """ A listener handles TWEETS are the received from the stream.
    This is a basic listener that just prints received TWEETS to stdout.

    """
    def on_data(self, data):
        # print data
        TWEETS.append(data)
        return True
        
    def on_error(self, status):
        print status

class HyphenatorDictionary(object):
    """
    This class wraps and builds our dictionary
    of words. It provides simple methods for us
    to retrieve relevant information from the dictionary
    (the hyphenated version if it exists)
    """    
    def __init__(self):
        self._syl_dict = {}

    def load_dict(self, filename):
        """
        Loads a syllable dictionary that is seperated by "-" or by "bullets"
        """
        with open(filename) as f: #open our hyphenator dictionary
            ls = csv.reader(f) 
            for _string in ls:
                word, syllables = self._split_word(_string[0].decode('UTF-8'))
                self.add_word(word, syllables)

    def add_word(self, word, syllables):
        """
        adds a word to the in memory dictionary, this is not permanent
        """
        if word not in self._syl_dict:
            self._syl_dict[word] = syllables
        # else:
            # if self._syl_dict[word] != syllables:
            #     print("%s => Current: %i :: New: %i" 
            #         % (word, self._syl_dict[word], syllables))
                
    def _split_word(self, unsplit_word):
        """This will take an unsplit word and 
        return the word and number of syllables
        from our hyphenation dictionary"""

        if u"•" in unsplit_word and "-" not in unsplit_word: 
            splitted_word = unsplit_word.split(u"•")
            return u"".join(splitted_word), len(splitted_word)
        elif u"•" not in unsplit_word and "-" in unsplit_word:
            splitted_word = unsplit_word.split(u"-")
            return u"".join(splitted_word), len(splitted_word)
        else:
            return unsplit_word, 1

        unsplit_word.split()
                
    def syllables(self, word):
        """
        Searches for the word in our dictionary, if it's there returns number
        of syllables, if not returns False
        """
        if word in self._syl_dict:
            return self._syl_dict[word]
        else:
            return 0

class HyphenatorAlgorithm(object):
    """
    This is a small wrapper on the Hyphenator method from our Hyphen import.
    Conforms to the same return type as the HyphenatorDictionary class
    """
    def __init__(self):
        """
        Initialize the class
        """
        self._hyphenator = Hyphenator('en_US')

    def syllables(self, word):
        """
        Calculates the number of syllables, if it tries to return 0 it returns 1.
        All words should count as a syllable
        """
        syll = self._hyphenator.syllables(unicode(word))
        length = len(syll)

        if length != 0:
            return length
        else:
            return 1

class Evaluator(object):
    """
    Our Evaluator allows us to evaluate an individual word or a string of words
    to get the syllable count. It does this by first looking in the dictionary,
    if it finds nothing it uses the hyphenator algorithm to try and get a response
    """
    def __init__(self):
        self.h_dict = HyphenatorDictionary()
        self.h_algo = HyphenatorAlgorithm()
        self.h_dict.load_dict('dictionary files/mhyph-utf8.txt')
        
    def evaluate_word(self, word):
        """
        Evaluate word takes in one word and returns a tuple of 
        the syllable count from our dictionary and our algorithm
        """
        # print word, self.h_dict.syllables(word), self.h_algo.syllables(word)
        return self.h_dict.syllables(word), self.h_algo.syllables(word)

    def strip_retweet(self, _string):
        """
        If a tweet starts with RT, it's a retweet. We want to strips the beginning
        returns original string minus RT : 
        """
        if _string.startswith("RT"):
            _string = _string[_string.index(":")+1:]
        return _string

    def clean_word(self, word):
        """
        Cleans a word by:
         - Stripping symbols
         - converting ascii
         - stripping new line formatting

         We currently do the following but 
         should figure out a better way to handle it
         - removing user mentions
         - removing links 

        """
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        word = word.encode('ascii', 'ignore')
        word = regex.sub('', word)
        if word.startswith("@"):
            return ""
        elif word.startswith("http"):
            return ""
        else:
            return word

    def clean_string(self, _string):
        """
        Cleans up our strings by stripping retweets and cleaning each word in the tweet
        """
        word_value_tuples = []

        raw_word_list = self.strip_retweet(_string).replace('\n',' ').replace('-',' ').split(" ")
        raw_word_list = [word for word in raw_word_list if word != '' and len(word) < 100]

        for word in raw_word_list:
            w = self.clean_word(word)
            if w:
                dic, alg = self.evaluate_word(unicode(w.lower()))
                if dic != 0:
                    word_value_tuples.append((w, dic, alg, dic))
                else:
                    word_value_tuples.append((w, dic, alg, alg))

        return word_value_tuples

    def check_user_mentions(self, tweet, _string):
        """
        Checks whether or not there is a user mention.
        returns True or False
        """
        mntns = tweet['entities']['user_mentions']
        for mtn in mntns:
            if self.clean_word(mtn['screen_name']) in _string:
                return False
        return True

    def evaluate_string(self, _string):
        """
        Evaluates a string by splitting it then passing along the unicode to
        the evaluate word method. It then returns a tuple of the mix, the dictionary's
        calculation and our algorithm's calculation for further comparison
        """

        word_val_list = self.clean_string(_string)
        mixed = [x[3] for x in word_val_list]

        temp = 0
        break_1 = 0
        break_2 = 0
        break_3 = 0

        for count, val in enumerate(mixed):
            temp += val
            if temp == 5 and break_1 == 0:
                temp = 0
                break_1 = count

            elif temp == 7 and break_1 != 0 and break_2 == 0:
                temp = 0
                break_2 = count

            elif temp == 5 and break_1 != 0 and break_2 != 0 and break_3 == 0:
                break_3 = count
                break

        breaks = (break_1, break_2, break_3)
        if break_1 and break_2 and break_3:
            return True, breaks, word_val_list
        else:
            return False, breaks, word_val_list

class TwitterWrap(object):
    def __init__(self):
        self.auth = OAuthHandler(CONS_KEY, CONS_SECRET)
        self.auth.set_access_token(AXS_TKN, AXS_TKN_SECRET)
        self.twitter = API(self.auth)

    def tweet_length_check(self, user_name, tweet_id, haiku):
        """"
        Makes sure our tweet length is short enough for twitter
        """
        p1, p2, p3 = haiku
        tweet = "A #haiku: https://twitter.com/%s/status/%s\n\n%s\n%s\n%s" % (user_name, tweet_id, p1, p2, p3)
        return tweet

    def tweet(self, _string):
        """Updates the status of the twitter user, then sleeps for a random 
        amount of time to avoid getting blocked by the API"""
        sleeptime1 = random.random()
        sleeptime2 = random.randint(0,50)
        print "Sleeping for " + str(sleeptime1 + sleeptime2)
        sleep(sleeptime1 + sleeptime2)
        self.twitter.update_status("%s" % (_string))

    def debug_tweet(self, tweet, to_tweet, word_val_list):
        """Prints out the information about a tweet"""
        template = "{0:30}{1:5}{2:5}{3:5}"
        print "ORIGINAL TWEET::"
        print tweet['text']
        print "BY::"
        print tweet['user']['screen_name']
        print "PARSED VERSION::"
        print to_tweet
        print "length %i" % len(to_tweet)
        print "Number of syllables in each word in the tweet..."
        print template.format("    ", '   DIC', '  ALG', '  Best')
        for count, val in enumerate(word_val_list):
            print template.format(*val)

def post_to_twitter(tweets, count=200):
    """Takes in a list of tweets then posts to twitter the ones that are good tweets
    """
    evaluator = Evaluator()
    tw = TwitterWrap()
    tweets = [json.loads(tweet) for tweet in tweets]
    print "%i tweets processed" % (len(tweets))

    if count == -1:
        count = len(tweets)

    for tweet in tweets:
        print tweet
        haiku, breaks, word_val_list = evaluator.evaluate_string(tweet['text'])
        # print tweet['entities']

        if haiku and tweet['lang'] == 'en':
            words = [_x[0] for _x in word_val_list]

            p1 = " ".join(words[:breaks[0]+1])
            p2 = " ".join(words[breaks[0]+1:breaks[1]+1])
            p3 = " ".join(words[breaks[1]+1:breaks[2]+1])

            # print evaluator.check_user_mentions(tweet, p1+" "+p2+" "+p3)
            if evaluator.check_user_mentions(tweet, p1+" "+p2+" "+p3):
                to_tweet = tw.tweet_length_check(tweet['user']['screen_name'], tweet['id'], (p1,p2,p3))
                tw.debug_tweet(tweet, to_tweet, word_val_list)
                tw.tweet(to_tweet)
        if count == 0:
            break
        count -= 1

def print_to_std_out(tweets, count=200):
    """Takes in a list of tweets then prints to stdout the ones
    that qualify as tweets
    """
    evaluator = Evaluator()
    tw = TwitterWrap()
    tweets = [json.loads(tweet) for tweet in tweets]
    print "%i tweets processed" % (len(tweets))

    if count == -1:
        count = len(tweets)

    for tweet in tweets:
        haiku, breaks, word_val_list = evaluator.evaluate_string(tweet['text'])
        # print tweet['entities']

        if haiku and tweet['lang'] == 'en':
            words = [_x[0] for _x in word_val_list]

            p1 = " ".join(words[:breaks[0]+1])
            p2 = " ".join(words[breaks[0]+1:breaks[1]+1])
            p3 = " ".join(words[breaks[1]+1:breaks[2]+1])

            # print evaluator.check_user_mentions(tweet, p1+" "+p2+" "+p3)
            if evaluator.check_user_mentions(tweet, p1+" "+p2+" "+p3):
                to_tweet = tw.tweet_length_check(tweet['user']['screen_name'], tweet['id'], (p1,p2,p3))
                tw.debug_tweet(tweet, to_tweet, word_val_list)
        if count == 0:
            break
        count -= 1

auth = OAuthHandler(CONS_KEY, CONS_SECRET)  
auth.set_access_token(AXS_TKN, AXS_TKN_SECRET)
stream = Stream(auth, listenr())

def download_tweets():
    # We have to create the above in order for this to know what to do with stream,
    # this is a side effect and probably could be done better.
    stream.filter(track=['World Cup', 'Brazil', 'WorldCup'])

    
def main():
    print "Creating Thread to Download Tweets..."
    th = Thread(target=download_tweets)
    th.daemon = True
    th.start()
    print "Thread created, now sleeping for 30 seconds..."
    sleep(15)
    print "15 seconds is up, waiting another 15 seconds..."
    sleep(15)
    print_to_std_out(TWEETS)


if __name__ == '__main__':
    # print sys.argv
    # for parsing command line args
    main()
