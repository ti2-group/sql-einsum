import string
import pickle
from timeit import default_timer as timer
import os
from itertools import product

import numpy as np
import opt_einsum as oe

from experiments.util.performance import get_opt_einsum_performance, get_db_performance, print_as_csv, get_python_sat_performance
from experiments.util.sql_commands import sql_einsum_query
from experiments.util.sat_solving import to_3_sat


chars = string.ascii_lowercase + string.ascii_uppercase + string.printable
chars = chars[8:] + chars[:8]


chars = []
for i in range(10000):
    chars.append(oe.get_symbol(i))


def _create_tensors():
    tensors = {}
    enumeration_index = 0
    for order in range(1, 4):
        non_zero = {}
        for indices in product([0,1], repeat=order):
            tensor = np.ones([2]*order)
            tensor[tuple(indices)] = 0.0
            non_zero[tuple(indices)] = (f"E{enumeration_index}", tensor)
            enumeration_index += 1
        tensors[order] = non_zero
    return tensors


def _get_index_and_tensor(clause):
    index = ""
    for var in clause:
        index += chars[np.abs(var)]
    return index


def _create_tensor_network_from_clauses_and_variables(clauses, tensors):
    indices = []
    tensor_names = []
    for clause in clauses:
        index = _get_index_and_tensor(clause)
        index_tuple = tuple(1 if i < 0 else 0 for i in clause)
        indices.append(index)
        name, tensor = tensors[len(clause)][index_tuple]
        tensor_names.append(name)

    return ",".join(indices) + "->", tensor_names


def _get_conda_problem(num_clauses, tensors, verbose=False):
    # load the clauses and indices with names
    conda_clauses = pickle.load(open(os.path.join("sat_solving", "clauses_sqlite.p"), "rb"))
    conda_clauses = to_3_sat(conda_clauses)

    clauses = conda_clauses[:num_clauses]
    variables = list(set([np.abs(var) for clause in clauses for var in clause]))

    print(f"Number of variables {len(variables)}, number of clauses {len(clauses)}.")

    # create the tensor network
    einsum_notation, tensor_names = _create_tensor_network_from_clauses_and_variables(clauses, tensors)
    evidence = {name: tensor
                for order, index_dict in tensors.items()
                    for index, (name, tensor) in index_dict.items()
                        if name in tensor_names}

    return einsum_notation, tensor_names, evidence, clauses


def run_sat_experiment(iterations=10, skip_pysat=False, verbose=False):
    # track results
    results = {}

    # create multiple problems
    clauses_sizes = [100, 200, 300, 400, 500, 600, 700, 718]

    tensors = _create_tensors()

    for clause_size in clauses_sizes:
        results[clause_size] = {}
        einsum_notation, tensor_names, evidence, clauses = _get_conda_problem(clause_size, tensors, verbose=True)
        einsum_tensors = [evidence[name] for name in tensor_names]

        results[clause_size]["Python"], oe_result, path_info = get_opt_einsum_performance(einsum_notation, einsum_tensors,
                                                                               evidence=evidence, tensor_names=tensor_names,
                                                                                 iterations=iterations, verbose=verbose)

        query = sql_einsum_query(einsum_notation, tensor_names, evidence=evidence, path_info=path_info)

        if not skip_pysat:
            results[clause_size]["PySAT"] = get_python_sat_performance(clauses, oe_result,
                                                                    iterations=iterations, verbose=verbose)
        results[clause_size].update(get_db_performance([], query, oe_result=oe_result, compile_hyper=False,
                                                         iterations=iterations, verbose=verbose))

    print_as_csv(results)
    pickle.dump(results, open(f"sat_results_{timer()}.p", "wb"))
    return results

