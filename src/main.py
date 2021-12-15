from indexer import Indexer
import argparse
import logging
import sys
from search_engine import Search_Engine


class Main:
    def __init__(self):
        indexer_args = self.check_arguments()

        if not self.search:
            self.indexer = Indexer(*indexer_args)
        else:
            self.search_engine = Search_Engine(self.index_dir, self.queries_file)


    def usage(self):
        print("Usage: python3 main.py\
            \n\t-i <Directory name for indexation:str>\
            \n\t-f <File Name (Path) for data set:str>\
            \n\t-m <Minimum Length Filter>\
            \n\t-l <Length for Minimum Length Filter:int>\
            \n\t-porter <Porter Stemmer Filter>\
            \n\t-stopwords <Stop Words Filter>\
            \n\t-stopwords_file <Stop Words File>\
            \n\t-mp <Map Reduce>\
            \n\t-search <Search Engine>\
            \n\t-positions <Store term's positions in postings>")


    def check_arguments(self):
        arg_parser = argparse.ArgumentParser(
            prog="Indexer",
            usage=self.usage
        )
        arg_parser.add_argument('-index_dir', nargs=1, default=[''])
        arg_parser.add_argument('-filename', nargs=1, default=['amazon_reviews.tsv'])
        arg_parser.add_argument('-min_length', action='store_true')
        arg_parser.add_argument('-length', nargs=1, type=int)
        arg_parser.add_argument('-porter', action='store_true')
        arg_parser.add_argument('-stopwords', action='store_true')
        arg_parser.add_argument('-stopwords_file', nargs=1, default=['stopwords.txt'])
        arg_parser.add_argument('-search', action='store_true')
        arg_parser.add_argument('-mp', action='store_true')
        arg_parser.add_argument('-positions', action='store_true')
        arg_parser.add_argument('-queries_file', nargs=1, default=['queries.txt'])
        arg_parser.add_argument('-ranking', nargs=1, choices=['BM25', 'VS'], default=['VS'])
        arg_parser.add_argument('-k1', nargs=1, type=int, default=[1.2])
        arg_parser.add_argument('-b', nargs=1, type=int, default=[0.75])
        arg_parser.add_argument('-schema', nargs=1, choices=['lnc.ltc', 'lnc.ntc'], type=str, default=["lnc.ltc"])

        try:
            args = arg_parser.parse_args()
        except:
            self.usage()
            sys.exit(0)

        self.search = args.search
        self.index_dir = args.index_dir[0]
        filename = args.filename[0]
        if self.index_dir == "":
            self.index_dir = filename.split('/')[-1].split('.')[0]
        min_len = args.length[0] if args.min_length and args.length else None

        self.queries_file = args.queries_file[0]
    
        return self.index_dir, filename, args.min_length, min_len, args.porter,\
            args.stopwords, args.stopwords_file[0], args.mp, args.positions, args.ranking[0], args.schema[0], args.k1[0], args.b[0]


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    main = Main()
