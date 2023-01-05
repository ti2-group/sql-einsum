FROM frolvlad/alpine-miniconda3

# set meta information
LABEL maintainer ="Julien Klaus <julien.klaus@uni-jena.de>"

# create the working directory
RUN mkdir /sql-einstein
WORKDIR /sql-einstein

# set meta information
ARG conda_env=sql-einstein

# create the environment
COPY environment.yml .
RUN conda init
RUN conda env create -f environment.yml
ENV PATH /opt/conda/envs/$conda_env/bin:$PATH
ENV CONDA_DEFAULT_ENV $conda_env

# install and configure postgres (https://luppeng.wordpress.com/2020/02/28/install-and-start-postgresql-on-alpine-linux/)
RUN apk update && apk add postgresql postgresql-client postgresql-contrib
RUN (addgroup -S postgres && adduser -S postgres -G postgres || true)
RUN mkdir -p /run/postgresql
RUN chown postgres:postgres /run/postgresql

USER postgres
RUN mkdir -p /var/lib/postgresql/data
RUN chmod 0700 /var/lib/postgresql/data
RUN initdb -D /var/lib/postgresql/data
RUN echo "host all all 127.0.0.0/0 md5" >> /var/lib/postgresql/data/pg_hba.conf
RUN sed -i "s/unix_socket_directories = '\/run\/postgresql'/unix_socket_directories = '\/tmp'/g" /var/lib/postgresql/data/postgresql.conf

# copy all remaining data
COPY . .

# unzip the Olympus dataset
USER root
RUN apk add unzip --no-cache
RUN unzip experiments/rdf_queries/olympics-nt-nodup.zip -d experiments/rdf_queries/
RUN touch /usr/bin/startup.sh
RUN echo "#!/bin/sh" >> /usr/bin/startup.sh
RUN echo "su - postgres -c 'pg_ctl start -D /var/lib/postgresql/data/'" >> /usr/bin/startup.sh
RUN echo "export PYTHONPATH='$PWD'" >> /usr/bin/startup.sh
RUN echo "sh" >> /usr/bin/startup.sh
RUN chmod +x /usr/bin/startup.sh

RUN export PYTHONPATH="$PWD"
