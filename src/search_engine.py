from collections import defaultdict
from email.policy import default
import os
import gzip
import sys
import logging
from tokenizer import Tokenizer
from functools import lru_cache
from math import log10, sqrt, log2
import time
from tabulate import tabulate
from statistics import mean


class Search_Engine:
    def __init__(self, index_dir, queries_file, boost, window_size):
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
        self.boost = boost
        self.window_size = window_size

        self.queries_file = queries_file

        self.load_indexer()

        self.load_doc_mapping()
        self.top_k = [10, 20, 50]

        self.metrics = {}
        for k in self.top_k:
            self.metrics[k] = {'precision': [], 'recall': [],\
                'f_measure': [], 'avg_precision': [], 'ndcg' : []}

        total_prepare_time = time.time() - prepare_search_time

        queries_times = self.search_queries()

        self.get_statistics(total_prepare_time, queries_times)


    def check_dir_exist(self, directory):
        if not os.path.exists(directory):
            os.mkdir(directory)


    def get_statistics(self, total_prepare_time, queries_times):
        print(f"e) Time to start up an index searcher, after the final index is written to disk: {total_prepare_time:.2f} seconds")
        print(f"Total time to handle {queries_times[2]} queries: {queries_times[0]:.2f} seconds")
        print(f"Average time to handle a single query: {queries_times[1]:.2f} seconds")

        headers = ["Top K", "Precision", "Recall", "F-Measure", "Average Precision", "NDCG"]
        data = []
        for k, metrics in self.metrics.items():
            data.append([k, mean(metrics['precision']), mean(metrics['recall']),\
                mean(metrics['f_measure']), mean(metrics['avg_precision']), mean(metrics['ndcg'])])
        print(self.ranking+": Mean Values Over All Queries" + " With Boost" if self.boost else "")
        print(tabulate(data, headers=headers))


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

    """ Finds the partition file in which the term is indexed"""
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
        """
        Find the terms partition and retrieves the document weights
        for the term in cause, according to the ranking strategy.
        Has a Least Recently Used cache.
        """
        idf, partition_line = self.indexer[term]

        if idf:
            partition_file = self.get_partition_file(term)
            # logging.info(f"Postings of '{term}' are indexed in the partition file '{partition_file}'")

            try:
                partition_file = gzip.open(partition_file, 'rt')
            except FileNotFoundError as e:
                logging.error("Could not find partition on disk.")
                return None

            term_postings = self.read_file_line(partition_file, partition_line).split(';')[:-1]
            partition_file.close()
            
            doc_pos = {}

            if self.ranking == "VS":
                doc_weights = {}

                for doc_weight_str in term_postings:
                    doc_info = doc_weight_str.split(':')
                    if not self.store_positions:
                        doc, weight = self.doc_mapping[doc_info[0]], float(doc_info[1])
                    else:
                        doc, weight, pos = self.doc_mapping[doc_info[0]], float(doc_info[1]), doc_info[2]
                    doc_weights[doc] = weight
                    doc_pos[doc] = pos[1:-1].split(', ')
                # In Vector Space, we need to retrieve also the Idf of the term
                return idf, doc_weights, doc_pos

            # BM25
            doc_scores = {}
            for doc_score in term_postings:
                doc_info = doc_score.split(":")
                if not self.store_positions:
                    doc_id, score = doc_info
                else:
                    doc_id, score, pos = doc_info
                doc_scores[self.doc_mapping[doc_id]] = float(score)
                doc_pos[self.doc_mapping[doc_id]] = pos[1:-1].split(', ')
            return doc_scores, doc_pos


    def handle_query_vs(self, query):
        """
        Calculates the final score of each document for the query
        and retrieves a list with the 100 most relevant document,
        using the VS Strategy, with the choosen Indexing schema
        """
        use_idf = True

        scores = defaultdict(lambda: 0)

        tokenized_query = self.tokenizer.tokenize(query)

        # if the query has only one term there's no need to use idf
        if len(tokenized_query) == 1:
            use_idf = False

        cos_norm_value = 0
        term_doc_pos = {}

        for term, positions in tokenized_query.items():
            search_result = self.search_term(term)

            if not search_result:
                print(f"Term '{term}' not indexed.")
                continue

            idf, doc_weights, doc_pos = search_result
            if self.store_positions:
                term_doc_pos[term] = doc_pos
           
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
        
        if self.boost:
            scores = self.boost_function(scores, term_doc_pos, tokenized_query)

        return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:50]


    def handle_query_bm25(self, query):
        """
        Calculates the final score of each document for the query
        and retrieves a list with the 100 most relevant document,
        using the BM25 Strategy
        """
        scores = defaultdict(lambda: 0)

        tokenized_query = self.tokenizer.tokenize(query)
        term_doc_pos = {}
        for term, positions in tokenized_query.items():
            doc_scores, doc_pos = self.search_term(term)
            
            if self.store_positions:
                term_doc_pos[term] = doc_pos
                
            tf = len(positions)

            if not doc_scores:
                print(f"Term '{term}' not indexed.")
                continue

            for doc_id, score in doc_scores.items():
                scores[doc_id] += score * tf

        if self.boost:
            scores = self.boost_function(scores, term_doc_pos, tokenized_query)

        return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:50]


    def boost_function(self, scores, term_doc_pos, tokenized_query):
        if self.ranking == "VS":
            boost = 0.5
        else:
            boost = 2

        for doc in scores:
            windows = {}
            for term, doc_pos in term_doc_pos.items():
                if doc in doc_pos:
                    for pos in doc_pos[doc]:
                        windows[int(pos)] = []
            for init_pos in windows:
                for term, doc_pos in term_doc_pos.items():
                    if doc in doc_pos:
                        for pos in doc_pos[doc]:
                            pos = int(pos)
                            term_win_pos = pos - init_pos
                            if 0 <= term_win_pos <= self.window_size:
                                windows[init_pos].append((term, term_win_pos))

            for window in windows.values():
                if len(window) == 1:
                    continue
                
                unique = set()
                [unique.add(x) for x, _ in window]
                
                if len(unique) == 1:
                    continue

                window.sort(key = lambda x: x[1])
                lst_index = -1
                pos_offset = 1
                terms = list(tokenized_query.keys())

                for term, pos in window:
                    pos_offset += self.window_size - abs(pos - tokenized_query[term][0])
                    if lst_index != -1 and terms.index(term) - lst_index == 1:
                        pos_offset += self.window_size
                    lst_index = terms.index(term)
                
                pos_offset += (len(tokenized_query) - len(unique)) * (self.window_size - 1)
                scores[doc] += boost / pos_offset

        return scores


    def write_results_to_file(self, queries_results_file, query, results_query):
        queries_results_file.write(f"Q: {query}\n")
        results = '\n'.join(results_query)
        queries_results_file.write(f"{results}\n")


    def search_queries(self):
        """
        Loads a file with a query in each line, and writes to the disk the most relevant documents
        according to the choosen ranking strategy.
        """
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
            results_query = self.handle_query_vs(query) if self.ranking == "VS"\
                else self.handle_query_bm25(query)

            queries_total_time += time.time() - start_time

            self.write_results_to_file(queries_results_file, query, results_query)
            self.get_metrics(query, results_query)

        queries_average_time = queries_total_time / num_queries
        return queries_total_time, queries_average_time, num_queries


    def get_metrics(self, query, results_query):
        relevant_docs = self.get_relevant_docs(query)
        top_rel_docs = list(relevant_docs.items())
        
        headers = ["Top K", "Precision", "Recall", "F-Measure", "Average Precision", "NDCG"]
        data = []

        for k in self.top_k:
            TP, avg_precision, dcg, ideal_dcg = 0, 0, 0, 0
            for num_doc, doc in enumerate(results_query[:k]):
                if not num_doc:
                    ideal_dcg = top_rel_docs[num_doc][1]
                else:
                    ideal_dcg += top_rel_docs[num_doc][1] / log2(num_doc + 1)

                if doc in relevant_docs:
                    if not num_doc:
                        dcg = relevant_docs[doc]
                    else:
                        dcg += relevant_docs[doc] / log2(num_doc + 1)

                    TP += 1
                    avg_precision += TP / (num_doc + 1)

            ndcg = dcg / ideal_dcg

            FP = FN = k - TP
            # precision and recall have the same denominator
            precision = recall = TP / (TP + FP) if TP + FP else 0

            f_measure = 2 * precision * recall / (precision + recall) if precision else 0

            avg_precision = avg_precision / (num_doc + 1)

            self.metrics[k]['precision'].append(precision)
            self.metrics[k]['recall'].append(recall)
            self.metrics[k]['f_measure'].append(f_measure)
            self.metrics[k]['avg_precision'].append(avg_precision)
            self.metrics[k]['ndcg'].append(ndcg)
            data.append([k, precision, recall, f_measure, avg_precision, ndcg])

        print(f"Metrics for Q:{query}")
        print(f"{tabulate(data, headers)}\n")


    def get_relevant_docs(self, query):
        f = open('queries_relevance.txt')
        relevant_docs = {}
        found_query = False
        
        for line in f:
            line = line.strip()
            if 'Q:' in line:
                if line.split(':')[-1] == query:
                    found_query = True
            elif found_query:
                if not line:
                    return relevant_docs
                doc, relevancy = line.split()
                relevant_docs[doc] = int(relevancy)
        return relevant_docs
