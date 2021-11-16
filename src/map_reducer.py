import logging
from multiprocessing import Queue, Process, Manager, Pool
from collections import defaultdict
from functools import partial

class MapReducer:
	def __init__(self, tokenizer, num_workers=4) -> None:
		self.num_workers = num_workers
		# self.pool = Pool(processes=num_workers)
		self.tokenizer = tokenizer
		self.map_q_in = Manager().Queue(1)
		self.map_q_out = Manager().Queue()
		self.map_proc = [Process(target=MapReducer.map_func, args=(self.map_q_in, self.map_q_out, self.tokenizer))
            for _ in range(self.num_workers)]
		self.red_q_in = Manager().Queue(1)
		self.red_q_out = Manager().Queue()
		self.red_proc = [Process(target=MapReducer.reduce_func, args=(self.red_q_in, self.red_q_out))
            for _ in range(self.num_workers)]
		for p in self.map_proc:
			p.daemon = True
			p.start()
		for p in self.red_proc:
			p.daemon = True
			p.start()

	# mapper
	# {term:{ doc_id_1: [2,3,4] } }
	# {term:{ doc_id_2: [6,4] } }
	@staticmethod
	def map_func(q_in, q_out, tokenizer) -> list:
		while True:
			document_id, text = q_in.get()
			if document_id is None and text is None:
				break
			output = defaultdict(partial(defaultdict, list))
			for token, positions in tokenizer.tokenize(text).items():
				output[token][document_id] = positions
			q_out.put(output)
	
	# @staticmethod
	# def map_func(document, tokenizer) -> list:
	# 	document_id, text = document[0], document[1]

	# 	output = defaultdict(partial(defaultdict, list))

	# 	for index, token in enumerate(text.lower().split()):
	# 		output[token][document_id].append(index)
	# 	return output

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
	def reduce_func(q_in, q_out) -> tuple:
		while True:
			term, doc_id_pos = q_in.get()
			if term is None and doc_id_pos is None:
				break
			q_out.put((term, doc_id_pos, len(doc_id_pos.keys())))

	# @staticmethod
	# def reduce_func(partitioned_data) -> tuple:
	# 	term, doc_id_pos = partitioned_data
	# 	return (term, doc_id_pos, len(doc_id_pos.keys()))

	def close_proc(self):
		logging.info('closing processes')
		# self.pool.join()
		# self.pool.close()
		[self.map_q_in.put((None, None)) for _ in range(self.num_workers)]
		[self.red_q_in.put((None, None)) for _ in range(self.num_workers)]
		for p in self.map_proc:
			p.join()
			p.close()

		for p in self.red_proc:
			p.join()
			p.close()


	def __call__(self, inputs):
		"""Process the inputs through the map and reduce functions given.

		inputs
		  A list containing the input data to be processed.
		"""
		sent = [self.map_q_in.put(doc) for doc in inputs]
		map_responses = [self.map_q_out.get() for _ in range(len(sent))]
		# map_responses = self.pool.map(partial(MapReducer.map_func, tokenizer=self.tokenizer), inputs, chunksize=1)
		logging.info("Mapping done")
		partitioned_data = self.partition(map_responses)
		logging.info("Partitioning done")
		sent = [self.red_q_in.put(part_doc) for part_doc in partitioned_data]
		reduced_values = [self.red_q_out.get() for _ in range(len(sent))]
		logging.info("Reduction done")
		# reduced_values = self.pool.map(MapReducer.reduce_func, partitioned_data)
		return reduced_values
