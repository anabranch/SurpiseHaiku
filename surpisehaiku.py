#!/usr/local/bin/python
# coding: UTF-8
from hyphen import Hyphenator, dict_info
import tweepy
import csv
import time
import os
import re
import string
import json
import random

CONS_KEY = os.environ.get('AH_CONS_KEY')
CONS_SECRET = os.environ.get('AH_CONS_SECRET')
AXS_TKN = os.environ.get('AH_AXS_TKN')
AXS_TKN_SECRET = os.environ.get('AH_AXS_TKN_SECRET')
TWEET_FILE = 'testdata10.txt'

def getTweets():
    tweets = []
    with open(TWEET_FILE) as f:
        temp = f.readlines()
        total_lines = len(temp)
        for line in temp:
            try:
                tweets.append(json.loads(line))
            except(ValueError):
                pass
    return tweets

class listenr(tweepy.StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def on_data(self, data):
        print data
        return True
        
    def on_error(self, status):
        print status

class HyphenatorDictionary(object):
    """docstring for HyphenatorDictionary"""    
    def __init__(self):
        self._syl_dict = {}
        # self.addWord('a', 1)

    def digest(self, unsplit_word):
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

    def loadDict(self, filename):
        """
        Loads a syllable dictionary that is seperated by "-" or by "bullets"
        """
        with open(filename) as f: #open our hyphenator dictionary
            ls = csv.reader(f) 
            for _string in ls:
                word, syllables = self.digest(_string[0].decode('UTF-8'))
                self.addWord(word, syllables)

    def addWord(self, word, syllables):
        """
        adds a word to the in memory dictionary, this is not permanent
        """
        if word not in self._syl_dict:
            self._syl_dict[word] = syllables
        # else:
            # if self._syl_dict[word] != syllables:
            #     print("%s => Current: %i :: New: %i" 
            #         % (word, self._syl_dict[word], syllables))
                

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
    Conforms to the same return type as the HyphenatorDictionary
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
    """
    def __init__(self):
        self.h_dict = HyphenatorDictionary()
        self.h_algo = HyphenatorAlgorithm()
        self.h_dict.loadDict('dictionary files/mhyph-utf8.txt')
        
    def evaluateWord(self, word):
        """
        Evaluate word takes in one word and returns a tuple of 
        the syllable count from our dictionary and our algorithm
        """
        # print word, self.h_dict.syllables(word), self.h_algo.syllables(word)
        return self.h_dict.syllables(word), self.h_algo.syllables(word)

    def stripRetweet(self, _string):
        """
        If a tweet starts with RT, it's a retweet. We want to strips the beginning
        returns original string minus RT : 
        """
        if _string.startswith("RT"):
            _string = _string[_string.index(":")+1:]
        return _string

    def cleanWord(self, word):
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

    def cleanString(self, _string):
        """
        Cleans up our strings by stripping retweets and cleaning each word in the tweet
        """
        word_value_tuples = []

        raw_word_list = self.stripRetweet(_string).replace('\n',' ').replace('-',' ').split(" ")
        raw_word_list = [word for word in raw_word_list if word != '' and len(word) < 100]

        for word in raw_word_list:
            w = self.cleanWord(word)
            if w:
                dic, alg = self.evaluateWord(unicode(w.lower()))
                if dic != 0:
                    word_value_tuples.append((w, dic, alg, dic))
                else:
                    word_value_tuples.append((w, dic, alg, alg))

        return word_value_tuples

    def checkUserMentions(self, tweet, _string):
        mntns = tweet['entities']['user_mentions']
        for mtn in mntns:
            if self.cleanWord(mtn['screen_name']) in _string:
                return False
        return True

    def evaluateString(self, _string):
        """
        Evaluates a string by splitting it then passing along the unicode to
        the evaluate word method. It then returns a tuple of the mix, the dictionary's
        calculation and our algorithm's calculation
        """

        word_val_list = self.cleanString(_string)
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
        self.auth = tweepy.OAuthHandler(CONS_KEY, CONS_SECRET)
        self.auth.set_access_token(AXS_TKN, AXS_TKN_SECRET)
        self.twitter = tweepy.API(self.auth)

    def tweetLengthCheck(self, user_name, tweet_id, haiku):
        p1, p2, p3 = haiku
        tweet = "A #haiku: https://twitter.com/%s/status/%s\n\n%s\n%s\n%s" % (user_name, tweet_id, p1, p2, p3)
        return tweet

    def tweet(self, _string):
        sleeptime1 = random.random()
        sleeptime2 = random.randint(0,50)
        print "Sleeping for " + str(sleeptime1 + sleeptime2)
        time.sleep(sleeptime1 + sleeptime2)
        self.twitter.update_status("%s" % (_string))

    def startTweet(self):
        self.tweet("%i tweets processed. No longer mentioning users. Version 0.5 of SurpiseHaiku")

    def debugTweet(self, tweet, to_tweet, word_val_list):
        template = "{0:30}{1:5}{2:5}{3:5}"
        print tweet['text']
        print tweet['user']['screen_name']
        print to_tweet
        print len(to_tweet)
        print template.format("    ", '   DIC', '  ALG', '  Best')
        for count, val in enumerate(word_val_list):
            print template.format(*val)


def evaluate(post=False, version_post=False, count=200):
    evaluator = Evaluator()
    tweets = getTweets()
    tw = TwitterWrap()

    print "%i tweets processed" % (len(tweets))

    if count == -1:
        count = len(tweets)

    for tweet in tweets:
        haiku, breaks, word_val_list = evaluator.evaluateString(tweet['text'])
        # print tweet['entities']

        if haiku and tweet['lang'] == 'en':
            words = [_x[0] for _x in word_val_list]

            p1 = " ".join(words[:breaks[0]+1])
            p2 = " ".join(words[breaks[0]+1:breaks[1]+1])
            p3 = " ".join(words[breaks[1]+1:breaks[2]+1])

            # print evaluator.checkUserMentions(tweet, p1+" "+p2+" "+p3)
            if evaluator.checkUserMentions(tweet, p1+" "+p2+" "+p3):
                to_tweet = tw.tweetLengthCheck(tweet['user']['screen_name'], tweet['id'], (p1,p2,p3))
                tw.debugTweet(tweet, to_tweet, word_val_list)
                if post:
                    tw.tweet(to_tweet)
        if count == 0:
            break
        count -= 1
    
def main():
    # switch these to run tests
   # evaluate()
   evaluate(True, True, -1)


if __name__ == '__main__':
    main()

#could be good to convert numbers to their names...check downloads or package py2num
# could be good to throw a random user mention in there...for the really goods ones???
