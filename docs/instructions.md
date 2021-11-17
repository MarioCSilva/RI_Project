## How to run

Inside the RI_Project diretory:

- Run the command to install requirements:
```bash
pip3 install -r requirements.txt
```

- To run the project go to the `src` dir and simply execute:
```bash
python3 main.py
```

- Additional arguments:
```
    -i <Directory name for indexation:str>
    -f <File Name for data set:str>
    -m <Minimum Length Filter>
    -l <Length for Minimum Length Filter:int>
    -p <Porter Stemmer Filter>
    -stopwords <Stop Words Filter>
    -stopwords_file <Stop Words File>
    -mp <Map Reduce>
    -search <Search Engine>
    -positions <Store term's positions in postings>
```
