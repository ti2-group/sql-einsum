# Supplement for the paper - Efficient and Portable Einstein Summation in SQL

## Structure of the Repository

````
.
├── case_study                 # Stand alone files for some case studies of the paper
│   ├── discussion             # Stand alone files for the discussion section
│   ├── graphical_models       # Stand alone files for the graphical model experiments
│   └── quantum_circuits       # Stand alone files for the quantum circuits experiments
├── experiments                # Experimental files to reproduce the results of the paper
└── generate_sql_code          # Stand alone file for generating sql-code
````

__See each folder for more information.__

## Requirements
### Python and Anaconda
All files were tested using Python version 3.8 and Anaconda version 4.9.2  

Further we require the following Python packages.
* numpy (version 1.21.1)
* pandas (version 1.4.2)
* tableauhyperapi (version 0.0.13287)
* psycopg2 (version 2.9.3)
* sqlite (version 3.33.0)
* opt_einsum (version 3.3.0)
* rdflib (version 6.2.0)
* python-sat (version 0.1.7.dev19)

All packages can be installed using Anaconda and the yaml file with

 `conda env create -f environment.yml`
 
after this the environment is activated with

`conda activate exql`

and can be deleted with 

`conda env remove -n exql`.

### Postgres
The experiments further need a postgres DBMS installation. We used psql version 12.7. You can install postgres on linux using

````commandline
sudo apt-get install postgresql-12.11 postgresql-contrib-12.11
````
The postgres installation should have a 
database with the following configuaration:
* name: 'postgres',
* user: 'postgres',
* password: 'password',
* host: 'localhost'.
