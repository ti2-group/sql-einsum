# Supplement for the paper - Efficient and Portable Einstein Summation in SQL

You will find information about our group and other projects at [ti2.uni-jena.de](https://ti2.uni-jena.de/). 

If you are not familiar with einstein summation, good entrypoints are the article [Einstein Summation in NumPy](https://obilaniu6266h16.wordpress.com/2016/02/04/einstein-summation-in-numpy/) or [Einsum](https://rockt.github.io/2018/04/30/einsum).

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
_For a docker setup see below._
### Python and Anaconda
All files were tested using Python version 3.8 and Anaconda version 4.9.2  

Further we require the following Python packages.
* numpy (version 1.21.1)
* pandas (version 1.4.2)
* tableauhyperapi (version 0.0.13287)
* psycopg2 (version 2.9.3)
* opt_einsum (version 3.3.0)
* rdflib (version 6.2.0)
* python-sat (version 0.1.7.dev19)

All packages can be installed using Anaconda and the yaml file with

 `conda env create -f environment.yml`
 
after this the environment is activated with

`conda activate sql-einstein`

and can be deleted with 

`conda env remove -n sql-einstein`.

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

## Docker Setup
We also support a docker setup. A `Dockerfile` is available and can be build with
````commandline
docker build -t sql-einstein .
````
After building you can run the docker container with
````commandline
docker run --rm -it sql-einstein
````
This command removes (`--rm`) the container after execution. Also it runs the script `startup.sh` as an entrypoint. This script
does start the postgres server.

After running the `docker run ...` command you will be prompted with an interactive shell 
where you can run experiments as described in each subfolder. 
For a quickstart you can run 

````commandline
cd experiments
python run_experiments
````

to start all experiments or

````commandline
cd case_study/quantum_circuits
python qc_sqlite.py
````

to start the quantum circuit sqlite experiment.
