# Query Ranking Statistics for the 3rd Assignment

## Vector Space without Boost Function

Time to start up an index searcher, after the final index is written to disk: 1.77 seconds

Total time to handle 15 queries: 10.08 seconds

Average time to handle a single query: 0.67 seconds

Average Query Throughput: 1.49 queries/second

Median Query Latency: 0.39 seconds

Mean Values Over All Queries:

|   Top K |   Precision |   Recall |   F-Measure |   Avg. Precision |     NDCG |
|---------|-------------|----------|-------------|------------------|----------|
|      10 |    0.98     | 0.136045 |    0.238361 |         0.97428  | 0.866399 |
|      20 |    0.983333 | 0.27303  |    0.425819 |         0.972697 | 0.875603 |
|      50 |    0.894667 | 0.615518 |    0.725592 |         0.870808 | 0.884981 |


## Vector Space with Boost Function

Time to start up an index searcher, after the final index is written to disk: 1.68 seconds

Total time to handle 15 queries: 17.30 seconds

Average time to handle a single query: 1.15 seconds

Average Query Throughput: 0.87 queries/second

Median Query Latency: 1.25 seconds

Mean Values Over All Queries:

|   Top K |   Precision |   Recall |   F-Measure |   Avg. Precision |     NDCG |
|---------|-------------|----------|-------------|------------------|----------|
|      10 |    0.986667 | 0.136889 |    0.23986  |         0.982066 | 0.876623 |
|      20 |    0.983333 | 0.27303  |    0.425819 |         0.973863 | 0.882996 |
|      50 |    0.894667 | 0.615152 |    0.725379 |         0.87201  | 0.89108  |


## BM25 without Boost Function

Time to start up an index searcher, after the final index is written to disk: 1.60 seconds

Total time to handle 15 queries: 7.55 seconds

Average time to handle a single query: 0.50 seconds

Average Query Throughput: 1.99 queries/second

Median Query Latency: 0.26 seconds

Mean Values Over All Queries:

|   Top K |   Precision |   Recall |   F-Measure |   Avg. Precision |     NDCG |
|---------|-------------|----------|-------------|------------------|----------|
|      10 |    0.886667 | 0.122181 |    0.214248 |         0.862246 | 0.761467 |
|      20 |    0.79     | 0.216159 |    0.33817  |         0.75241  | 0.726889 |
|      50 |    0.625333 | 0.426095 |    0.504385 |         0.552623 | 0.688719 |


## BM25 with Boost Function

Time to start up an index searcher, after the final index is written to disk: 1.47 seconds

Total time to handle 15 queries: 40.64 seconds

Average time to handle a single query: 2.71 seconds

Average Query Throughput: 0.37 queries/second

Median Query Latency: 2.85 seconds

Mean Values Over All Queries:

|   Top K |   Precision |   Recall |   F-Measure |   Avg. Precision |     NDCG |
|---------|-------------|----------|-------------|------------------|----------|
|      10 |    0.96     | 0.133202 |    0.233385 |         0.947225 | 0.805324 |
|      20 |    0.913333 | 0.25178  |    0.393266 |         0.892151 | 0.791467 |
|      50 |    0.725333 | 0.493483 |    0.584507 |         0.667357 | 0.744143 |