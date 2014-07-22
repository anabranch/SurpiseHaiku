#SurpriseHaiku

SurpriseHaiku was an experiment that parsed random twitter tweets to see if they followed the Haiku cadence of 5 / 7 / 5 (syllables). I ran this experiment during the 2014 Olympics to try and focus around Olympics related tweets.

See: https://twitter.com/surprisehaiku

**Status:** No longer under development

   
## Examples
-----
A #haiku: https://twitter.com/chasedog6/status/432727303148142592 …

Lets Show Why Baseball

Is The Best Sport RT if

you want Baseball back

------
A #haiku: https://twitter.com/heyfrazier/status/432727300325388288 …

every time they 

show putin i get really

uncomfortable


## Dependencies

   * Python
   * [PyHyphen](https://pypi.python.org/pypi/PyHyphen/2.0.5)
   * Tweepy
   * The Project Gutenberg Etext of Moby Hyphenator II by Grady Ward   

##Usage
* Download this repo
* Install dependencies
	* Use either:

----
    pip install pyhyphen
    pip install tweepy
----

or...

----
	pip install -r requirements.txt
----

* [Get yourself a registered twitter app
](https://dev.twitter.com/) then either enter your credentials as environment variables at  line 18 of surprisehaiku.py
* Run it with the below command!

----

    python surprisehaiku.py
   

* Now you wait for 30 seconds as the script gets a list of tweets and then it will print them to the terminal. You can see which words are missing from the dictionary and how the algorithm chooses which hyphenation is best (comparing the dictionary and the hyphenator).

Example:

-----
    ORIGINAL TWEET::
    FOLLOW ME, I LOVE YOU, YOU IS MY LIFE, MY DREAM, I LOVE U, BRAZIL LOVES U @ShawnMendes #LOTPgift @taylorcaniff #TayTo1 x108
    BY::
    z4yumb4e
    PARSED VERSION::
    A #haiku: https://twitter.com/z4yumb4e/status/483482944573816832

    FOLLOW ME I LOVE
    YOU YOU IS MY LIFE MY DREAM
    I LOVE U BRAZIL
    length 126
    Number of syllables in each word in the tweet...
                                     DIC  ALG  Best
    FOLLOW                            2    2    2
    ME                                0    1    1
    I                                 0    1    1
    LOVE                              1    1    1
    YOU                               1    1    1
    YOU                               1    1    1
    IS                                0    1    1
    MY                                0    1    1
    LIFE                              1    1    1
    MY                                0    1    1
    DREAM                             1    1    1
    I                                 0    1    1
    LOVE                              1    1    1
    U                                 0    1    1
    BRAZIL                            2    1    2
    LOVES                             0    1    1
    U                                 0    1    1
    ShawnMendes                       0    2    2
    LOTPgift                          0    1    1
    taylorcaniff                      0    4    4
    TayTo1                            0    1    1
    x108                              0    1    1

It's far from perfect as parsing something like "ShawnMendes" is tough. But overall it does a decent job finding true tweets and printing them out.

## How it Works
Surprise Haiku will listen to the twitter firehose for a random set amount of time. Right now it the "track" or keywords it looks for in tweets in hard coded for the world cup. It will look at those tweets (which are a particularly hard bunch as they include lots of names and countries misspelled) and tries to find a haiku in them. The method for finding a haiku is explained below.


###Method for identifying a Haiku

The simplest explanation is:

* Normalize the tweets text
* Split it by syllable/ each word by syllable
* see if we get a 5/7/5 combination


Identifying the syllabyles on the English language is tough. We've got a lot of different ways of pronouncing things. Our application loads a dictionary of syllabic breaks along with words. Then we start analyzing tweets by normalizing the text, removing capitalization, and other punctuation. From there we iterate through each word to see if it is in the dictionary, we then test what our "PyHyphen" hyphenator returns the value to be. 

Once we get our values (nearly instantly), we compare them and spit out the like breaks and word values. If it's a Haiku and we have the correct cadence (and the cadence ends at the end of a word) then we tweet/print out the result.

###To Do/Improvements

* Add in some more natural language processing so that Haikus have to end with certain parts of speech
* Add in some natural language processing to throw out words with a lot of typos and or words we won't be able to recognize
* Automate this so that it could be deployed to a server/doesn't have to be run manually
* Automate adding to dictionary
* Reporting mechanism for validation
* Add plurals to dictionary
* Better dictionary than just in memory/ maybe a database
* parse command line arguments for time and whether to print them to twitter, etc