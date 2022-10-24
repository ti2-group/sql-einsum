# Supplement for the paper - Efficient and Portable Einstein Summation in SQL

## Experiments
This folder contains all experiments from the experimental section of the publication. 
We have split the experiments into each subsection. 

## Requirements
See [requirements](../README.md#Requirements) of the whole repository.

Further you need to unzip the file `experiments/rdf_queries/olympics-nt-nodeup.zip`.

## Online Interface
We have an online interface for creating SQL queries from einstein notation. You can check it out at 
https://sql-einsum.ti2.uni-jena.de/.

## Usage 
You can start the experiments with 
````commandline
python run_experiments.py
````

This command starts all experiments. You can uncomment the experiments you do not
want to run:
````python
# comment or uncomment the experiment you want to exclude or include

# quantum circuit experiments
quantum_use_case(depth=8, iterations=iterations, verbose=verbose)
quantum_use_case(nbits=10, iterations=iterations, verbose=verbose)

# rdf experiments
run_rdf_experiment(iterations=iterations, verbose=verbose)

# sat experiments
run_sat_experiment(iterations=iterations, verbose=verbose)

# graphical model experiments
run_gm_query_experiment(iterations=iterations, verbose=verbose)
````