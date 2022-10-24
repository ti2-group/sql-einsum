# -*- coding: UTF-8 -*-
import os
from timeit import default_timer as timer

import psycopg2 as psy


def postgres_discussion():
    # load sql query
    sql_file = 'gm_query.sql'
    with open(sql_file, 'r') as file:
        query = file.read()

    # connect to the database
    conn = psy.connect(user='postgres', password='password', database='postgres', host='localhost')
    conn.set_isolation_level(psy.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # insert data
    with open("gm_insert.sql", "r") as sql_insert_file:
        for line in sql_insert_file.readlines():
            cur.execute(line)

    # Planning Time
    analyze_query = "EXPLAIN " + query
    postgres_planning_time = 0.0
    tic = timer()
    cur.execute(analyze_query)
    report = cur.fetchall()
    toc = timer()
    time_explain_query = toc - tic

    # execute query
    tic = timer()
    cur.execute(query)
    postgres_result = cur.fetchall()
    toc = timer()
    # close connection
    cur.close()
    conn.close()

    print(f"postgres result: {postgres_result}\n(computated in {toc - tic - time_explain_query}s) - planning time: {time_explain_query}s")


if __name__ == "__main__":
    postgres_discussion()