from indexer import Indexer
import argparse
import logging


class Main:
    def __init__(self):
        self.indexer = Indexer(*self.check_arguments())


    def usage(self):
        print("Usage: python3 main.py \n\t-f <File Name for data set:str> \n\t-m <Minimum Length Filter>" +\
            "\n\t-l <Length for Minimum Length Filter:int> \n\t-p <Porter Stemmer Filter> \n\t-s <Stop Words Filter>\n\t -sf <Stop Words File>")


    def check_arguments(self):
        arg_parser = argparse.ArgumentParser(
            prog="Indexer",
            usage=self.usage
        )
        arg_parser.add_argument('-file_name', nargs=1, default=['amazon_reviews.tsv'])
        arg_parser.add_argument('-min_length', action='store_true')
        arg_parser.add_argument('-length', nargs=1, type=int)
        arg_parser.add_argument('-porter', action='store_true')
        arg_parser.add_argument('-stopwords', action='store_true')
        arg_parser.add_argument('-sf', nargs=1,  default=['stop_words.txt'])

        args = arg_parser.parse_args()

        file_name = args.file_name[0]
        min_len = args.length[0] if args.min_length and args.length else None
        
        return file_name, args.min_length, min_len, args.porter, args.stopwords, args.sf[0]


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    main = Main()
