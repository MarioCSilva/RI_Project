# Indexation Statistics for 1st Assignment

In this part we gather statistics like the following:

a) Total indexing time. (No filters)

b) Total index size on disk.

c) Vocabulary size (number of terms).

d) Number of temporary index segments written to disk (before merging).

e) Amount of time taken to start up an index searcher, after the final index is written to disk.


### Dataset: amazon_reviews_us_Digital_Video_Games_v1_00.tsv.gz (26.2 MB)

|                                          | Run #1             | Run #2             | Run #3             | Run #4             | Run #5             |
|------------------------------------------|--------------------|--------------------|--------------------|--------------------|--------------------|
| Minimum Length Filter: 3                 | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ |
| Stop Words Filter                        |         ❌        |         ❌        | ✔️ |         ❌        |         ❌        |
| Snowball Stemmer Filter                  |         ❌        | ✔️ | ✔️ |         ❌        | ✔️ |
| Map Reduce                               |         ❌        |         ❌        |         ❌        | ✔️ | ✔️ |
| Total indexing time                      |    38.2 seconds    |    97.6 seconds    |    92.9 seconds    |    164.2 seconds   |    212.1 seconds   |
| Total index size on disk                 |     47.834 MBs     |     46.545 MBs     |     33.674 MBs     |     47.844 MBs     |     46.555 MBs     |
| Vocabulary size                          |        70407       |        49332       |        49265       |        70402       |       49326      |
| Temporary index segments written to disk |          6         |          6         |          4         |          2         |          2         |
| Time to start up an index searcher       |  0.0894 seconds  |    0.0679 seconds    |   0.0797 seconds   |   0.0832 seconds   |   0.0780 seconds   |

From these results, we are able to observe the difference in a few aspects.

- The stop words filter can have a big impact even though it only ignores 67 terms from being processed, it reduces by 27.7% the total index size on disk, because these words are very common and have huge posting lists.

- The usage of the snowball stemmer filter has a big impact on the total indexing time due to it's high computational cost, but reduces significantly the vocabulary size, which may be relevant for search queries.

- With the map reduce method, because of the overhead costs, explained more in detail in the Structure section, it has bigger total indexing times, however, the difference of total indexing time between map reduce with low CPU intensive operations during tokenization (using only minimum length Filter) and a higher CPU intensive (with snowball stemmer Filter) is much smaller when compared to the indexation with the normal algorithm, thus, the time went up by 29.2% and the normal algorithm went up by 155.5%.


### Dataset: amazon_reviews_us_Digital_Music_Purchase_v1_00.tsv.gz (241.8 MB)

|                                          | Run #1             | Run #2             | Run #3             |
|------------------------------------------|--------------------|--------------------|--------------------|
| Minimum Length Filter: 3                 | ✔️ | ✔️ | ✔️ |
| Stop Words Filter                        |         ❌        |         ❌        |         ❌        |
| Snowball Stemmer Filter                  |         ❌        | ✔️ |  ✔️ |
| Map Reduce                               |         ❌        |         ❌        | ✔️ |
| Total indexing time                      |    9.8 minutes    |  19.8 minutes  |  25.5 minutes  |
| Total index size on disk                 |    411.621 MBs    |   403.723 MBs  |   403.735 MBs   |
| Vocabulary size                          |      330690       |    265154      |    265154     |
| Temporary index segments written to disk |         46        |        45      |       17      |
| Time to start up an index searcher       |   0.9606 seconds  |   0.5429 seconds   |  0.4480 seconds  |

- Here we can see that the overhead of the map reducer is still too costly for these kind of operations, if it was able to process less temporary segments, meaning that it would process more quantity of data each time it is called, it would be able to benefit more. Instead of 17 temporary index segments, if it had around 4, chances are it would be even faster, however we were not able to test it because of deadlocks that happen whenever the queues that share data between processes get too large.


### Dataset: amazon_reviews_us_Music_v1_00.tsv.gz(1.4GB)

|                                          | Run #1             |
|------------------------------------------|--------------------|
| Minimum Length Filter: 3                 | ✔️ |
| Stop Words Filter                        |         ❌        |
| Snowball Stemmer Filter                  |         ❌        |
| Map Reduce                               |         ❌        |
| Total indexing time                      |    68.3 minutes   |
| Total index size on disk                 |    2650.859 MBs   |
| Vocabulary size                          |     1133257       |
| Temporary index segments written to disk |        293        |
| Time to start up an index searcher       |   3.8156 seconds  |


### Dataset: amazon_reviews_us_Books_v1_00.tsv.gz (2.6 GB)

|                                          | Run #1             |
|------------------------------------------|--------------------|
| Minimum Length Filter: 3                 | ✔️ |
| Stop Words Filter                        |         ❌        |
| Snowball Stemmer Filter                  |         ❌        |
| Map Reduce                               |         ❌        |
| Total indexing time                      |    85.6 minutes   |
| Total index size on disk                 |    4353.265 MBs   |
| Vocabulary size                          |     1328795       |
| Temporary index segments written to disk |       482         |
| Time to start up an index searcher       |    4.4627 seconds        |
