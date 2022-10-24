
from experiments.graphical_models.model_experiment import run_gm_query_experiment
from sat_solving.sat_experiment import run_sat_experiment
from rdf_queries.rdf_experiment import run_rdf_experiment
from quantum_circuits.qc_experiments import quantum_use_case


if __name__ == "__main__":

    iterations = 10
    verbose = True

    # for the quantum_use_case you can define a number of layers or qbits
    quantum_use_case(depth=8, iterations=iterations, verbose=verbose)
    quantum_use_case(nbits=10, iterations=iterations, verbose=verbose)

    run_rdf_experiment(iterations=iterations, verbose=verbose)

    run_sat_experiment(iterations=iterations, verbose=verbose)

    run_gm_query_experiment(iterations=iterations, verbose=verbose)

