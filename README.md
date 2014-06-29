#SurpriseHaiku

SurpriseHaiku was an experiment that parsed random twitter tweets to see if they followed the Haiku cadence of 5 / 7 / 5. I ran this experiment during the 2014 Olympics to try and focus around Olympic related tweets.

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
   

## How it Works
Surprise Haiku will listen to the twitter firehose for a random set amount of time. As of now this is a manual operation that has to be explicitly stopped. Once stopped it writes this information to a file. I then run the *surprisehaiku.py* file which looks at whether or not a tweet is a Haiku. If it is it will tweet the Haiku along with the line splits. Some examples:



###Method for identifying a Haiku

Identifying the syllabyles on the English language is tough. We've got a lot of different ways of pronouncing things. Our application loads a dictionary of syllabic breaks along with words. Then we start analyzing tweets by normalizing the text, removing capitalization, and other punctuation. From there we iterate through each word to see if it is in the dictionary, we then test what our "PyHyphen" hyphenator returns the value to be. 

Once we get our values (nearly instantly), we compare them and spit out the like breaks and word values. If it's a Haiku and we have the correct cadence (and the cadence ends at the end of a word) then we tweet the result.

###To Do/Improvements

* Add in some more natural language processing so that Haikus have to end with certain parts of speech
* Automate this so that it could be deployed to a server/doesn't have to be run manually
* Automate adding to dictionary
* Reporting mechanism for validation
* Add plurals to dictionary
* Better dictionary than just in memory