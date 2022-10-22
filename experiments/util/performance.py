
from timeit import default_timer as timer
from itertools import product

import numpy as np
import opt_einsum as oe
from tableauhyperapi import HyperProcess, Telemetry, CreateMode, Connection
import sqlite3
import psycopg2 as psy

from pysat.formula import CNF
from pysat.solvers import Solver


def _get_sizes(einsum_notation, tensors):
    index_sizes = {}
    for einsum_index, tensor in zip(einsum_notation.split("->")[0].split(","), tensors):
        for index, dimension in zip(list(einsum_index), list(np.array(tensor).shape)):
            if not index in index_sizes:
                index_sizes[index] = dimension
            else:
                if index_sizes[index] != dimension:
                    raise Exception(f"Dimension error for index '{index}'.")
    return index_sizes


def get_opt_einsum_gm_performance(einsum_notation, tensors, tensor_names=None, evidence=None, iterations=10, verbose=False):
    opt_rg = oe.RandomGreedy(max_repeats=256, parallel=True)
    index_sizes = _get_sizes(einsum_notation, tensors)
    views = oe.helpers.build_views(einsum_notation, index_sizes)
    path, path_info = oe.contract_path(einsum_notation, *views, optimize=opt_rg)

    # constant arrays
    sum_mask = np.array([1, 1])
    for _ in range(iterations):
        oe_result = oe.contract(einsum_notation, *tensors, optimize=path)
        # calculate the probability for class=1
        oe_result = oe_result / np.outer(oe_result.dot(sum_mask), sum_mask)
    tic = timer()
    # constant arrays
    sum_mask = np.array([1, 1])
    for _ in range(iterations):
        oe_result = oe.contract(einsum_notation, *tensors, optimize=path)
        # calculate the probability for class=1
        oe_result = oe_result / np.outer(oe_result.dot(sum_mask), sum_mask)
    toc = timer()
    if verbose: print(f"opt_einsum: {1 / ((toc - tic) / iterations)} iterations per second.")
    return 1 / ((toc - tic) / iterations), oe_result, path_info


def get_opt_einsum_performance(einsum_notation, tensors, tensor_names=None, evidence=None, iterations=10, verbose=False):
    """
    Determine the performance for opt_einsum for a given einsum-notation
    :param einsum_notation: calculation given as einsum notation
    :param tensors: tensors used in the einsum-summation
    :param iterations: calculation is performed iteration times
    :param verbose: set to True to get more information
    :return:
    """
    ##### OPT_EINSUM EXPERIMENT #####
    # get the optimal contraction path
    opt_rg = oe.RandomGreedy(max_repeats=256, parallel=True)
    index_sizes = _get_sizes(einsum_notation, tensors)
    views = oe.helpers.build_views(einsum_notation, index_sizes)
    path, path_info = oe.contract_path(einsum_notation, *views, optimize=opt_rg)

    if tensor_names is None:
        # burn in
        for _ in range(iterations):
            oe_result = oe.contract(einsum_notation, *tensors, optimize=path)
        tic = timer()
        for _ in range(iterations):
            oe_result = oe.contract(einsum_notation, *tensors, optimize=path)
        toc = timer()
    else:
        # if we reuse some tensors
        name_to_tensor = {}
        if not evidence is None:
            for name, tensor in evidence.items():
                exec(f"{name} = evidence[name]")
                exec(f"name_to_tensor['{name}'] = {name}")

        evidence_arguments = [name_to_tensor[name] for name in tensor_names]
        # burn in
        for _ in range(iterations):
            oe_result = oe.contract(einsum_notation, *evidence_arguments, optimize=path)
        tic = timer()
        for _ in range(iterations):
            oe_result = oe.contract(einsum_notation, *evidence_arguments, optimize=path)
        toc = timer()
    if verbose: print(f"opt_einsum: {1 / ((toc - tic) / iterations)} iterations per second.")
    return 1 / ((toc - tic) / iterations), oe_result, path_info


def get_python_sat_performance(clauses, oe_result=False, iterations=10, verbose=False):
    cnf = CNF(from_clauses=clauses)
    with Solver(bootstrap_with=cnf) as solver:
        # burn in
        for _ in range(iterations):
            solver.solve()
        tic = timer()
        for _ in range(iterations):
            solver.solve()
        toc = timer()
        models = list(solver.enum_models())
        variables = [var for clause in clauses for var in clause]
        cleaned_models = []
        for model in models:
            cleaned_models.append(set(model).intersection(set(variables)))
        num_models = len(set([" ".join([str(i) for i in model]) for model in cleaned_models]))
        print(int(oe_result), num_models)
        if verbose: print(f"PySAT: {1 / ((toc-tic) / iterations)} iterations per second.")
        assert num_models == oe_result, "Error during calculation."

        return 1 / ((toc-tic) / iterations)


