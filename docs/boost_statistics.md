# Query Ranking Statistics for the 3rd Assignment

## Vector Space without Boost Function

Time to start up an index searcher, after the final index is written to disk: 1.63 seconds

Total time to handle 15 queries: 8.52 seconds

Average time to handle a single query: 0.57 seconds

Average Query Throughput: 1.76 queries/second

Median Query Latency: 0.34 seconds

Mean Values Over All Queries:

|   Top K |   Precision |   Recall |   F-Measure |   Avg. Precision |     NDCG |
|---------|-------------|----------|-------------|------------------|----------|
|      10 |    0.94     | 0.130497 |    0.228615 |         0.919725 | 0.839183 |
|      20 |    0.93     | 0.258418 |    0.40288  |         0.91066  | 0.833954 |
|      50 |    0.850667 | 0.585557 |    0.689928 |         0.818631 | 0.84357  |


## Vector Space with Boost Function

Time to start up an index searcher, after the final index is written to disk: 1.68 seconds

Total time to handle 15 queries: 17.30 seconds

Average time to handle a single query: 1.15 seconds

Average Query Throughput: 0.87 queries/second

Median Query Latency: 1.25 seconds

Mean Values Over All Queries:

|   Top K |   Precision |   Recall |   F-Measure |   Avg. Precision |     NDCG |
|---------|-------------|----------|-------------|------------------|----------|
|      10 |    0.94     | 0.130497 |    0.228615 |         0.920836 | 0.85067  |
|      20 |    0.926667 | 0.257325 |    0.401234 |         0.907728 | 0.839027 |
|      50 |    0.846667 | 0.581814 |    0.686051 |         0.816521 | 0.846974 |


## BM25 without Boost Function

Time to start up an index searcher, after the final index is written to disk: 1.62 seconds

Total time to handle 15 queries: 7.74 seconds

Average time to handle a single query: 0.52 seconds

Average Query Throughput: 1.94 queries/second

Median Query Latency: 0.29 seconds

Mean Values Over All Queries:

|   Top K |   Precision |   Recall |   F-Measure |   Avg. Precision |     NDCG |
|---------|-------------|----------|-------------|------------------|----------|
|      10 |    0.86     | 0.118459 |    0.207714 |         0.836706 | 0.750858 |
|      20 |    0.766667 | 0.210028 |    0.328444 |         0.732444 | 0.713823 |
|      50 |    0.605333 | 0.411407 |    0.48744  |         0.539773 | 0.67222  |


## BM25 with Boost Function

Time to start up an index searcher, after the final index is written to disk: 1.60 seconds

Total time to handle 15 queries: 15.85 seconds

Average time to handle a single query: 1.06 seconds

Average Query Throughput: 0.95 queries/second

Median Query Latency: 1.12 seconds

Mean Values Over All Queries:

|   Top K |   Precision |   Recall |   F-Measure |   Avg. Precision |     NDCG |
|---------|-------------|----------|-------------|------------------|----------|
|      10 |    0.86     | 0.118173 |    0.20728  |         0.832862 | 0.750627 |
|      20 |    0.77     | 0.211262 |    0.330246 |         0.733582 | 0.711687 |
|      50 |    0.594667 | 0.403652 |    0.478481 |         0.533248 | 0.665441 |