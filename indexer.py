import csv
import os
import nltk
from collections import defaultdict
from tokenizer import Tokenizer
import psutil

class Indexer:
	def __init__(self, file_name="amazon_reviews.tsv", min_length_filter=False,\
		min_len=None, porter_filter=False, stop_words_filter=False,\
		stopwords_file='stop_words.txt'):

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

		self.POSTINGS_DIR = './posting_blocks/'

		# current number of stored tokens
		self.num_stored_tokens = 0

		# maximum number of tokens's postings stored in memory
		self.MAX_TOKENS_PER_CHUNK = 1000000


	def parse_file(self):
		tsv_file = open(self.file_name)
		reviews_file = csv.reader(tsv_file, delimiter="\n")
		# ignore headers
		next(reviews_file)

		for paragraph in reviews_file:
			paragraph = paragraph[0].split("\t")
			review_id, review_headline, review_body = \
				paragraph[2], paragraph[-3], paragraph[-2]
		
			input_string = review_headline + review_body

			tokens = self.tokenizer.tokenize(input_string)

			self.index_tokens(document_id=review_id, tokens=tokens)

		self.merge_blocks()


	def has_available_ram(self) -> bool:
		return self.python_process.memory_percent() <= 0.4


	def has_passed_chunk_limit(self) -> bool:
		return self.num_stored_tokens >= self.MAX_TOKENS_PER_CHUNK


	def index_tokens(self, document_id:str, tokens:str):
		for token in tokens:
			self.num_stored_tokens += 1
			self.indexer[token] += 1
			self.postings[token].add(document_id)

			if self.has_passed_chunk_limit():
				# out of available memory
				# sort terms and write current block to disk
				sorted_terms = self.sort_terms(self.postings)
				output_file = f"{self.POSTINGS_DIR}block_{self.block_id}.txt"

				print(f"Writing new block with id {self.block_id}")
				self.write_block_to_disk(sorted_terms=sorted_terms, output_file=output_file)

				self.postings = defaultdict(lambda: set())
				self.block_id+=1

		#TODO: Currently last chunk is not being written to disk


	def sort_terms(self, postings_dict):
		return sorted(postings_dict.items(), key = lambda x: x[0])


	def write_block_to_disk(self, sorted_terms, output_file='./posting_blocks/block.txt'):
		with open(output_file,'w+') as f:
			for term, postings in sorted_terms:
				f.write(term + '  ' + str(postings) + '\n')

		self.num_stored_tokens = 0


	def merge_blocks(self):
		block_files_dir = os.listdir(self.POSTINGS_DIR)
		block_files = [open(self.POSTINGS_DIR+filename) for filename in block_files_dir]
		block_postings = [block_file.readline()[:-1] for block_file in block_files]
		
		self.num_stored_tokens = 0

		merge_postings = defaultdict(lambda: set())

		last_term = ""

		print(len(block_files))

		while len(block_files) > 0:
			# get smaller element in alphabet
			min_ind = block_postings.index(min(block_postings))
			line_posting = block_postings[min_ind].split('  ')
			term, posting = line_posting[0], eval(line_posting[1])

			# write partition of postings to disk when
			# finds a new term and passed the limit
			if last_term != term and self.has_passed_chunk_limit():
				sorted_terms = self.sort_terms(merge_postings)
				first_word, last_word = sorted_terms[0][0], sorted_terms[-1][0]
				partition_file = f"{self.POSTINGS_DIR}{first_word}-{last_word}.txt"

				self.write_block_to_disk(sorted_terms=sorted_terms, output_file=partition_file)

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
				print(len(block_files))

		#TODO: Currently last postings are not being written to disk


	def print_indexer(self):
		print(self.indexer)

	def print_postings(self):
		print(self.postings)