import sys
from indexer import Indexer

class Menu:
    def __init__(self):
        self.indexer = Indexer()

        self.choices = {
            "1": self.indexer.file_parsing,
        }

    def display_menu(self):
        print("""
            Menu
            1. Read File
        """)

    def run(self):
        self.indexer.file_parsing()
        self.indexer.print_indexer()
        self.indexer.print_postings()

        '''Display the menu and respond to choices.'''
        # while True:
        #     self.display_menu()
        #     choice = input("Enter an option: ")
        #     action = self.choices.get(choice)
        #     if action:
        #         action()
        #     else:
        #         print("{0} is not a valid choice".format(choice))

    def quit(self):
        sys.exit(0)

if __name__ == "__main__":
    Menu().run()