from collections import defaultdict
import re
from nltk.stem.snowball import SnowballStemmer

'''
i.A minimum length filterthat removes tokens with less than a defaultnumber of characters.
Allow the user to disable the filter or set another value;
ii.A stopword filter using a default list.Allow the user to disable the filter or use a different list;
iii.Porter stemmer (from snowball or NLTK). Allow the user to disable the filter
'''

class Tokenizer:
    def __init__(self, min_length_filter=False, min_length=3,\
            porter_filter=False, stop_words_filter=False, stopwords_file="stopwords.txt"):

        self.porter_filter = porter_filter
        self.min_length_filter = min_length_filter
        self.stop_words_filter = stop_words_filter
        # Longest word in the English language featuring alternating consonants and vowels
        # and longest word word in Shakespeare's works has size 27
        self.max_length = 27
        
        # initialize Stop Words and Porter Filter if needed
        self.init_min_len_filter(length=min_length)
        self.init_porter_filter()
        self.init_stop_words_filter(stopwords_file=stopwords_file)
    

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


    @staticmethod
    def simple_tokenize(input_string):
        tokens = input_string.split()
        
        tokens = [re.sub("[^0-9a-z]+"," ", token.lower()).split() for token in tokens]
        tokens = [token for sublist in tokens for token in sublist if not token.isdigit()]

        return tokens


    def tokenize(self, input_string) -> list():
        final_tokens = defaultdict(list)

        tokens = input_string.split()
        
        tokens = [re.sub("[^0-9a-z]+"," ", token.lower()).split() for token in tokens]
        tokens = [token for sublist in tokens for token in sublist if not token.isdigit()]

        for index, token in enumerate(tokens):
            token_size = len(token)
            if (not self.min_length_filter or token_size >= self.min_length) \
                and token_size <= self.max_length \
                and (not self.stop_words_filter or token not in self.stop_words):
                    if self.porter_filter:
                        final_tokens[self.ps.stem(token)].append(index)
                    else:
                        final_tokens[token].append(index)
        return final_tokens
