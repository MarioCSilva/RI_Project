# Ranking Statistics for 2nd Assignment


| Dataset                                  |   Video Games      |     Video Games    |   Digital Music    |    Digital Music   |
|------------------------------------------|--------------------|--------------------|--------------------|--------------------|
| Ranking                                  |     Vector Space   |     BM25   |     Vector Space   |      BM25   |
| Index Schema                             |       lnc.ltc      |       :x:      |       lnc.ltc      |      :x:    |
| Minimum Length Filter: 3                 | ✔️ | ✔️ | ✔️ | ✔️ |
| Stop Words                               | ✔️ | ✔️ | ✔️ | ✔️ |
| Total indexing time                      |   71.27 seconds    |    66.98 seconds |    879.74 seconds   |     829.73 seconds   |
| Total index size on disk                 |    27.23 MBs       |    23.40 MBs     |    226.99 MBs   |    185.01 MBs   |
| Vocabulary size                          |     76513          |     76513        |     425072       |     425072       |
| Temporary index segments written to disk |       5            |       5          |       38         |       38         |
| Time to start up an index searcher       |    0.27 seconds    |    0.27 seconds  |    2.59 seconds  |    2.57 seconds  |
| Total time to handle 15 queries          |    1.92 seconds    |    1.72 seconds  |    10.45 seconds |    7.92 seconds |
| Average time to handle a single query    |    0.12 seconds    |    0.11 seconds  |    0.70 seconds  |    0.53 seconds  |



# Analysis of the Query Results

Regarding the query results we obtained for the `amazon_reviews_us_Digital_Music_Purchase_v1_00.tsv` dataset, we managed to gather some conclusions whether the most relevant documents that have been found for each of the queries made sense or not, according to the ranking strategy applied. 
Once again, the complete results of the queries using BM25 and Vector Space ( with lnc.ltc indexing schema) are stored in the `music_bm25` and `music_lncltc` folders, respetively, inside the `search_engine`subfolder.

# Query: 70's country music

## Vector Space ( lnc.ltc Indexing Schema)

### Top 2 Most Relevant:

R2FE5Y5CT334DH - Terms: 5, Relevant Terms: 3
    
    ['matter', 'love', "70's", "70's", "70's"]

RFZ57MNC19CTS - Terms: 14, Relevant Terms: 6

    ['time', 'country', 'hits', 'classic', 'hits', "50's", "60's", "70's", 'country', 'music', 'great', 'album', 'country', 'music']


### Least Relevant:

R33GU4BB8DOZ6B - Terms: 5, Relevant Terms: 1

    ['bop', 'five', 'stars', 'loved', "70's"]


The most relevant document has a considerable small number of terms, in which the word "70's" occurs three times.
As "70's" is a term that has a low frequency on the corpus compared to the terms 'music' and 'country' (smaller document frequency), the documents containing it will have more importance than these ones, due to the use of "idf" on the querying process.


## BM25

### Top 2 Most Relevant:

RFZ57MNC19CTS - Terms: 14, Relevant Terms: 6

    ['time', 'country', 'hits', 'classic', 'hits', "50's", "60's", "70's", 'country', 'music', 'great', 'album', 'country', 'music']


R29NDVL5G55OJM - Terms: 33, Relevant Terms: 8

    ['super', 'box', 'country', 'country', 'classics', "50's", "60's", "70's", "80's", 'country', 'music', 'creates', 'get', 'done', 'attitude', 'wanted', 'music', 'clean', 'spent', "70's", "80's", 'texas', 'album', 'goodies', 'enough', 'rhythm', 'keep', 'going', 'mixed', 'quality', 'music', 'performers', 'job']


### Least Relevant:

R1YN6QZMIEXDSC - Terms: 26, Relevant Terms: 3

    ['time', 'country', 'hits', 'classic', 'hits', "50's", "60's", "70's", 'purchase', 'get', 'songs', 'purchase', 'get', 'songs', 'really', 'catchy', 'songs', 'little', 'twangy', 'taste', 'really', 'refreshing', 'rock', 'passes', 'country', 'days']


With the BM25 Strategy we get results that seem a better fit to the given query, this because it takes into account the document length and the term frequency saturation. When compared to the Vector Space with lnc.ltc schema, BM25 does not reward as much the small documents that contain terms with smaller document frequencies, such as "70's".
