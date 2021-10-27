import csv
import re
import nltk
from collections import defaultdict
from tokenizer import Tokenizer


class Indexer:
	def __init__(self, file_name="amazon_reviews.tsv"):
		self.file_name = file_name

		# data structures
		self.indexer = defaultdict(lambda: 0)
		self.postings = defaultdict(lambda: set())

		# init tokenizer
		self.tokenizer = Tokenizer()

		STOP_FILTER = False
	
	def file_parsing(self):
		tsv_file = open(self.file_name)
		reviews_file = csv.reader(tsv_file, delimiter="\n")
		# ignore headers
		next(reviews_file)

		for paragraph in reviews_file:
			print("as")
			paragraph = paragraph[0].split("\t")
			review_id, review_headline, review_body, product_title = \
			paragraph[2], paragraph[-3], paragraph[-2], paragraph[5]
		
			input_string = review_headline + review_body + product_title

			tokens = self.tokenizer.tokenize(input_string)

			for token in tokens:
				self.indexer[token] += 1
				self.postings[token].add(review_id)
		
	def print_indexer(self):
		print(self.indexer)
	
	def print_postings(self):
		print(self.postings)

if __name__ == "__main__":
	indexer = Indexer()
	print("here -")
	indexer.file_parsing()
	print("here -")
