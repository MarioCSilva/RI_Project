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

# TODO:
# Analysis of Query Results
# meter comentarios no codigo i guess
# talvez escrever temporariamente os dict (shotless)