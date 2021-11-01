import re
from nltk.stem.snowball import SnowballStemmer
import logging

'''
i.A minimum length filterthat removes tokens with less than a defaultnumber of characters.
Allow the user todisable the filter orset another value;
ii.A stopword filterusinga default list.Allow the user to disable the filter or usea different list;
iii.Porter stemmer (from snowball or NLTK). Allow the user to disable the filter
'''

class Tokenizer:
    def __init__(self, min_length_filter=False, min_length=3,\
            porter_filter=False, stop_words_filter=False, stopwords_file="stopwords.txt"):

        self.porter_filter = porter_filter
        self.min_length_filter = min_length_filter
        self.stop_words_filter = stop_words_filter
        
        # initialize Stop Words and Porter Filter if needed
        self.init_min_len_filter(length=min_length)
        self.init_porter_filter()
        self.init_stop_words_filter(stopwords_file=stopwords_file)

        # regex normalizer
        self.rgx = re.compile("(\w[\w']*\w|\w)")


    def init_min_len_filter(self, length):
        if self.min_length_filter:
            if length <= 0:
                raise ValueError("Cannot use minimum length filter for a length inferior to 1")
            self.min_length = length


    def init_porter_filter(self):
        if self.porter_filter:
            self.ps = SnowballStemmer("english", ignore_stopwords=True)


    def init_stop_words_filter(self, stopwords_file):
        if self.stop_words_filter:
            self.stop_words = set()
            with open(stopwords_file, 'r') as stop_words_file:
                for line in stop_words_file:
                    self.stop_words |= set(line.split(","))


    def tokenize(self, input_string) -> list():
        # TODO: ver isto melhor
        input_normalized = re.sub("[^0-9a-zA-Z'_-]+"," ", input_string).lower()
        tokens = self.rgx.findall(input_string)

        if self.porter_filter:
            return [
                self.ps.stem(word) for word in tokens
                if (not self.min_length_filter or len(word) >= self.min_length)
                and (not self.stop_words_filter or word not in self.stop_words)
            ]

        return [
                word for word in tokens \
                if (not self.min_length_filter or len(word) >= self.min_length)
                and (not self.stop_words_filter or word not in self.stop_words)
            ]

