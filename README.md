# RI Project

Document indexer using the SPIMI approach.


## Structure

### Class Indexer:
- does w/e

### Class Tokenizer:
- does w/e

### Class Main:
- does w/e


## How to run

Inside the RI_Project diretory:

- Run the command to install requirements:
```
pip3 install -r requirements.txt
```

- To run the project simply execute:
```
python3 main.py
```

- Additional arguments:
```
    -f <File Name for data set:str>
    -m <Minimum Length Filter>
    -l <Length for Minimum Length Filter:int>
    -p <Porter Stemmer Filter>
    -s <Stop Words Filter>
    -sf <Stop Words File>
```

## Statistics

a) Total indexing time. (No filters)
b) Total index size on disk.
c) Vocabulary size (number of terms).
d) Number of temporary index segments written to disk (before merging).
e) Amount of time taken to start up an index searcher, after the final index is written to disk.
Note: consider the minimum data required by the searcher.

### amazon_reviews_us_Digital_Video_Games_v1_00.tsv.gz (26.2 MB)

a) 73.42232 seconds
b) 61750990.00000 Bs == 58.663 MBs
c) 75318
d) 11
e) 0.04935026168823242 seconds


# TODO:
estatisticas pos outros data sets e com map reduce
apontar para a linha q esta o termo no dict
ver a condicao de memoria melhor, ver pq é q a ram n diminui logo a seguir da escrita
