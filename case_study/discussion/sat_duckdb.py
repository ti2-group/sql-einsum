# -*- coding: UTF-8 -*-
import os
from timeit import default_timer as timer

import duckdb


def duckdb_discussion():
    # load sql query
    sql_file = 'sat_query_952.sql'
    with open(sql_file, 'r') as file:
        query = file.read()

    con = duckdb.connect(database=':memory:', read_only=False)

    # disable optimization
    con.execute("PRAGMA disable_optimizer")

    tic = timer()
    con.execute("EXPLAIN " + query)
    duck_db_result = con.fetchall()
    toc = timer()
    time_explain_query = toc - tic

    tic = timer()
    con.execute(query)
    duckdb_result = con.fetchall()
    toc = timer()
    print(f"duckdb result: {duckdb_result}\n(computated in {toc - tic - time_explain_query}s) - planning time: {time_explain_query}s")


if __name__ == "__main__":
    duckdb_discussion()
