

import os
import pickle

from timeit import default_timer as timer
import opt_einsum as oe

from numpy import array

from experiments.util.sql_commands import sql_einsum_query
from experiments.util.performance import get_db_performance, print_as_csv


def _get_sizes(einstein, tensors, parameters):
    index_sizes = {}
    for name, tensor in tensors.items():
        line = f"{name} = {tensor.__repr__()}"
        exec(line)
    for einsum_index, tensor_name in zip(einstein.split("->")[0].split(","), parameters):
        for index, dimension in zip(list(einsum_index), list((tensors[tensor_name]).shape)):
            if not index in index_sizes:
                index_sizes[index] = dimension
            else:
                if index_sizes[index] != dimension:
                    raise Exception(f"Dimension error for index '{index}'.")
    return index_sizes


def oe_experiment(einstein, tensors, parameters, iterations=10, verbose=False):
    opt_rg = oe.RandomGreedy(max_repeats=256, parallel=True)
    index_sizes = _get_sizes(einstein, tensors, parameters)
    views = oe.helpers.build_views(einstein, index_sizes)
    path, path_info = oe.contract_path(einstein, *views, optimize=opt_rg)
    for name, tensor in tensors.items():
        line = f"{name} = {tensor.__repr__()}"
        exec(line)
    # Burn In
    for _ in range(iterations):
        line = f"oe_result = oe.contract('{einstein}', {','.join(parameters)}, optimize=path)"
        exec(line)
    # Experiment
    tic = timer()
    for _ in range(iterations):
        line = f"oe_result = oe.contract('{einstein}', {','.join(parameters)}, optimize=path)"
        exec(line)
    toc = timer()
    if verbose: print(f"Performance Opt_Einsum {1 / ((toc-tic) / iterations)} iterations per second.")
    return locals()['oe_result'], 1 / ((toc-tic) / iterations), path_info


def quantum_use_case(depth=-1, nbits=-1, iterations=10, verbose=False):
    results = dict()

    for file in sorted(os.listdir(os.path.join("quantum_circuits", "circuits"))):
        data = pickle.load(open(os.path.join("quantum_circuits", "circuits", file), "rb"))
        einstein = data["einstein"]
        tensors = data["tensors"]
        depth_c = int(file.split("_")[1])
        nbits_c = int(file.split("_")[2])

        if depth_c != depth and depth != -1:
            continue
        if nbits_c != nbits and nbits != -1:
            continue

        print("Tensors:", len(tensors))
        print("Number Operations:", len(einstein.split(",")))
        parameters = data["parameters"]

        # OPT EINSUM Experiment
        result, performance, path_info = oe_experiment(einstein, tensors, parameters,
                                                       iterations=iterations, verbose=verbose)

        # SQL EXPERIMENT
        query = sql_einsum_query(einstein, parameters, tensors, path_info=path_info, complex=True)
        times = get_db_performance([], query, oe_result=result, complex_data=True, iterations=iterations,
                                   verbose=verbose, compile_hyper=False)
        times["Python"] = performance

        print(times)

        results[nbits_c] = times

        print_as_csv(results)

    print_as_csv(results)
