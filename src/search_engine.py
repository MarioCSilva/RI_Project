from collections import defaultdict
import os
import gzip
import sys
import logging
from tokenizer import Tokenizer
from functools import lru_cache
from math import log10, sqrt
import time


class Search_Engine:
    def __init__(self, index_dir, queries_file):
        prepare_search_time = time.time()

        self.INDEX_DIR = f"../{index_dir}"
        self.INDEXER_DIR = f"{self.INDEX_DIR}/indexer_dict/"
        self.PARTITION_DIR = f"{self.INDEX_DIR}/partition_index/"
        self.CONFIG_DIR = f"{self.INDEX_DIR}/config/"
        self.QUERY_DIR = f"{self.INDEX_DIR}/search_engine/"

        self.check_dir_exist(self.QUERY_DIR)

        self.indexer = defaultdict(lambda: [0, 0])
        self.doc_mapping = {}

        self.store_positions = False
        self.index_schema = None
        self.tokenizer = self.read_config()

        self.queries_file = queries_file

        self.load_indexer()

        self.load_doc_mapping()

        total_prepare_time = time.time() - prepare_search_time

        self.get_statistics(total_prepare_time=total_prepare_time)

        queries_times = self.search_queries()

        self.get_statistics(queries_times=queries_times)


    def check_dir_exist(self, directory):
        if not os.path.exists(directory):
            os.mkdir(directory)


    def get_statistics(self, total_prepare_time=None, queries_times=None):
        if total_prepare_time:
            print(f"e) Time to start up an index searcher, after the final index is written to disk: {total_prepare_time:.2f} seconds")
        if queries_times:
            print(f"Total time to handle {queries_times[2]} queries: {queries_times[0]:.2f} seconds")
            print(f"Average time to handle a single query: {queries_times[1]:.2f} seconds")


    """ Load configurations used during indexation """
    def read_config(self):
        tokenizer = Tokenizer()
        try:
            config_dir = os.listdir(self.CONFIG_DIR)
            if len(config_dir) < 0:
                return
            config_file = gzip.open(f"{self.CONFIG_DIR}config.txt.gz",'rt')
        except FileNotFoundError as e:
            logging.error("Could not find configurations file on disk. Please run the indexer first.")
            sys.exit(0)

        for line in config_file:
            config = line[:-1].split(':')

            if config[0] == "ranking":
                self.ranking = config[1]
            elif config[0] == "index_schema":
                self.index_schema = config[1]
            elif config[0] == "store_positions":
                self.store_positions = True
            elif config[0] == "min_length_filter":
                tokenizer.min_length_filter = True
                tokenizer.init_min_len_filter(int(config[1]))
            elif config[0] == "porter_filter":
                tokenizer.porter_filter = True
                tokenizer.init_porter_filter()
            elif config[0] == "stop_words_filter":
                tokenizer.stop_words_filter = True
            elif config[0] == "stop_words_file":
                stop_words_file = config[1]
                tokenizer.init_stop_words_filter(stop_words_file)

        return tokenizer


    """ Load indexer data structure into memory """
    def load_indexer(self):
        try:
            indexer_dir = os.listdir(self.INDEXER_DIR)
            if len(indexer_dir) < 0:
                return
            indexer_file = gzip.open(f"{self.INDEXER_DIR}indexer.txt.gz", 'rt')
        except FileNotFoundError as e:
            logging.error("Could not find indexer on disk. Please run the indexer first.")
            sys.exit(0)

        for line in indexer_file:
            indexer_line = line[:-1].split(';')
            term = indexer_line[0]
            self.indexer[term][0], self.indexer[term][1] = \
                float(indexer_line[1]), int(indexer_line[2])
    

    """ Load documents id mapping data structure into memory """
    def load_doc_mapping(self):
        try:
            indexer_dir = os.listdir(self.INDEXER_DIR)
            if len(indexer_dir) < 0:
                return
            doc_mapping_file = gzip.open(f"{self.INDEXER_DIR}doc_mapping.txt.gz", 'rt')
        except FileNotFoundError as e:
            logging.error("Could not find document mapping on disk. Please run the indexer first.")
            sys.exit(0)

        for line in doc_mapping_file:
            doc_mapping_line = line[:-1].split(';')
            self.doc_mapping[doc_mapping_line[0]] = doc_mapping_line[1]


    def get_partition_file(self, term):
        for file in os.listdir(self.PARTITION_DIR):
            first_term, last_term = file.split('.')[0].split(' ')
            if term >= first_term and term <= last_term:
                return f"{self.PARTITION_DIR}{file}"


    def read_file_line(self, file, line):
        for i, x in enumerate(file):
            if i == line:
                return x[:-1]


    @lru_cache(maxsize=50)
    def search_term(self, term):
        idf, partition_line = self.indexer[term]

        if idf:
            partition_file = self.get_partition_file(term)
            logging.info(f"Postings of '{term}' are indexed in the partition file '{partition_file}'")

            try:
                partition_file = gzip.open(partition_file, 'rt')
            except FileNotFoundError as e:
                logging.error("Could not find partition on disk.")
                return None

            term_postings = self.read_file_line(partition_file, partition_line).split(';')[:-1]
            partition_file.close()

            if self.ranking == "VS":
                doc_weights = {}

                for doc_weight_str in term_postings:
                    doc_weight = doc_weight_str.split(':')
                    doc, weight = self.doc_mapping[doc_weight[0]], float(doc_weight[1])
                    doc_weights[doc] = weight
                return idf, doc_weights

            doc_scores = {}
            for doc_score in term_postings:
                doc_id, score = doc_score.split(":")
                doc_scores[self.doc_mapping[doc_id]] = float(score)
            return doc_scores


    def handle_query_vs(self, query):
        use_idf = True

        scores = defaultdict(lambda: 0)

        tokenized_query = self.tokenizer.tokenize(query)

        if len(tokenized_query) == 1:
            use_idf = False

        cos_norm_value = 0

        for term, positions in tokenized_query.items():
            search_result = self.search_term(term)

            if not search_result:
                print(f"Term '{term}' not indexed.")
                continue

            idf, doc_weights = search_result
            tf = len(positions)

            if self.index_schema[4] == 'l':
                weight = 1 + log10(tf)
            elif self.index_schema[4] == 'n':
                weight = tf

            if self.index_schema[5] == 't' and use_idf:
                weight *= idf

            if self.index_schema[6] == "c":
                cos_norm_value += weight ** 2

            for doc, doc_weight in doc_weights.items():
                scores[doc] += doc_weight * weight

        if self.index_schema[6] == "c" and cos_norm_value:
            cos_norm_value = 1 / sqrt(cos_norm_value)

            for doc in scores.keys():
                scores[doc] *= cos_norm_value

        return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:100]


    def handle_query_bm25(self, query):
        scores = defaultdict(lambda: 0)

        tokenized_query = self.tokenizer.tokenize(query)

        for term, positions in tokenized_query.items():
            doc_scores = self.search_term(term)
            tf = len(positions)

            if not doc_scores:
                print(f"Term '{term}' not indexed.")
                continue

            for doc_id, score in doc_scores.items():
                scores[doc_id] += score * tf

        return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:100]


    def write_results_to_file(self, queries_results_file, query, results_query):
        queries_results_file.write(f"Q: {query}\n")
        results = '\n'.join(results_query)
        queries_results_file.write(f"{results}\n")


    def search_queries(self):
        try:
            queries_file = open(self.queries_file, "r")
        except FileNotFoundError:
            logging.info("File for queries not found.")
            sys.exit()

        index_schema = f'_{self.index_schema}' if self.index_schema else ''
        filename = f"{self.QUERY_DIR}queries_results_{self.ranking}{index_schema}.txt"
        queries_results_file = open(filename, 'w+')

        queries_total_time, num_queries = 0, 0

        for query in queries_file:
            num_queries += 1

            start_time = time.time()

            query = query[:-1] if query[-1] == "\n" else query
            results_query = self.handle_query_vs(query)if self.ranking == "VS"\
                else self.handle_query_bm25(query)

            queries_total_time += time.time() - start_time

            self.write_results_to_file(queries_results_file, query, results_query)

        queries_average_time = queries_total_time / num_queries
        return queries_total_time, queries_average_time, num_queries
