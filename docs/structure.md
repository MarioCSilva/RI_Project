## Class Indexer:

This class has the main goal to index all terms found on each dataset, and write them to disk so they can be used for search queries later.

- Parse file and index terms and postings:

    Starts off by parsing the file and obtain all tokens, recurring to the Tokenizer Class, as well as its documents references and, optionally, the positions on those documents.

- Write postings to temporary block files (terms sorted alphabetically):

    While the parse and indexing process is taking place, every time a threshold of memory used (RAM), or a certain number of tokens processed has been reached, it begins the write operations of the postings on disk through temporary blocks. The postings that are being written are all ordered alphabetically.

- Merge all temporary block files:

    Opens all temporary block files and reads line by line, finds the smallest (alphabetically) term, and adds it to an Ordered Dictionary structure of python. This way, the terms are sorted on the fly and then when writing a partition to disk, there is no need for sorting the terms since they were inserted in a correct order. This partition files are also compressed so occupy less space on disk.

- Delete all temporary block files.

    After the merge operation has been completed, the temporary blocks are no longer needed and thus deleted from the disk.

- Store indexer data structure in a file:

    This structure is a dictionary with the terms as key, and as value, the document frequency, as well as the line the term is written on the partition file.

- Store Document Mapper structure in a file:

    This structure is a dictionary with a compact incremental ID, using all ASCII characters, as key, and the review ID as value.
    This allows to use much less space in disk because it shortens the ID's to the smallest value possible in order to occupy less bytes.

- Store configuration metadata for the search engine:
    Once the merge has been completed, a new directory and consequently a new file is created on disk containing metadata that will be useful for the Search Engine, such as which filters were used, ranking strategy choosen and others.
    


## Class Tokenizer:

This class will process the documents and return all terms found and the positions of these.

- Allows the user of three type of filters, which can be used simultaneously. Those filters are the minimum length filter, the Stop Words Filter and Snowball Stemmer Filter. The minimum length filter allows only the processing of terms with the minimum length wished. The Stop Words filter has the goal of ignoring certain words, the Stop Words, such as articles, prepositions, pronouns or conjunctions. Finally, the Snowball Stemmer Filter is available to do the stemming of the terms, in other words, reduces words by removing its prefixes and suffixes.
        
- The tokenization function makes the all terms lower cased, then, it replaces any terms that contain only digits, and also unwanted symbols.

- Removes words bigger than 27 characters, because the longest word in the English language featuring alternating consonants and vowels and longest word word in Shakespeare's works has 27 characters.

## Class Map Reducer:

- The MapReducer class can be used as a way of indexing all terms in distributed manner using the Map Reduce Strategy. To do so there are three different stages: Mapping, Partitioning and Reducing.

- This class initializes a certain amount of processes, default is currently the number of CPUs of the machine the algorithm is running, and half of them are used to Map and other half to Reduce. It also uses queues to transfer information between processes.

- The Mapping stage:

    This stage collects all terms, the documents where those have appeared and its positions, and stores them in a dictionary of dictionaries as suggested bellow. This step is very important since it uses the tokenization function which can be a big CPU intensive function. Each mapping corresponds to the process of one document.

```
{ term: { doc_id_1: [2,3,4] } }
{ term: { doc_id_2: [6,4] } }
```

This task is computed simultaneously by 4 processes that are launched with this goal. Each output is sent to the next stage, the partitioning.

- The Partitioning stage:
    
    This stage will only be executed once all processes have done the mapping function over all documents and returned the mapped terms. The objective of this step is to organize the mapped values for the reducing step to use them, in this case, we will group all documents on a single entry (term), as suggested bellow:

```
{ term: { doc_id_1: [2,3,4], doc_id_2: [6,4] } }
```

- The Reducing Stage:

    The final stage, the Reducing, aims to compute the total number of occurrences of each term in all documents, by  organizing the data in the following structure.

```
( term, { doc_id_1: [2,3,4], doc_id_2: [6,4] }, 5)
```

- Overhead - there is only benefit of using map reducing when the cost of transferring information from processes is much smaller to the processing that is executed in the functions of mapping and reducing. It also should be used in different machines and not in a single computer to take the most benefit out of it. In our case, the overhead of creating processes and data transferring between processes could be too big for the operations that are executed. However we will analyze the results on the Statistics part.


## Class Search Engine:

- Once the Indexing of a certain dataset has finished, using the Search Engine module, it is possible to read a file with queries.

- To do so, this module starts by reading a configuration  containing all relevant characteristics for the indexing process(usage of filters, ranking strategy, indexing schema,..).

- After that it loads the indexer data structure, which is a dictionary with every term indexed as key and for the value it has the idf associated to the term and it also has the line that the postings list of this term was written.

- To get the document scores of a term, first it is necessary to get partition file by comparing the term with the first word of a partition file and the last word to find which partition file the term is indexed. After that, it needs to get the postings list of the term, which is done by reading every line until the line that is obtained from the indexer data structure mentioned before. Then it calculates the documents scores based on the ranking system.

- A Least Recently Used Cache is used to store, in our case, 50, the document scores associated to the term from the queries that are being processed. Ideally should be the most recurrent terms in all searchs queries, but since we don't have a query log to analyze this, it is a simple cache that stores the last ones.

- The results of the top 100 most relevant documents with the highest scores, acording to the ranking strategy that has been choosen from the user back on the indexation process, are written on the choosen indexing directoring, on the `search_engine` subfolder.
