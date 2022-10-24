# -*- coding: UTF-8 -*-
import os
from timeit import default_timer as timer

from tableauhyperapi import HyperProcess, Telemetry, CreateMode, Connection


def hyper_discussion():
    # load sql query
    sql_file = 'gm_query.sql'
    with open(sql_file, 'r') as file:
        query = file.read()

    # hyper compiled
    parameters = {
        "log_config": "",
        "max_query_size": "10000000000",
        "hard_concurrent_query_thread_limit": "1",
        "initial_compilation_mode": "o"  # o - optimize, v - virtual (interpreter), c - machine code not optimized
    }
    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU, parameters=parameters) as hyper:
        with Connection(hyper.endpoint, 'data.hyper', CreateMode.CREATE_AND_REPLACE) as connection:
            # insert data
            with open("gm_insert.sql", "r") as sql_insert_file:
                for line in sql_insert_file.readlines():
                    connection.execute_list_query(line)
            # query plan
            tic = timer()
            hyper_result = connection.execute_list_query("EXPLAIN " + query)
            toc = timer()
            time_explain_query = toc - tic
            # execute query
            tic = timer()
            hyper_result = connection.execute_list_query(query)
            toc = timer()
    print(f"hyper (compiled) result: {hyper_result}\n(computated in {toc - tic - time_explain_query}s) - planning time: {time_explain_query}")

    # hyper interpreted
    parameters = {
        "log_config": "",
        "max_query_size": "10000000000",
        "hard_concurrent_query_thread_limit": "1",
        "initial_compilation_mode": "v"  # o - optimize, v - virtual (interpreter), c - machine code not optimized
    }
    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU, parameters=parameters) as hyper:
        with Connection(hyper.endpoint, 'data.hyper', CreateMode.CREATE_AND_REPLACE) as connection:
            # insert data
            with open("gm_insert.sql", "r") as sql_insert_file:
                for line in sql_insert_file.readlines():
                    connection.execute_list_query(line)
            # query plan
            tic = timer()
            hyper_result = connection.execute_list_query("EXPLAIN " + query)
            toc = timer()
            time_explain_query = toc - tic
            # execute query
            tic = timer()
            hyper_result = connection.execute_list_query(query)
            toc = timer()
    print(f"hyper (interpreted) result: {hyper_result}\n(computated in {toc - tic - time_explain_query}s) - planning time: {time_explain_query}s")


if __name__ == "__main__":
    hyper_discussion()