def get_db_performance(insert_queries, query, oe_result=False, iterations=10,
                       compile_hyper=True, return_sql_result=False, complex_data=False, verbose=False):
    """
    Determine the performance for different database systems for a query.
    :param insert_queries: list of queries for temporary tables, not used for performance
    :param query: query for the performance measurement
    :param oe_result: result of the einsum-summation described by the query in opt_einsum used for error detection
    :param iterations: query is calculated iteration times
    :param verbose: set to True to get more information
    :return:
    """
    results = {}

    ##### SQLITE EXPERIMENTS #####
    # connect to database
    con = sqlite3.connect(':memory:')
    cur = con.cursor()

    # insert data
    tic = timer()
    for insert_query in insert_queries:
        cur.execute(insert_query)
    toc = timer()
    if verbose: print(f"Insert data in {toc - tic}s.")

    # burn in
    for _ in range(iterations):
        sqlite_result = cur.execute(query)
        con.commit()
        sqlite_result = sqlite_result.fetchall()
    tic = timer()
    for _ in range(iterations):
        sqlite_result = cur.execute(query)
        con.commit()
        sqlite_result = sqlite_result.fetchall()
    toc = timer()
    results["SQLite"] = 1 / ((toc - tic) / iterations)
    if verbose: print(f"sqlite: {results['SQLite']} iterations per second.")
    con.commit()
    con.close()


    ##### POSTGRES EXPERIMENT #####
    # connect to the database
    conn = psy.connect(user='postgres', password='password', database='postgres', host='localhost')
    conn.set_isolation_level(psy.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    # insert data
    tic = timer()
    for insert_query in insert_queries:
        cur.execute(insert_query)
    toc = timer()
    if verbose: print(f"Insert data in {toc - tic}s.")

    # burn in
    for _ in range(iterations):
        cur.execute(query)
        postgres_result = cur.fetchall()
    tic = timer()
    for _ in range(iterations):
        cur.execute(query)
        postgres_result = cur.fetchall()
    toc = timer()
    cur.close()
    conn.close()
    results["PostgreSQL"] = 1 / ((toc - tic) / iterations)
    if verbose: print(f"postgres: {results['PostgreSQL']} iterations per second.")


    ##### HYPER EXPERIMENT #####
    parameters = {
        # "log_config": "", # remove it when you want a log, search for query-end, there it all starts
        "max_query_size": "10000000000",
        "hard_concurrent_query_thread_limit": "1",
        "initial_compilation_mode": "v"
    }
    if compile_hyper:
        parameters["initial_compilation_mode"] = "o"  # o - optimize, v - virtual (interpreter), c - machine code not optimized

    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU, parameters=parameters) as hyper:
        with Connection(hyper.endpoint, 'data.hyper', CreateMode.CREATE_AND_REPLACE) as connection:
            # insert data
            tic = timer()
            for insert_query in insert_queries:
                connection.execute_list_query(insert_query)
            toc = timer()
            if verbose: print(f"Insert data in {toc - tic}s.")

            # burn in
            for _ in range(iterations):
                hyper_result = connection.execute_list_query(query)
            tic = timer()
            for _ in range(iterations):
                hyper_result = connection.execute_list_query(query)
            toc = timer()
            results["HyPer"] = 1 / ((toc - tic) / iterations)
            if verbose: print(f"hyper: {results['HyPer']} iterations per second.")


    ##### ERROR CHECK #####
    # only check error if there are data available
    if not oe_result is False:
        if complex_data:
            sqlite_result = {tuple(index_val[:-2]): complex(index_val[-2], index_val[-1]) for index_val in sqlite_result}
            hyper_result = {tuple(index_val[:-2]): complex(index_val[-2], index_val[-1]) for index_val in hyper_result}
            postgres_result = {tuple(index_val[:-2]): complex(index_val[-2], index_val[-1]) for index_val in postgres_result}
        else:
            hyper_result = {tuple(index_val[:-1]): index_val[-1] for index_val in hyper_result}
            sqlite_result = {tuple(index_val[:-1]): index_val[-1] for index_val in sqlite_result}
            postgres_result = {tuple(index_val[:-1]): index_val[-1] for index_val in postgres_result}
        values_neq_zero = 0
        db_values = 0
        if isinstance(oe_result, float):
            assert np.allclose(oe_result, hyper_result[()], sqlite_result[()], postgres_result[()]), "Error during calculation"
            assert values_neq_zero == db_values, "Error during calculaution."

        else:
            for indices in product(*[range(i) for i in oe_result.shape]):
                if oe_result[indices] != 0 or oe_result[indices] != 0j:
                    values_neq_zero += 1
                if indices in sqlite_result:
                    if sqlite_result[indices] == 0j:
                        continue
                    db_values += 1
                    if complex_data:
                        assert np.allclose(oe_result[indices], sqlite_result[indices]), "Error during calculation"
                        assert np.allclose(oe_result[indices], hyper_result[indices]), "Error during calculation"
                        assert np.allclose(oe_result[indices], postgres_result[indices]), "Error during calculation"
                    else:
                        assert np.allclose(oe_result[indices], sqlite_result[indices], hyper_result[indices], postgres_result[indices]), "Error during calculation"
            assert values_neq_zero == db_values, "Error during calculaution."

    if return_sql_result:
        return results, sqlite_result
    else:
        return results


def print_as_csv(results, no_feature=False):
    if no_feature:
        sep = "&"
        print("name", sep, "performance")
        for feature, performance in results.items():
            print(feature, sep, performance)
        print()
    else:
        sep = "&"
        for index, feature in enumerate(sorted(results.keys())):
            # print header
            if index == 0:
                print("feature", end="")
                for database in results[feature].keys():
                    print(f" {sep} ", database, end="")
                print()
            print(feature, end="")
            for database in results[feature].keys():
                print(f" {sep} ", results[feature][database], end="")
            print()
