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
    -index_dir <Directory name for indexation:str>
    -filename <File Name (Path) for data set:str>
    -min_length <Minimum Length Filter>
    -length <Length for Minimum Length Filter:int>
    -porter <Porter Stemmer Filter>
    -stopwords <Stop Words Filter>
    -stopwords_file <Stop Words File>
    -mp <Map Reduce>
    -positions <Store term's positions in postings>
    -search <Search Engine to Get Queries Results>
    -ranking <Ranking Algorithm:str>
    -queries_file <File Name (Path) for Queries:str>
    -k1 <k1 value for BM25:float>
    -b <B value for BM25:float>
    -schema <Indexing Schema:str> Example: lnc.ltc
```

- For a more complex running example consider the following one. 
  - Indexing:
    ```bash
    python3 main.py -index_dir example_games_lncltc -schema lnc.ltc -min -len 3
    ```

  - Searching:
    ```bash
    python3 main.py -index_dir example_games_lncltc -search -queries_file ../queries.txt
    ```

## Important Notes
- For this assignment the `Map Reduce` option  was not updated, thus it is only working for the purposes of the first assignment

- The results of the queries using BM25 and Vector Space ( with lnc.ltc indexing schema) are stored in the `music_bm25` and `music_lncltc` folders, respetively,inside the `search_engine`subfolder.