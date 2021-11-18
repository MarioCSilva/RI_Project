In this part we gather statistics like the following:

a) Total indexing time. (No filters)

b) Total index size on disk.

c) Vocabulary size (number of terms).

d) Number of temporary index segments written to disk (before merging).

e) Amount of time taken to start up an index searcher, after the final index is written to disk.


### amazon_reviews_us_Digital_Video_Games_v1_00.tsv.gz (26.2 MB)

|                                          | Run #1             | Run #1             | Run #3             | Run #4             | Run #5             |
|------------------------------------------|--------------------|--------------------|--------------------|--------------------|--------------------|
| Minimum Length Filter: 3                 | ✔️ | ✔️ | ✔️ | ✔️ | ✔️ |
| Stop Words Filter                        |         ❌        |         ❌        | ✔️ |         ❌        |         ❌        |
| Snowball Stemmer Filter                  |         ❌        | ✔️ | ✔️ |         ❌        | ✔️ |
| Map Reduce                               |         ❌        |         ❌        |         ❌        | ✔️ | ✔️ |
| Total indexing time                      |    38.2 seconds    |    97.6 seconds    |    92.9 seconds    |    164.2 seconds   |    212.1 seconds   |
| Total index size on disk                 |     47.834 MBs     |     46.545 MBs     |     33.674 MBs     |     47.844 MBs     |     46.555 MBs     |
| Vocabulary size                          |        70455       |        49372       |        49305       |        70455       |        49372       |
| Temporary index segments written to disk |          6         |          6         |          4         |          2         |          2         |

e) 0.04935026168823242 seconds
