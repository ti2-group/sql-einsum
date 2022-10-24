# Supplement for the paper - Efficient and Portable Einstein Summation in SQL

## Graphical Models
This folder contains stand alone files to run an inference query computing for 100 
patients simultaneously if they have recurrent cancer. 

Before running the query we insert the graphical model parameter into the database.

## Requirements
See [requirements](../README.md#Requirements) of the whole repository.

## Usage
The repository contains multiple files, that all can run stand alone. 
You can run the Python file with 
````python
>>> python sat_hyper.py
sqlite result: [(0, 0, 0.694491778844999), (0, 1, 0.3055082211550009), ...
(computated in 0.3179582000000001s) - planning time: 0.00949079999999991s
````

**Note**: If you want to run the SQL-code in `gm_query.sql` you have beforehand to insert all the parameter values for the 
graphical model. You can do so by executing the SQL-code in `gm_insert.sql`.