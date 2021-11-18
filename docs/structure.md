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

    This structure is a dictionary with the terms as key, and as value, the document frequency, as well as the line the term is on the partition file.


## Class Tokenizer:

This class will process the documents and return all terms found and the positions of these.

- Allows the user of three type of filters, which can be used simultaneously. Those filters are the minimum length filter, the Stop Words Filter and Snowball Stemmer Filter. The minimum length filter allows only the processing of terms with the minimum length wished. The Stop Words filter has the goal of ignoring certain words, the Stop Words, such as articles, prepositions, pronouns or conjunctions. Finally, the Snowball Stemmer Filter is available to do the stemming of the terms, in other words, reduces words by removing its prefixes and suffixes.

        
- The tokenization function makes the all terms lower cased, then, it replaces any terms that contain only digits, and also unwanted symbols.

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

- Overhead - there is only benefit of using map reducing when the cost of transferring information from processes is much smaller to the processing that is executed in the functions of mapping and reducing. It also should be used in different machines and not in a single computer to take the most benefit out of it. In out case, the overhead of creating processes and data transferring between processes could be too big for the operations that are executed. However we will analyze the results on the Statistics part.


## Class Search Engine:

- Once the Indexing of a certain dataset has finished, using the Search Engine module, it is possible to query a term, and check its number of occurrences. Besides this, the total time needed to load the indexer is outputted.
