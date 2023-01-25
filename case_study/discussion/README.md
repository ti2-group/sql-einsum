# Supplement for the paper - Efficient and Portable Einstein Summation in SQL

## Discussion
This folder contains stand alone files to run the computation for the discussion section for each data base management system and `opt_einsum` 
individually. The einstein notation compuates the number of soluations of a conjugation normal form with 952 clauses.

Interestingly the computation in HyPer is more performant then in Python. This can be explained through the intermediate computations that are performed by the einstein summation. `sat_intermediate_calculations.txt` shows, that for those intermediate computations the high dimensional intermediate results are quite sparse. 
 
For example the following excerpt shows this behavior. The left operatnd has around 1 to 3 percent of non zero values (nnz = number non zero).

```
+--------------------------------------------------+------------------------+-----------------------+------------------------+

|                     formula                      |   operand 1 nnz (%)    |   operand 2 nnz (%)   |     result nnz (%)     |

+--------------------------------------------------+------------------------+-----------------------+------------------------+

...

|       ĪÁŁĔĤŚieÙñĲŸƮŵÅ,ÅÄ->ĪÁŁĔĤŚieÙñĲŸƮŵÅÄ       |   936 / 32768 (2.86)   |     3 / 4 (75.00)     |  1512 / 65536 (2.31)   |

|      ĪÁŁĔĤŚieÙñĲŸƮŵÅÄ,ÄÃ->ĪÁŁĔĤŚieÙñĲŸƮŵÅÄÃ      |  1512 / 65536 (2.31)   |     3 / 4 (75.00)     |  2088 / 131072 (1.59)  |

|     ĪÁŁĔĤŚieÙñĲŸƮŵÅÄÃ,ĔÃ->ĪÁŁĔĤŚieÙñĲŸƮŵÅÄÃ      |  2088 / 131072 (1.59)  |     3 / 4 (75.00)     |  1872 / 131072 (1.43)  |

|     ĪÁŁĔĤŚieÙñĲŸƮŵÅÄÃ,ÄÀ->ĪÁŁĔĤŚieÙñĲŸƮŵÅÄÃÀ     |  1872 / 131072 (1.43)  |     3 / 4 (75.00)     |  2808 / 262144 (1.07)  |

|    ĪÁŁĔĤŚieÙñĲŸƮŵÅÄÃÀ,ÀĤ->ĪÁŁĔĤŚieÙñĲŸƮŵÅÄÃÀ     |  2808 / 262144 (1.07)  |     3 / 4 (75.00)     |  2520 / 262144 (0.96)  |
```


## Requirements
See [requirements](../README.md#Requirements) of the whole repository.

## Usage
The repository contains multiple files, that all can run stand alone. 
You can run the Python file with 
````commandline
>>> python qc_sqlite.py
sqlite result: [(3.6969306313365856e+26,)]
(computated in 1.1461116s) - planning time: 0.1041782s

````

Each file returns the result of the computation and the computation time without planning. 
The data base management systems also compute the planning time for the sql query.
