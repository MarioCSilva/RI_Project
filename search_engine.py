from collections import defaultdict
import os
import gzip
import sys
import logging
import time


class Search_Engine:
	def __init__(self, indexer_dir):
		start_search_time = time.time()

		self.INDEXER_DIR = f"./{indexer_dir}/indexer_dict/"

		self.indexer = defaultdict(int)

		self.load_indexer()
		
		end_search_time = time.time()
		total_search_time = end_search_time -start_search_time

		self.get_statistics(total_search_time)

		self.search_text()


	def get_statistics(self, total_search_time):
		logging.info(f"e) Amount of time taken to start up an index searcher, after the final index is written to disk: {total_search_time} seconds")


	""" Load indexer data structure into memory """
	def load_indexer(self):
		indexer_dir = os.listdir(self.INDEXER_DIR)
		if len(indexer_dir) < 0:
			return

		indexer_file = gzip.open(f"{self.INDEXER_DIR}indexer.txt.gz", 'rt')

		for line in indexer_file:
			indexer_line = line[:-1].split('  ')
			term, freq = indexer_line[0], indexer_line[1]
			self.indexer[term] = freq

	def search_text(self):
		while True:
			query = input("Search for anything (q to quit): ")
			
			if query == "q":
				sys.exit()