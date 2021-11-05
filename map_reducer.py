import multiprocessing
import collections
import itertools

class MapReducer:
	def __init__(self, map_func, reduce_func, num_workers=None) -> None:
		self.num_workers = num_workers
		self.pool = multiprocessing.Pool(num_workers)
		self.map_func = map_func
		self.reduce_func = reduce_func

	def partition(self, mapped_values):
		"""Organize the mapped values by their key.
		Returns an unsorted sequence of tuples with a key and a sequence of values.
		"""
		partitioned_data = collections.defaultdict(list)
		for key, value in mapped_values:
			partitioned_data[key].append(value)

		return partitioned_data.items()

	def __call__(self, inputs, chunksize=1):
		"""Process the inputs through the map and reduce functions given.

		inputs
		  An iterable containing the input data to be processed.

		chunksize=1
		  The portion of the input data to hand to each worker.  This
		  can be used to tune performance during the mapping phase.
		"""
		map_responses = self.pool.map(self.map_func, inputs, chunksize=chunksize)
		partitioned_data = self.partition(itertools.chain(*map_responses))
		reduced_values = self.pool.map(self.reduce_func, partitioned_data)
		return reduced_values
