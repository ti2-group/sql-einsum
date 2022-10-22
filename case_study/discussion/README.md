# Supplement for the paper - Efficient and Portable Einstein Summation in SQL

## Discussion
This folder contains stand alone files to run the computation for the discussion section for each data base management system and `opt_einsum` 
individually. The einstein notation compuates the number of soluations of a conjugation normal form with 952 clauses.

## Requirements
See [requirements](../README.md#Requirements) of the whole repository.

## Usage
The repository contains multiple files, that all can run stand alone. 
You can run the Python file with 
````commandline
python qc_sqlite.py

    sqlite result: [(3.6969306313365856e+26,)] (computated in 1.1360257999999999s) - planning time: 0.1073153s
````

Each file returns the result of the computation and the computation time without planning. 
The data base management systems also compute the planning time for the sql query.