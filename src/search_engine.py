from collections import defaultdict
import os
import gzip
import sys
import logging
import time
from tokenizer import Tokenizer
from functools import lru_cache


class Search_Engine:
	def __init__(self, index_dir):
		start_search_time = time.time()

		self.INDEX_DIR = f"../{index_dir}"
		self.INDEXER_DIR = f"{self.INDEX_DIR}/indexer_dict/"
		self.PARTITION_DIR = f"{self.INDEX_DIR}/partition_index/"
		self.CONFIG_DIR = f"{self.INDEX_DIR}/config/"

		self.indexer = defaultdict(lambda: [0, 0])

		self.store_positions = False

		self.tokenizer = self.read_config()

		self.load_indexer()
		
		end_search_time = time.time()
		total_search_time = end_search_time -start_search_time

		self.get_statistics(total_search_time)

		self.search_text()


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
		num_occ, partition_line = self.indexer[term]
		postings = []
		idf = 0

		if num_occ:
			partition_file = self.get_partition_file(term)
			logging.info(f"Postings of '{term}' are indexed in the partition file '{partition_file}'")

			try:
				partition_file = gzip.open(partition_file, 'rt')
			except FileNotFoundError as e:
				logging.error("Could not find partition on disk.")
				return 0, 0

			term_idf_postings = self.read_file_line(partition_file, partition_line).split(';')

			idf, postings_str = term_idf_postings[0], term_idf_postings[1:]

			for doc in postings_str:
				postings.append(doc)

			partition_file.close()

		return num_occ, idf, postings


	def handle_query(self, query):
		for term in self.tokenizer.tokenize(query).keys():
			num_occ, idf, postings = self.search_term(term)
			if not num_occ:
				print(f"Term '{term}' not indexed.")
				continue
			print(f"IDF of '{term}': {idf}")
			print(f"Number of Occurrences of '{term}': {num_occ}")
			print(f"Posting List of '{term}': {postings}")


	def search_text(self):
		while True:
			query = input("Search for anything (q to quit): ")

			if query == "q":
				sys.exit()

			self.handle_query(query)
