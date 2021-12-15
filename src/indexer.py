import os
from collections import defaultdict, OrderedDict
from tokenizer import Tokenizer
import psutil
import logging
import gzip
import time
from math import log10, sqrt
from map_reducer import MapReducer
import sys

class Indexer:
	def __init__(self, index_dir, file_name="amazon_reviews.tsv", min_length_filter=False,\
		min_len=None, porter_filter=False, stop_words_filter=False, stopwords_file='stop_words.txt',\
		map_reducer=False, positions=False, ranking="VS", index_schema="lnc.ltc", k1=1.2, b=0.75):
		logging.info(f"Indexer")
		start_index_time = time.time()
		
		# data structures
		self.indexer = defaultdict(lambda: [0, 0])

		self.postings = defaultdict(lambda: defaultdict(lambda: [0, []]))
		
		self.ranking = ranking

		if ranking == "BM25":
			self.b = b
			self.k1 = k1
			self.docs_length = defaultdict(lambda : 0)
			self.total_docs_length = 0
			self.average_doc_len = 0

		# init tokenizer
		self.tokenizer = Tokenizer(min_length_filter, min_len, porter_filter,\
			stop_words_filter, stopwords_file)
		
		self.store_positions = positions

		# get process
		self.python_process = psutil.Process(os.getpid())

		# block id
		self.block_id = 0

		self.INDEX_DIR = f"../{index_dir}"
		self.POSTINGS_DIR = f"{self.INDEX_DIR}/posting_blocks/"
		self.PARTITION_DIR = f"{self.INDEX_DIR}/partition_index/"
		self.INDEXER_DIR = f"{self.INDEX_DIR}/indexer_dict/"
		self.CONFIG_DIR = f"{self.INDEX_DIR}/config/"

		self.file_name = file_name

		dir_list = [self.INDEX_DIR, self.POSTINGS_DIR,\
			self.PARTITION_DIR, self.INDEXER_DIR, self.CONFIG_DIR]
		self.check_dir_exist(dir_list)

		# current number of stored_chunks
		self.num_stored_items = 0

		# number of documents
		self.n_docs = 0
		
		# maximum number of tokens's postings stored in memory
		self.MAX_CHUNK_LIMIT = 1000000
		# maximum number of documents for map reduce to handle
		self.MAX_DOCS_LIMIT = 100000

		self.map_reducer = map_reducer
		if map_reducer:
			logging.info("Starting Map Reducer")
			self.map_reducer = MapReducer(tokenizer=self.tokenizer)

		# parse file and index terms and postings
		self.parse_and_index()

		# merge all block files
		self.merge_blocks()

		# delete all temporary block files
		self.clear_blocks()

		# store indexer data structure in a file
		self.store_indexer()

		# store important flags/configurations to be used in the search engine
		self.store_config()

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
			elif diretory == self.PARTITION_DIR:
				if len(os.listdir(self.PARTITION_DIR)) > 0:
					logging.info("Dataset has already been indexed.")
					sys.exit()


	def parse_and_index(self):
		data_set = open(self.file_name, 'r', encoding='utf-8')
		# ignore headers
		data_set.readline()
		input_documents = []

		logging.info("Parsing File")

		for paragraph in data_set:
			paragraph = paragraph.split("\t")
			review_id, input_string = paragraph[2],\
				f"{paragraph[-3]} {paragraph[-2]}"

			self.n_docs+=1

			if self.map_reducer:
				self.num_stored_items += 1
				input_documents.append( (review_id, input_string) )

				if self.has_passed_chunk_limit(True):
					logging.info("Sending data to map reducer")
					processed_documents = self.map_reducer(input_documents)
					logging.info("Got the processed data from map reducer")

					input_documents = []
					self.block_write_setup(processed_documents, True)
			else:
				tokens = self.tokenizer.tokenize(input_string)
				self.index_tokens(document_id=review_id, tokens=tokens)
					
				if self.has_passed_chunk_limit():
					self.block_write_setup() 

		data_set.close()
		# last chunk is not being written to disk, thus the function is called again
		if self.num_stored_items != 0:
			self.call_map_reducer(input_documents) if self.map_reducer \
			else self.block_write_setup()

		if self.map_reducer:
			self.map_reducer.close_proc()

		if self.ranking == "BM25":
			self.average_doc_len = self.calc_average_doc_len()


	def calc_average_doc_len(self):
		return self.total_docs_length / self.n_docs


	def call_map_reducer(self, input_documents):
		logging.info("Sending data to map reducer")
		processed_documents = self.map_reducer(input_documents)
		logging.info("Got the processed data from map reducer")
		self.block_write_setup(processed_documents, True)


	def has_available_ram(self) -> bool:
		return self.python_process.memory_percent() <= 2


	def has_passed_chunk_limit(self, map_red_index=False) -> bool:
		# ideally should be only ram but the constant monitoring of ram usage
		# by this process in python slows the process itself by a lot
		if map_red_index:
			return self.num_stored_items >= self.MAX_DOCS_LIMIT # and not self.has_available_ram()
		return self.num_stored_items >= self.MAX_CHUNK_LIMIT # and not self.has_available_ram()


	def index_tokens(self, document_id, tokens):
		doc_sum_term_weights = 0

		for token, positions in tokens.items():
			self.indexer[token][0] += 1
			if self.store_positions:
				self.postings[token][document_id][1] = positions

			if self.ranking == "VS":
				weight = 1 + log10(len(positions))
				self.postings[token][document_id][0] = weight
				doc_sum_term_weights += weight**2
			else:
				tf = len(positions)
				self.docs_length[document_id] += tf
				self.total_docs_length += tf
				self.postings[token][document_id][0] = tf

			self.num_stored_items += 1

		if doc_sum_term_weights:
			cos_norm = 1 / sqrt(doc_sum_term_weights)

			for token, _ in tokens.items():
				self.postings[token][document_id][0] *= cos_norm


	def sort_terms(self, postings_lst):
		return sorted(postings_lst, key = lambda x: x[0])


	def write_block_to_disk(self, sorted_terms, output_file='./posting_blocks/block.txt', map_red_index=False):
		with  open(output_file,'w+') as f:
			if map_red_index:
				for term, postings, num_occ in sorted_terms:
					self.indexer[term][0] += num_occ
					f.write(f"{term}  {';'.join([f'{doc}:{data[0]}' for doc, data in postings.items()])}\n")
			else:
				for term, postings in sorted_terms:
					if self.store_positions:
						f.write(f"{term}  {';'.join([f'{doc}:{data[0]}:{data[1]}' for doc, data in postings.items()])}\n")
					else:
						f.write(f"{term}  {';'.join([f'{doc}:{data[0]}' for doc, data in postings.items()])}\n")


	def write_partition_to_disk(self, sorted_terms, output_file='./posting_blocks/block.txt.gz', map_red_index=False):
		with gzip.open(output_file,'wt') as f:
			line = 0
			for term, postings in sorted_terms:
				self.indexer[term][1] = line
				line += 1
				if self.ranking == "VS":
					idf = log10(self.n_docs / self.indexer[term][0])
					f.write(f"{idf};{postings}\n")
				else:
					final_str = ''
					docs_tf = [doc_tf.split(':') for doc_tf in postings.split(';')]
					for doc_id, tf in docs_tf:
						B = (1 - self.b) + self.b * self.docs_length[doc_id] / self.average_doc_len
						tf_norm = int(tf) / B
						c = log10(self.n_docs / self.indexer[term][0]) * (self.k1 + 1) * tf_norm / (self.k1 + tf_norm)
						final_str += f"{doc_id}:{c};"
					f.write(f"{final_str}\n")


	def block_write_setup(self, processed_documents=None, map_red_index=False):
		output_file = f"{self.POSTINGS_DIR}block_{self.block_id}.txt"
		logging.info(f"Writing new block with id {self.block_id}")

		# sort terms and write current block to disk
		if processed_documents:
			sorted_terms = self.sort_terms(processed_documents)
		else:
			sorted_terms = self.sort_terms(self.postings.items())
			self.postings = defaultdict(lambda: defaultdict(lambda: [0, []]))
		self.write_block_to_disk(sorted_terms=sorted_terms, output_file=output_file, map_red_index=map_red_index)

		self.num_stored_items = 0
		self.block_id += 1


	def merge_blocks(self):
		block_files_dir = os.listdir(self.POSTINGS_DIR)
		block_files = [open(self.POSTINGS_DIR+filename, 'r') for filename in block_files_dir]
		block_postings = [block_file.readline()[:-1] for block_file in block_files]
		self.num_stored_items = 0

		merge_postings = OrderedDict()

		last_term = ""

		while len(block_files) > 0:
			# get smaller element in alphabet
			min_ind = block_postings.index(min(block_postings))
			line_posting = block_postings[min_ind].split('  ')

			term, postings = line_posting[0], line_posting[1]

			# write partition of postings to disk when
			# finds a new term and passed the limit
			if last_term != term and self.has_passed_chunk_limit(True):
				self.block_merge_setup(merge_postings)
				# reset temporary postings
				merge_postings = OrderedDict()
			self.num_stored_items += 1

			if term in merge_postings:
				merge_postings[term] += f";{postings}"
			else:
				merge_postings[term] = postings
	
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
		#sorted_terms = self.sort_terms(merge_postings.items())
		sorted_terms = list(merge_postings.items())
		first_word, last_word = sorted_terms[0][0], sorted_terms[-1][0]
		partition_file = f"{self.PARTITION_DIR}{first_word} {last_word}.txt.gz"

		logging.info(f"Writing partition from word {first_word} to {last_word}")

		self.write_partition_to_disk(sorted_terms=sorted_terms, output_file=partition_file)
		self.num_stored_items = 0


	def store_indexer(self):
		with gzip.open(f"{self.INDEXER_DIR}indexer.txt.gz",'wt') as f:
			for term, freq_pos in self.indexer.items():
				f.write(f"{term};{str(freq_pos[0])};{str(freq_pos[1])}\n")


	def store_config(self):
		with gzip.open(f"{self.CONFIG_DIR}config.txt.gz",'wt') as f:
			f.write(f"ranking:{self.ranking}\n")
			if self.ranking == "VS": f.write(f"index_schema:{self.index_schema}\n")
			if self.store_positions: f.write(f"store_positions\n")
			if self.tokenizer.min_length_filter: f.write(f"min_length_filter:{self.tokenizer.min_length}\n")
			if self.tokenizer.porter_filter: f.write(f"porter_filter\n")
			if self.tokenizer.stop_words_filter: f.write(f"stop_words_filter\n")
			if self.tokenizer.stop_words_file: f.write(f"stop_words_file:{self.tokenizer.stop_words_file}\n")

