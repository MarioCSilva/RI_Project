import re
from nltk.stem.snowball import SnowballStemmer


class Tokenizer:
    def __init__(self, stopwords_file="stopwords.txt"):
        # porter stemmer
        self.ps = SnowballStemmer("english", ignore_stopwords=True)

        # stop words
        self.STOP_WORDS_FILE = stopwords_file
        self.STOP_WORDS = set()
        self.stopwords_file = open(self.STOP_WORDS_FILE, 'r')

        for line in stopwords_file:
            self.STOP_WORDS |= set(line.split(","))
        
        # regex normalizer
        self.rgx = re.compile("(\w[\w']*\w|\w)")

    def tokenize(self, input_string):
        # TODO: ver isto melhor
        input_normalized = re.sub("[^0-9a-zA-Z'_-]+"," ", input_string).lower()
        tokens = self.rgx.findall(input_string)

        # TODO: ver melhor tb palavras comuns e maior q 2
        tokens = [ self.ps.stem(word) for word in tokens if len(word) > 2 and word not in self.STOP_WORDS]
        
        return tokens