
import os
from timeit import default_timer as timer
import pickle

import numpy as np

from experiments.util.sql_commands import get_queries_for_COO, sql_einsum_query
from experiments.graphical_models.model import get_tensornetwork_from_pairwise_matrix
from experiments.datasets.breastcancer import get_data, create_evidence_tensors
from experiments.util.performance import get_db_performance, get_opt_einsum_gm_performance, print_as_csv


def _get_complete_query(query):
    split_query = query.split("\n")
    top_query = "\n".join(split_query[:-2])
    # -1 is empty
    bottom_query = split_query[-2]
    normalized_query = f"""{top_query}
), X(i, j, val) AS (
    {bottom_query[2:]}
) SELECT X.i, Y.j, Y.val / SUM(X.val) AS val FROM X, X Y WHERE Y.i = X.i GROUP BY X.i, Y.j, Y.val ORDER BY X.i, Y.j
        """
    return normalized_query


def run_gm_query_experiment(iterations=10, verbose=False):
    ##### LOAD DATA #####
    # load breast cancer data set
    data = get_data()

    ##### CREATE TENSORNETWORK #####
    # load the best model
    q = np.load(os.path.join(os.path.dirname(__file__), "pairwise_Q_0.5.npy"))

    # create the tensor network
    einsum_notation, parameter_tensors = get_tensornetwork_from_pairwise_matrix(q)

    # track results
    results = {}

    # generate query for experiment with different batch sizes
    for batchsize in [1, 10, 50, 100, 200, 250]:
        # track each value in the results
        results.setdefault(batchsize, dict())

        # make a local copy
        tensors = parameter_tensors.copy()

        # get batchsize many random data
        batch_data = data.sample(batchsize, replace=False)

        # get indices
        vars = set([j for i in einsum_notation.split(",") for j in i])
        clasz = "i"
        evidence = vars.difference(set(clasz))
        vars = sorted(list(vars))

        # create evidence tensors
        einsum_notation_evidence = einsum_notation + "," + ",".join([f"Z{v}" for v in vars[1:]]) + "->Zi"
        # remove the first evidence tensor, that represents the class
        evidence_tensors = create_evidence_tensors(batch_data, replace={"Class": 1})[1:]

        e_tensors = tensors.copy()

        # insert evidence in tensor names, einsum notation and tensors, leave out the class (index 0)
        for index, evidence in enumerate(evidence_tensors):
            e_tensors.append(evidence)

        # run opt_einsum calculation
        time, oe_result, path_info = get_opt_einsum_gm_performance(einsum_notation_evidence, e_tensors,
                                                                      iterations=iterations, verbose=verbose)
        results[batchsize]["Python"] = time

        ##### GENERATE DATABASE QUERIES #####
        # insert parameter tensors and save relation name
        insert_queries = []
        e_tensors = {}
        additional_tensors = {}
        tensor_names = []
        for index, tensor in enumerate(parameter_tensors):
            insert_queries += get_queries_for_COO(tensor, f"R{index}")
            tensor_names.append(f"R{index}")
            additional_tensors[f"R{index}"] = tensor
        # add evidence tensors to names
        for index, evidence in enumerate(evidence_tensors):
            tensor_names.append(f"E{index}")
            e_tensors[f"E{index}"] = evidence
        # compile into sql query
        query_e = sql_einsum_query(einsum_notation_evidence, tensor_names, evidence=e_tensors, path_info=path_info,
                                   further_tensors=additional_tensors, order_by=False)

        query = _get_complete_query(query_e)

        # run database calculations
        results[batchsize].update(get_db_performance(insert_queries, query, oe_result=oe_result, iterations=iterations,
                                                     verbose=verbose, compile_hyper=False))

    print_as_csv(results)
    pickle.dump(results, open(f"gm_evidence_results_{timer()}.p", "wb"))

    return results