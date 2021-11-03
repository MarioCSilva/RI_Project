import csv
import os
import nltk
from collections import defaultdict
from tokenizer import Tokenizer
import psutil
import logging
import gzip
import time


class Indexer:
	def __init__(self, index_dir, file_name="amazon_reviews.tsv", min_length_filter=False,\
		min_len=None, porter_filter=False, stop_words_filter=False,\
		stopwords_file='stop_words.txt'):
		logging.info(f"Indexer")
		start_index_time = time.time()
		
		self.file_name = file_name

		# data structures
		self.indexer = defaultdict(lambda: 0)
		self.postings = defaultdict(lambda: set())

		# init tokenizer
		self.tokenizer = Tokenizer(min_length_filter, min_len, porter_filter,\
			stop_words_filter, stopwords_file)

		# get process
		self.python_process = psutil.Process(os.getpid())
		# block id
		self.block_id = 0

		self.INDEX_DIR = index_dir
		self.POSTINGS_DIR = f"./{self.INDEX_DIR}/posting_blocks/"
		self.PARTITION_DIR = f"./{self.INDEX_DIR}/partition_index/"
		self.INDEXER_DIR = f"./{self.INDEX_DIR}/indexer_dict/"
		
		dir_list = [self.INDEX_DIR, self.POSTINGS_DIR,\
			self.PARTITION_DIR, self.INDEXER_DIR]
		self.check_dir_exist(dir_list)

		# current number of stored tokens
		self.num_stored_tokens = 0

		# maximum number of tokens's postings stored in memory
		self.MAX_TOKENS_PER_CHUNK = 1000000

		# parse file and then index terms and postings
		self.parse_and_index()

		# merge all block files
		self.merge_blocks()

		# delete all temporary block files
		self.clear_blocks()

		# store indexer data structure in a file
		self.store_indexer()

		end_index_time = time.time()
		total_index_time = end_index_time -start_index_time

		self.get_statistics(total_index_time)


	def get_statistics(self, total_index_time):
		block_files_dir = os.listdir(self.PARTITION_DIR)
		files_size = sum([os.path.getsize(f"{self.PARTITION_DIR}{f}") for  f in block_files_dir])

		logging.info(f"a) Total indexing time: {total_index_time:.5f} seconds")

		logging.info(f"b) Total index size on disk: {files_size:.5f} Bs == {9.5e-07*files_size:.3f} MBs")

		logging.info(f"c) Vocabulary size: {len(self.indexer)}")

		logging.info(f"d) Number of temporary index segments written to disk: {self.block_id}")


	def check_dir_exist(self, directories):
		for diretory in directories:
			if not os.path.exists(diretory):
				os.mkdir(diretory)


	def parse_and_index(self):
		data_set = open(self.file_name)
		reviews_file = csv.reader(data_set, delimiter="\n")
		# ignore headers
		next(reviews_file)

		for paragraph in reviews_file:
			paragraph = paragraph[0].split("\t")
			review_id, review_headline, review_body = \
				paragraph[2], paragraph[-3], paragraph[-2]
		
			input_string = f"{review_headline} {review_body}"

			tokens = self.tokenizer.tokenize(input_string)

			self.index_tokens(document_id=review_id, tokens=tokens)

		data_set.close()

		# last chunk is not being written to disk, thus the function is called again
		if self.postings:
			self.block_write_setup()


	def has_available_ram(self) -> bool:
		return self.python_process.memory_percent() <= 0.6


	def has_passed_chunk_limit(self) -> bool:
		return self.num_stored_tokens >= self.MAX_TOKENS_PER_CHUNK \
			and not self.has_available_ram()


	def index_tokens(self, document_id:str, tokens:str):
		for token in tokens:
			self.num_stored_tokens += 1
			self.indexer[token] += 1
			self.postings[token].add(document_id)

			if self.has_passed_chunk_limit():
				self.block_write_setup()


	def block_write_setup(self):
		# out of available memory
		# sort terms and write current block to disk
		sorted_terms = self.sort_terms(self.postings)
		output_file = f"{self.POSTINGS_DIR}block_{self.block_id}.txt.gz"

		logging.info(f"Writing new block with id {self.block_id}")
		self.write_block_to_disk(sorted_terms=sorted_terms, output_file=output_file)

		self.postings = defaultdict(lambda: set())
		self.block_id += 1


	def sort_terms(self, postings_dict):
		return sorted(postings_dict.items(), key = lambda x: x[0])


	def write_block_to_disk(self, sorted_terms, output_file='./posting_blocks/block.txt.gz'):
		with gzip.open(output_file,'wt') as f:
			for term, postings in sorted_terms:
				f.write(term + '  ' + str(postings) + '\n')

		self.num_stored_tokens = 0


	def merge_blocks(self):
		block_files_dir = os.listdir(self.POSTINGS_DIR)
		block_files = [gzip.open(self.POSTINGS_DIR+filename, 'rt') for filename in block_files_dir]
		block_postings = [block_file.readline()[:-1] for block_file in block_files]

		self.num_stored_tokens = 0

		merge_postings = defaultdict(lambda: set())

		last_term = ""

		while len(block_files) > 0:
			# get smaller element in alphabet
			min_ind = block_postings.index(min(block_postings))
			line_posting = block_postings[min_ind].split('  ')
			term, posting = line_posting[0], eval(line_posting[1])

			# write partition of postings to disk when
			# finds a new term and passed the limit
			if last_term != term and self.has_passed_chunk_limit():
				self.block_merge_setup(merge_postings)
				# reset temporary postings
				merge_postings = defaultdict(lambda: set())

			self.num_stored_tokens += len(posting)
			merge_postings[term] |= posting

			# store last term
			last_term = term

			# read next term from the correspondent block file
			block_postings[min_ind] = block_files[min_ind].readline()[:-1]

			# if file is now empty, remove file and posting from the lists
			if block_postings[min_ind] == "":
				block_files[min_ind].close()
				block_files.pop(min_ind)
				block_postings.pop(min_ind)

		# Last postings are not being written to disk, thus the function is called again
		if merge_postings:
			self.block_merge_setup(merge_postings)


	def clear_blocks(self):
		block_files_dir = os.listdir(self.POSTINGS_DIR)
		block_files = [ filename for filename in block_files_dir]
		temp = block_files
		for f in temp:
			logging.info(f"Removing block {f}")
			os.remove(f"{self.POSTINGS_DIR}{f}")


	def block_merge_setup(self, merge_postings):
		sorted_terms = self.sort_terms(merge_postings)
		first_word, last_word = sorted_terms[0][0], sorted_terms[-1][0]
		partition_file = f"{self.PARTITION_DIR}{first_word}-{last_word}.txt.gz"

		logging.info(f"Writing partition from word {first_word} to {last_word}")

		self.write_block_to_disk(sorted_terms=sorted_terms, output_file=partition_file)


	def store_indexer(self):
		with gzip.open(f"{self.INDEXER_DIR}indexer.txt.gz",'wt') as f:
			for term, freq in self.indexer.items():
				f.write(term + '  ' + str(freq) + '\n')

