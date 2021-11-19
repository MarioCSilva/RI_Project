from collections import defaultdict
import os
import gzip
import sys
import logging
import time


class Search_Engine:
	def __init__(self, indexer_dir):
		start_search_time = time.time()

		self.INDEXER_DIR = f"../{indexer_dir}/indexer_dict/"

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


	def search_text(self):
		while True:
			print(len(self.indexer))
			query = input("Search for anything (q to quit): ")
			if query == "q":
				sys.exit()
			res = self.indexer[query]
			print(f"Number of Occurrences of {query}: {res[0]}")
			