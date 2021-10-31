from indexer import Indexer
import argparse

class Main:
    def __init__(self):
        self.indexer = Indexer(*self.check_arguments())


    def check_arguments(self):
        arg_parser = argparse.ArgumentParser(
            prog="Indexer",
            usage="-f file_name.txt -l 4 -p -s stop_words.txt"
        )
        arg_parser.add_argument('-file_name', nargs=1, default=['amazon_reviews.tsv'])
        arg_parser.add_argument('-min_length', action='store_true')
        arg_parser.add_argument('-length', nargs=1, type=int)
        arg_parser.add_argument('-porter', action='store_true')
        arg_parser.add_argument('-stopwords', action='store_true')
        arg_parser.add_argument('-stopwords_file', nargs=1,  default=['stop_words.txt'])

        args = arg_parser.parse_args()

        file_name = args.file_name[0]
        min_len = args.length[0] if args.min_length and args.length else None

        print(file_name, args.min_length, min_len, args.porter, args.stopwords, args.stopwords_file)
        
        return file_name, args.min_length, min_len, args.porter, args.stopwords, args.stopwords_file


    def run(self):
        self.indexer.parse_file()


if __name__ == "__main__":
    main = Main()
    main.run()
