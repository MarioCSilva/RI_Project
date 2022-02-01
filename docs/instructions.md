## How to run

Inside the RI_Project directory:

- Run the command to install requirements:
```bash
pip3 install -r requirements.txt
```

- Add to a directory called `dataset` the files that contain the documents to be indexed.

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
    -ranking <Ranking Algorithm:str> Choices: BM25 or VS           
    -queries_file <File Name (Path) for Queries:str>            
    -k1 <k1 value for BM25:float>            
    -b <B value for BM25:float>            
    -schema <Indexing Schema:str> Example: lnc.ltc            
    -boost <Use Ranking Boost function>            
    -window_size <Window Size to be used on Boost Function: int>  
```

- For a more complex running example consider the following one. 
  - Indexing:
    ```bash
    python3 main.py -index_dir example -stopwords -min_len -len 3 -positions
    ```

  - Searching:
    ```bash
    python3 main.py -index_dir example -search -boost
    ```

## Important Notes
- For the second assignment the `Map Reduce` option  was not updated, thus it is only working for the purposes of the first assignment

- The results of the queries using BM25 and Vector Space ( with lnc.ltc indexing schema) are stored in the `music_bm25` and `music_vs_lncltc` folders, respectively, inside the `search_engine` subfolder. To be able to obtain the same queries results, the arguments for the indexation process that were used can also be seen inside the `config` subfolder.