from rdflib import Graph

from experiments.util.sql_commands import get_queries_for_COO_from_tripel, sql_einsum_query
from experiments.util.performance import get_db_performance, print_as_csv

import os
from timeit import default_timer as timer


def get_tripel_from_graph(graph, verbose=False):
    tic = timer()
    objects = set()
    for s, p, o in graph:
        objects.add(o)
        objects.add(s)
        objects.add(p)
    toc = timer()
    if verbose: print(f"Split graph into dictionaries in {toc-tic}s")

    # create values for each index
    objects_to_index = {value: index for index, value in enumerate(objects)}

    # calculate indice tripel
    tripels = []
    for s, p, o in graph:
        tripel = (objects_to_index[s], objects_to_index[p], objects_to_index[o])
        tripels.append(tripel)
    return tripels, objects_to_index


def parse_graph(file, verbose=False):
    tic = timer()
    graph = Graph().parse(file)
    toc = timer()
    if verbose: print(f"Graph parsed in {toc - tic}s")
    return graph


def get_redf_sql_query_olympics_gold(meta_info, verbose=False):
    indices = {}
    for i in meta_info.keys():
        if str(i) == "http://wallscope.co.uk/ontology/olympics/athlete":
            indices["athlete"] = meta_info[i]
        if str(i) == "http://wallscope.co.uk/ontology/olympics/medal":
            indices["medal"] = meta_info[i]
        if str(i) == "http://www.w3.org/2000/01/rdf-schema#label":
            indices["label"] = meta_info[i]
        if str(i) == "http://wallscope.co.uk/resource/olympics/medal/Gold":
            indices["gold"] = meta_info[i]

    query = f"""
        WITH T1(i, j, val) AS (    -- ?instance walls:athlete ?athlete 
          SELECT s, o, val FROM G WHERE p={indices['athlete']}
        ), T2(i, val) AS ( -- ?instance walls:medal <http://wallscope.co.uk/resource/olympics/medal/Gold>
          SELECT s, val FROM G WHERE p={indices['medal']} AND o={indices['gold']}
        ), T3(i, j, val) AS (    -- ?athlete rdfs:label ?name
          SELECT s, o, val FROM G WHERE p={indices['label']}
        ),  K1 AS (
            SELECT T1.j AS i, SUM(T2.val * T1.val) AS val FROM T2, T1 WHERE T2.i=T1.i GROUP BY T1.j
        ) SELECT T3.j AS i, SUM(K1.val * T3.val) AS val FROM K1, T3 WHERE K1.i=T3.i GROUP BY T3.j ORDER BY val DESC
    """

    if verbose: print(query)

    return query


def rdf_query(graph, iterations=10):
    q = """
    PREFIX walls: <http://wallscope.co.uk/ontology/olympics/>
    PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?name (COUNT(?name) AS ?count) 
    WHERE {
     ?instance walls:athlete ?athlete .
     ?instance walls:medal <http://wallscope.co.uk/resource/olympics/medal/Gold> .
     ?athlete rdfs:label ?name .
    }
    GROUP BY ?name ORDER BY DESC(?count)
    """

    # burn in
    for _ in range(iterations):
        result = graph.query(q)
    tic = timer()
    for _ in range(iterations):
        result = graph.query(q)
    toc = timer()

    return result, 1 / ((toc-tic)/iterations)


def error_check(sql_result, rdf_result, meta_info):
    index_to_subjects = {index: name for name, index in meta_info.items()}
    sql_index_to_count = dict(sql_result)

    rdf_dict = {str(name): int(count) for name, count in rdf_result}

    for index, count in sql_index_to_count.items():
        if str(index_to_subjects[index]) in rdf_dict.keys():
            if sql_index_to_count[index] == rdf_dict[str(index_to_subjects[index])]:
                continue
        raise Exception("Error during SQL calculation.")


def run_rdf_experiment(verbose=False, iterations=10):
    if not os.path.exists(os.path.join("rdf_queries", "olympics.nt")):
        print("""Before starting the rdf experiment you have to unzip the file 'olympics-nt-nodup.zip'.\nSKIP RDF EXPERIMENT""")
        return None

    graph = parse_graph(os.path.join("rdf_queries", "olympics.nt"), verbose=verbose)
    tripel_list, meta_info = get_tripel_from_graph(graph, verbose=verbose)

    insert_queries = get_queries_for_COO_from_tripel(tripel_list)
    query = get_redf_sql_query_olympics_gold(meta_info, verbose=verbose)
    result, sql_result = get_db_performance(insert_queries, query, return_sql_result=True,
                                            verbose=verbose, iterations=iterations)

    rdf_result, result['RDF'] = rdf_query(graph)

    error_check(sql_result, rdf_result, meta_info)

    print_as_csv(result, no_feature=True)
