# Supplement for the paper - Efficient and Portable Einstein Summation in SQL

## Quantum Circuits
This folder contains stand alone files to run a quantum circuit with 2 qbits and 8 layers for each data base management system and `opt_einsum` 
individually. 

## Requirements
See [requirements](../README.md#Requirements) of the whole repository.

## Usage
The repository contains multiple files, that all can run stand alone. 
You can run the Python file with 
``````python
>>> python qc_sqlite.py
sqlite result: [(0, 0, -0.4785533905932733, -0.05177669529663631), ...
(computated in 0.004108200000000006s) - planning time: 0.003703000000000012s
``````