# Supplement for the paper - Efficient and Portable Einstein Summation in SQL

## Olympics data set
We use a cleaned and restructured olympics data set. The original data set can be found at https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results
and is under the CC0: Public Domain licence. If you are interested in the restructurung we refer to https://medium.com/wallscope/creating-linked-data-31c7dd479a9e.

Since the olympic data set is quite large we provide it as a zip file (the Dockerfile has a RUN command unzipping the file).
After unzipping the file `olympics-net-nodeup.zip` contains 1781625 rows, each containing a subject-predicate-object triple. 

For example the row 
````python
<http://wallscope.co.uk/resource/olympics/athlete/BlavonLasTorres> <http://dbpedia.org/ontology/team> <http://wallscope.co.uk/resource/olympics/team/Hungary> .
````
contains the information, that the athlete Blavon Las Torres is in the Hungarian team. Each row of the `olympics.nt` looks similiar with different uniform resource identifier (URIs). In total the file contains 544170 different URIs.
