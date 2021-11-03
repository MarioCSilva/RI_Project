from collections import defaultdict
import os
import gzip


class Search_Engine:
    def __init__(self, indexer_dir):
        self.INDEXER_DIR = './indexer_dict/'
        
        self.indexer = defaultdict(int)
        self.load_indexer()


    """ Load indexer data structure into memory """
    def load_indexer(self):
        indexer_dir = os.listdir(self.INDEXER_DIR)
        if len(indexer_dir) < 0:
            return

        indexer_file = gzip.open(f"{self.INDEXER_DIR}indexer.txt.gz", 'rb')

        for line in indexer_file:
            indexer_line = str(line).readline()[:-1].split('  ')
            term, freq = indexer_line[0][1]
            self.indexer[term] = freq