## How to run

Inside the RI_Project diretory:

- Run the command to install requirements:
```bash
pip3 install -r requirements.txt
```

- Add to a diretory called `dataset` the files that contain the documents to be indexed.

- To run the project go to the `src` dir and simply execute (the default value of the file may be different so please consider indicating that parameter):
```bash
python3 main.py
```

- Additional arguments:
```
    -i <Directory name for indexation:str>
    -f <File Name for data set:str>
    -mi <Minimum Length Filter>
    -l <Length for Minimum Length Filter:int>
    -por <Porter Stemmer Filter>
    -stopwords <Stop Words Filter>
    -stopwords_file <Stop Words File>
    -mp <Map Reduce>
    -search <Search Engine>
    -pos <Store term's positions in postings>
```
