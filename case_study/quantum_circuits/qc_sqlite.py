# -*- coding: UTF-8 -*-
import os
from timeit import default_timer as timer

import sqlite3


def sqlite_discussion():
    # load sql query
    sql_file = 'qc_query.sql'
    with open(sql_file, 'r') as file:
        query = file.read()

    # connect to database
    con = sqlite3.connect(':memory:')
    cur = con.cursor()
    # execute query
    tic = timer()
    cur.execute("EXPLAIN QUERY PLAN " + query)
    con.commit()
    cur.fetchall()
    toc = timer()
    time_explain_query = (toc - tic)

    tic = timer()
    sqlite_result = cur.execute(query)
    con.commit()
    sqlite_result = sqlite_result.fetchall()
    toc = timer()

    # close connection
    con.commit()
    con.close()

    print(f"sqlite result: {sqlite_result}\n(computated in {toc - tic - time_explain_query}s) - planning time: {time_explain_query}s")


if __name__ == "__main__":
    sqlite_discussion()