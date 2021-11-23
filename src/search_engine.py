from collections import defaultdict
import os
import gzip
import sys
import logging
import time


class Search_Engine:
	def __init__(self, index_dir):
		start_search_time = time.time()

		self.INDEX_DIR = f"../{index_dir}"
		self.INDEXER_DIR = f"{self.INDEX_DIR}/indexer_dict/"
		self.PARTITION_DIR = f"{self.INDEX_DIR}/partition_index/"

		self.indexer = defaultdict(lambda: [0, 0])

		self.load_indexer()
		
		end_search_time = time.time()
		total_search_time = end_search_time -start_search_time

		self.get_statistics(total_search_time)

		self.search_text()


	def get_statistics(self, total_search_time):
		logging.info(f"e) Amount of time taken to start up an index searcher, after the final index is written to disk: {total_search_time} seconds")


	""" Load indexer data structure into memory """
	def load_indexer(self):
		try:
			indexer_dir = os.listdir(self.INDEXER_DIR)
			if len(indexer_dir) < 0:
				return
			indexer_file = gzip.open(f"{self.INDEXER_DIR}indexer.txt.gz", 'rt')
		except FileNotFoundError as e:
			logging.error("Could not Find Indexer on disk. Please Run the Indexer first.")
			sys.exit(0)
		for line in indexer_file:
			indexer_line = line[:-1].split('  ')
			term = indexer_line[0]
			self.indexer[term][0], self.indexer[term][1] = \
				indexer_line[1], indexer_line[2]


	def get_partition_file(self, term):
		for file in os.listdir(self.PARTITION_DIR):
			first_term, last_term = file.split('.')[0].split(' ')
			if term >= first_term and term <= last_term:
				logging.info(f"Postings of the term {term} is indexed the partition file {file}")
				return file


	def handle_query(self, query):
		self.get_partition_file(query)
		res = self.indexer[query]
		print(f"Number of Occurrences of {query}: {res[0]}")


	def search_text(self):
		while True:
			query = input("Search for anything (q to quit): ")

			if query == "q":
				sys.exit()

			self.handle_query(query)
