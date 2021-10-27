import csv
import re
import nltk
from collections import defaultdict
from nltk.stem import PorterStemmer

tsv_file = open("amazon_reviews.tsv")
reviews_file = csv.reader(tsv_file, delimiter="\n")

# ignore headers
next(reviews_file)

# global variables
STOP_FILTER = False

# regex normalizer
rgx = re.compile("(\w[\w']*\w|\w)")

# white list words
WHITE_LIST = []

# set of stop words
STOP_WORDS = set()
stopwords_file = open("stopwords.txt")
for line in stopwords_file:
	STOP_WORDS |= set(line.split(","))
print(STOP_WORDS)

# porter stemmer
ps = PorterStemmer()

# data structures
indexer = defaultdict(lambda: 0)
postings = defaultdict(lambda: set())

for paragraph in reviews_file:
	paragraph = paragraph[0].lower().split("\t")
	review_id, review_headline, review_body, product_title = \
	paragraph[2], paragraph[-3], paragraph[-2], paragraph[5]
 
	# tokenizer
 	# split into words
	phrase = review_headline + review_body + product_title
	tokens = rgx.findall(phrase)

	tokens_no_sw = [ps.stem(word) for word in tokens if not word in STOP_WORDS]

	for token in tokens_no_sw:
		indexer[token] += 1
		postings[token].add(review_id)