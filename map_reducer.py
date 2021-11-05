import logging
import multiprocessing
from collections import defaultdict
import itertools
from functools import partial
from itertools import repeat

from tokenizer import Tokenizer

class MapReducer:
	def __init__(self, tokenizer , num_workers=None) -> None:
		self.num_workers = num_workers
		self.pool = multiprocessing.Pool(num_workers)
		self.tokenizer = tokenizer
		logging.info(f"tokenizer: {self.tokenizer}")

	# mapper
	# [term, doc_id_1, [2,3,4]]
	# [term, doc_id_2, [6,4]]
	@staticmethod
	def map_func(document, tokenizer) -> list:
		document_id, text = document[0], document[1]

		output = defaultdict(partial(defaultdict, list))
	
		words = text.split(' ')
		for index, word in enumerate(words):
			tokens = tokenizer.tokenize(word)

			for token in tokens:
				output[token][document_id].append(index)
		return output

	# partition/shuffle
	# {term: {doc_id_1: [2,3,4]}, {doc_id_2: [6,4]}}
	def partition(self, mapped_values):
		"""Organize the mapped values by their key.
		Returns an unsorted sequence of tuples with a key and a sequence of values.
		"""
		partitioned_data = defaultdict(partial(defaultdict, list))
		for mapping in mapped_values:
			for term, doc_id_pos in mapping.items():
				partitioned_data[term].update(doc_id_pos)
		return partitioned_data.items()

	# ({term: [(doc_id_1,(2,3,4)), doc_id_2 str(6,4)]}, 5)
	@staticmethod
	def reduce_func(partitioned_data) -> tuple:
		term, doc_id_pos = partitioned_data
		return (term, doc_id_pos, sum(len(lst) for lst in doc_id_pos.values()))


	def __call__(self, inputs, chunksize=1):
		"""Process the inputs through the map and reduce functions given.

		inputs
		  An iterable containing the input data to be processed.

		chunksize=1
		  The portion of the input data to hand to each worker.  This
		  can be used to tune performance during the mapping phase.
		"""
		map_responses = self.pool.map(partial(MapReducer.map_func, tokenizer=self.tokenizer), inputs, chunksize=chunksize)
		partitioned_data = self.partition(map_responses)
		reduced_values = self.pool.map(MapReducer.reduce_func, partitioned_data)
		return reduced_values
