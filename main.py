from indexer import Indexer
import argparse
import logging
from search_engine import Search_Engine


class Main:
    def __init__(self):
        indexer_args = self.check_arguments()

        if not self.search:
            self.indexer = Indexer(*indexer_args)
        else:
            self.search_engine = Search_Engine(self.index_dir)
            self.search_engine.search()


    def usage(self):
        print("Usage: python3 main.py \n\t-i <Directory name for indexation:str>\
            \n\t-f <File Name for data set:str> \n\t-m <Minimum Length Filter>\
            \n\t-l <Length for Minimum Length Filter:int> \n\t-p <Porter Stemmer Filter>\
            \n\t-s <Stop Words Filter>\n\t -sf <Stop Words File> \n\t-mp <Map Reduce>")


    def check_arguments(self):
        arg_parser = argparse.ArgumentParser(
            prog="Indexer",
            usage=self.usage
        )
        arg_parser.add_argument('-index_dir', nargs=1, default=[''])
        arg_parser.add_argument('-file_name', nargs=1, default=['amazon_reviews.tsv'])
        arg_parser.add_argument('-min_length', action='store_true')
        arg_parser.add_argument('-length', nargs=1, type=int)
        arg_parser.add_argument('-porter', action='store_true')
        arg_parser.add_argument('-stopwords', action='store_true')
        arg_parser.add_argument('-path_stopwords', nargs=1,  default=['stopwords.txt'])
        arg_parser.add_argument('-search', action='store_true')
        arg_parser.add_argument('-mp', action='store_true')


        args = arg_parser.parse_args()

        self.search = args.search
        self.index_dir = args.index_dir[0]
        file_name = args.file_name[0]
        if self.index_dir == "":
            self.index_dir = file_name.split('.')[0]
        min_len = args.length[0] if args.min_length and args.length else None

        return self.index_dir, file_name, args.min_length, min_len, args.porter, args.stopwords, args.path_stopwords[0], args.mp


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    main = Main()
