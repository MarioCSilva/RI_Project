from collections import defaultdict
import os
import gzip
import sys
import logging
from tokenizer import Tokenizer
from functools import lru_cache
from math import log10, sqrt
import time


class Search_Engine:
	def __init__(self, index_dir, queries_file):
		start_search_time = time.time()

		self.INDEX_DIR = f"../{index_dir}"
		self.INDEXER_DIR = f"{self.INDEX_DIR}/indexer_dict/"
		self.PARTITION_DIR = f"{self.INDEX_DIR}/partition_index/"
		self.CONFIG_DIR = f"{self.INDEX_DIR}/config/"

		self.QUERY_DIR = f"{self.INDEX_DIR}/queries_results/"

		self.check_dir_exist(self.QUERY_DIR)

		self.indexer = defaultdict(lambda: [0, 0])

		self.store_positions = False

		self.tokenizer = self.read_config()

		self.queries_file = queries_file

		self.load_indexer()
		
		total_search_time = time.time() -start_search_time

		self.get_statistics(total_search_time)

		self.search_queries()


	def check_dir_exist(self, directory):
		if not os.path.exists(directory):
			os.mkdir(directory)


	def get_statistics(self, total_search_time):
		logging.info(f"e) Amount of time taken to start up an index searcher, after the final index is written to disk: {total_search_time} seconds")


	""" Load configurations used during indexation """
	def read_config(self):
		tokenizer = Tokenizer()
		try:
			config_dir = os.listdir(self.CONFIG_DIR)
			if len(config_dir) < 0:
				return
			config_file = gzip.open(f"{self.CONFIG_DIR}config.txt.gz",'rt')
		except FileNotFoundError as e:
			logging.error("Could not find configurations file on disk. Please run the indexer first.")
			sys.exit(0)

		for line in config_file:
			config = line[:-1].split('  ')
			#config = line[:-1].split(':')
			if config[0] == "store_positions":
				self.store_positions = True
			elif config[0] == "min_length_filter":
				tokenizer.min_length_filter = True
				tokenizer.init_min_len_filter(int(config[1]))
			elif config[0] == "porter_filter":
				tokenizer.porter_filter = True
				tokenizer.init_porter_filter()
			elif config[0] == "stop_words_filter":
				tokenizer.stop_words_filter = True
			elif config[0] == "stop_words_file":
				stop_words_file = config[1]
				tokenizer.init_stop_words_filter(stop_words_file)

		return tokenizer


	""" Load indexer data structure into memory """
	def load_indexer(self):
		try:
			indexer_dir = os.listdir(self.INDEXER_DIR)
			if len(indexer_dir) < 0:
				return
			indexer_file = gzip.open(f"{self.INDEXER_DIR}indexer.txt.gz", 'rt')
		except FileNotFoundError as e:
			logging.error("Could not find indexer on disk. Please run the indexer first.")
			sys.exit(0)

		for line in indexer_file:
			indexer_line = line[:-1].split(';')
			term = indexer_line[0]
			self.indexer[term][0], self.indexer[term][1] = \
				int(indexer_line[1]), int(indexer_line[2])


	def get_partition_file(self, term):
		for file in os.listdir(self.PARTITION_DIR):
			first_term, last_term = file.split('.')[0].split(' ')
			if term >= first_term and term <= last_term:
				return f"{self.PARTITION_DIR}{file}"


	def read_file_line(self, file, line):
		for i, x in enumerate(file):
			if i == line:
				return x[:-1]


	@lru_cache(maxsize=50)
	def search_term(self, term):
		doc_freq, partition_line = self.indexer[term]
		idf = 0.0
		doc_weights = {}

		if doc_freq:
			partition_file = self.get_partition_file(term)
			logging.info(f"Postings of '{term}' are indexed in the partition file '{partition_file}'")

			try:
				partition_file = gzip.open(partition_file, 'rt')
			except FileNotFoundError as e:
				logging.error("Could not find partition on disk.")
				return 0, 0

			term_idf_postings = self.read_file_line(partition_file, partition_line).split(';')

			idf, postings_str = float(term_idf_postings[0]), term_idf_postings[1:]

			for doc_weight_str in postings_str:
				doc_weight_lst = doc_weight_str.split(':')
				doc, weight = doc_weight_lst[0], float(doc_weight_lst[1])
				doc_weights[doc] = weight

			partition_file.close()

		return doc_freq, idf, doc_weights


	def handle_query(self, query):
		use_idf = True

		scores = defaultdict(lambda: 0)

		tokenized_query = self.tokenizer.tokenize(query)

		if len(tokenized_query) == 1:
			use_idf = False

		cos_norm_value = 0
		for term, positions in tokenized_query.items():
			doc_freq, idf, doc_weights = self.search_term(term)
			
			if not doc_freq:
				print(f"Term '{term}' not indexed.")
				continue
			
			l = 1 + log10(len(positions))
			weight = l
			if not use_idf:
				weight *= idf

			cos_norm_value += weight ** 2

			for doc, doc_weight in doc_weights.items():
				scores[doc] += doc_weight * weight

			print(f"IDF of '{term}': {idf}")
			print(f"Document Frequency of '{term}': {doc_freq}")

		if cos_norm_value:
			cos_norm_value = 1 / sqrt(cos_norm_value)

			for doc in scores.keys():
				scores[doc] *= cos_norm_value
		
		return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:100]


	def write_results_to_file(self, query_index, results_query):
		with open(f"{self.QUERY_DIR}query_{query_index}", 'w+') as f:
			output = '\n'.join(results_query)
			f.write(f"{output}")


	def search_queries(self):
		try:
			queries_file = open(self.queries_file, "r")
		except FileNotFoundError:
			logging.info("File for queries not found.")
			sys.exit()

		for index, query in enumerate(queries_file):
			results_query = self.handle_query(query)
			
			self.write_results_to_file(index, results_query)