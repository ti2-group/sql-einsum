

from string import Template, ascii_letters
from itertools import product

import numpy as np
import opt_einsum as oe

characters = list(ascii_letters)
characters = characters[8:26] + characters[:8]

characters_tmp = characters.copy()
for i in range(1000):
    characters += [f"{char}{i}" for char in characters_tmp]


def _get_indices_for_tensor(X):
    relation_definition = ", ".join([character + ' INTEGER' for character in characters[:len(X.shape)]])
    return relation_definition


def get_queries_for_COO_from_tripel(tripel_list, relation_name="G"):
    relation_definition = "s INTEGER, p INTEGER, o INTEGER, val INTEGER"
    relation_indices = "s, p, o, val"
    queries = [
        f"DROP TABLE IF EXISTS {relation_name};",
        f"CREATE TEMPORARY TABLE {relation_name} ({relation_definition});"
    ]
    # insert values into table
    values = []
    for row, tripel in enumerate(tripel_list):
        # indices and value
        values.append(f"{tripel + (1,)}")
        if row + 1 % 10000 == 0:
            query = f"INSERT INTO {relation_name} ({relation_indices}) VALUES {', '.join(values)};"
            queries.append(query)
            values = []
    # insert missing values
    if values:
        query = f"INSERT INTO {relation_name} ({relation_indices}) VALUES {', '.join(values)};"
        queries.append(query)
    return queries


def var_list_to_sql(var_list):
    s = ""
    unique_names = set()
    for name, arr in var_list.items():
        if name in unique_names:
            continue
        unique_names.add(name)
        if s:
            s += "), "
        else:
            s += "WITH "
        if np.isscalar(arr):
            s += name + "(re, im) AS ("
        else:
            s += name + "(" + ",".join(characters[:len(arr.shape)]) + ", re, im) AS ("

        tmp_s = ""
        found_non_zero = False

        def rec_loop(shape, lidx):
            nonlocal tmp_s, arr, found_non_zero
            if shape:
                for idx in range(shape[0]):
                    lidx.append(idx)
                    rec_loop(shape[1:], lidx)
                    lidx.pop()
                if tmp_s[-1] != "\n":
                    tmp_s += "\n"
            else:
                is_zero = np.isclose(arr[tuple(lidx)].real, 0, rtol=1e-12, atol=1e-12) and np.isclose(
                    arr[tuple(lidx)].imag, 0, rtol=1e-12, atol=1e-12)
                all_indexes_zeros = lidx[0] == 0 and len(set(lidx)) == 1
                if not all_indexes_zeros and not found_non_zero and not is_zero:
                    all_indexes_zeros = True
                if not is_zero and all_indexes_zeros:
                    tmp_s += "VALUES (" + " AS INTEGER), ".join(
                        "CAST(" + str(idx) for idx in lidx) + " AS INTEGER), CAST(" + str(
                        arr[tuple(lidx)].real) + " AS DOUBLE PRECISION), CAST(" + str(
                        arr[tuple(lidx)].imag) + " AS DOUBLE PRECISION))"
                    tmp_s += ", "
                    found_non_zero = True
                elif not is_zero:
                    tmp_s += "(" + ", ".join(str(idx) for idx in lidx) + ", " + str(
                        arr[tuple(lidx)].real) + ", " + str(arr[tuple(lidx)].imag) + ")"
                    tmp_s += ", "

        if np.isscalar(arr):
            tmp_s += "VALUES (CAST(" + str(arr.real) + " AS DOUBLE PRECISION), CAST(" + str(
                arr.imag) + " AS DOUBLE PRECISION))\n  "
        else:
            rec_loop(arr.shape, [])
        s += "\n  " + tmp_s.replace("\n", "\n  ")[:-5] + "\n"
    return s


def get_queries_for_COO(X: np.array, relation_name="X"):
    """
        Creates the database queries for the COO format and creates also the X.csv and y.csv
        :param X: numpy array containing the values
        :return: list of string queries
        """
    relation_definition = ", ".join(characters[:len(X.shape)]) + ", val"
    queries = [
        f"DROP TABLE IF EXISTS {relation_name};",
        f"CREATE TEMPORARY TABLE {relation_name} ({_get_indices_for_tensor(X)}, val DOUBLE PRECISION );"
    ]
    # insert values into table
    values = []
    for row, indices in enumerate(product(*[range(i) for i in X.shape])):
        # skip zero values
        if X[indices] == 0:
            continue
        # indices and value
        values.append(f"{indices + (X[indices],)}")
        if row + 1 % 10000 == 0:
            query = f"INSERT INTO {relation_name} ({relation_definition}) VALUES {', '.join(values)};"
            queries.append(query)
            values = []
    # insert missing values
    if values:
        query = f"INSERT INTO {relation_name} ({relation_definition}) VALUES {', '.join(values)};"
        queries.append(query)
    return queries


def _sql_values_for_tensor(var_list):
    """
    Creates temporary data for all tensors in var_list
    :param var_list: dictionary containing string: np.array (tensor name: tensor)
    :return: sql query
    """
    query_for_single_tensors = []
    for tensor_name, tensor in var_list.items():
        if isinstance(tensor, float) or isinstance(tensor, int):
            query = f" {tensor_name}(val) AS ( VALUES ("
            query += "("
            query += f"CAST({tensor} AS DOUBLE PRECISION))))\n"
        else:
            query = f" {tensor_name}({', '.join(characters[:len(tensor.shape)])}, val) AS (\n"
            # create value tuples
            values = []
            cast = False
            for row, indices in enumerate(product(*[range(i) for i in tensor.shape])):
                # skip zero values
                if tensor[indices] == 0:
                    continue
                # if we add the first value we have to give the data type
                if not cast:
                    type_definition = "("
                    for index in indices:
                        type_definition += f"CAST({index} AS INTEGER), "
                    type_definition += f"CAST({tensor[indices]} AS DOUBLE PRECISION))"
                    values.append(type_definition)
                    cast = True
                else:
                    values.append(f"{indices + (tensor[indices],)}")
            cast = False
            query += f"  VALUES {', '.join(values)}\n)"
        query_for_single_tensors.append(query)
    query = f"WITH{','.join(query_for_single_tensors)}"
    return query


def _einsum_notation_to_sql(einsum_notation, tensors, order_by=True, complex=False):
    # get einsum-notation indices
    formula = einsum_notation.replace(" ", "")
    tensorindices, outindices = formula.replace(" ", "").split("->")
    tensorindices = tensorindices.split(",")

    # get tensor names and set constants
    arrays = tensors.replace(" ", "").split(",")
    len_arrays = len(arrays)
    array_aliases = []
    names = set()
    i = 1

    # generate einsum-summation
    from_clause = "FROM "
    for arr in arrays:
        alias = arr
        while alias in names:
            alias = "T" + str(i)
            i += 1
        names.add(alias)
        array_aliases.append(alias)
        from_clause += arr
        if arr != alias:
            from_clause += " " + alias
        from_clause += ", "
    from_clause = from_clause[:-2]

    group_by_clause = "GROUP BY "
    select_clause = "SELECT "

    # Die Indizes die bleiben, kommen in GROUP BY, diese Indice kommen auch aufgezählt in Ausgabereihenfolge in SELECT
    used_indices = set()
    idx = 0
    for i in range(len(outindices)):
        for t in range(len(tensorindices)):
            for j in range(len(tensorindices[t])):
                if tensorindices[t][j] == outindices[i] and outindices[i] not in used_indices:
                    used_indices.add(outindices[i])
                    varSQL = array_aliases[t] + "." + characters[j]
                    select_clause += varSQL + " AS " + characters[idx] + ", "
                    group_by_clause += varSQL + ", "
                    idx += 1

    group_by_clause = group_by_clause[:-2]

    # neue val ist immer SUM von allen val aufmultipliziert
    if complex:
        if len_arrays == 1:
            select_clause += "SUM("
            for t in array_aliases:
                select_clause += t + ".re * "
            select_clause = select_clause[:-3] + ") AS re"

            select_clause += ", SUM("
            for t in array_aliases:
                select_clause += t + ".im * "
            select_clause = select_clause[:-3] + ") AS im"
        else:
            # (a+bi)(c+di) = (ac−bd) + (ad+bc)i
            a = array_aliases[0] + ".re"
            b = array_aliases[0] + ".im"
            c = array_aliases[1] + ".re"
            d = array_aliases[1] + ".im"
            select_clause += "SUM(" + a + " * " + c + " - " + b + " * " + d + ") AS re"
            select_clause += ", SUM(" + a + " * " + d + " + " + b + " * " + c + ") AS im"
    else:
        select_clause += "SUM("
        for t in array_aliases:
            select_clause += t + ".val * "
        select_clause = select_clause[:-3] + ") AS val"

    # Indices die gleich sind zwischen den Eingabetensoren kommen in die WHERE Klausel in transitiver Beziehung zueinander
    unique_indices = ""
    for t in range(len(tensorindices)):
        for j in range(len(tensorindices[t])):
            if tensorindices[t][j] not in unique_indices:
                unique_indices += tensorindices[t][j]

    related_tensors_per_index = []
    for i in range(len(unique_indices)):
        related_tensors_per_index.append([])
        for t in range(len(tensorindices)):
            for j in range(len(tensorindices[t])):
                if unique_indices[i] == tensorindices[t][j]:
                    related_tensors_per_index[i].append((t, j))

    where_clause = "WHERE "
    for i in range(len(related_tensors_per_index)):
        if len(related_tensors_per_index[i]) > 1:
            t, j = related_tensors_per_index[i][0]
            firstvarSQL = array_aliases[t] + "." + characters[j]
            for j in range(1, len(related_tensors_per_index[i])):
                t, j = related_tensors_per_index[i][j]
                varSQL = array_aliases[t] + "." + characters[j]
                where_clause += firstvarSQL + "=" + varSQL + " AND "

    where_clause = where_clause[:-5]

    # use an order by for
    order_by_clause = "ORDER BY "
    for c in characters[:len(outindices)]:
        order_by_clause += c + ", "
    order_by_clause = order_by_clause[:-2]

    if len(where_clause) < 5:
        where_clause = ""
    else:
        where_clause = " " + where_clause

    gb_and_ob = ""
    if outindices:
        gb_and_ob = " " + group_by_clause + (" " + order_by_clause if order_by else "")

    # combine everything
    query = select_clause + " " + from_clause + where_clause + gb_and_ob
    return query


def _get_sizes(einsum_notation, tensor_names, tensors):
    index_sizes = {}
    for einsum_index, tensor_name in zip(einsum_notation.split("->")[0].split(","), tensor_names):
        for index, dimension in zip(list(einsum_index), list(np.array(tensors[tensor_name]).shape)):
            if not index in index_sizes:
                index_sizes[index] = dimension
            else:
                if index_sizes[index] != dimension:
                    raise Exception(f"Dimension error for index '{index}'.")
    return index_sizes


def _einsum_notation_to_opt_sql(einsum_notation, tensor_names, evidence, order_by=True, path_info=None, complex=False):
    # cleanup the einsum notation, get constants for further computations
    einsum_notation = einsum_notation.replace(" ", "")
    index_sizes = _get_sizes(einsum_notation, tensor_names, evidence)

    # we do not want an actual computation, so we create a view of the problem
    opt_rg = oe.RandomGreedy(max_repeats=256, parallel=True)
    views = oe.helpers.build_views(einsum_notation, index_sizes)
    if path_info is None:
        path_info = oe.contract_path(einsum_notation, *views, optimize=opt_rg)[1]
    if isinstance(path_info, list):
        cl = path_info
    else:
        cl = path_info.contraction_list

    # generate SQL query
    i = 1
    arrays = tensor_names.copy()
    names = set(arrays)
    query = "WITH "
    c = 0
    # generate for each contraction of the optimal opt_einsum path
    for contraction in cl:
        # get tensors and formula used in this contraction
        current_arrays = [arrays[idx] for idx in contraction[0]]
        for idx in contraction[0]:
            arrays.pop(idx)
        current_formula = contraction[2]
        current_arrays = ",".join(current_arrays)
        # perform temporary calculation and add the name to the end for later use
        name = f"K{i}"
        while name in names:
            i += 1
            name = f"K{i}"
        names.add(name)
        arrays.append(name)
        i += 1
        c += 1
        # generate sql query for einsum-summation
        if c < len(cl):
            query += name + " AS (\n  "
            query += _einsum_notation_to_sql(current_formula, current_arrays, False, complex=complex) + "\n), "
        else:
            query = query[:-2] + " " + _einsum_notation_to_sql(current_formula, current_arrays, order_by=order_by, complex=complex) + "\n"
    if query.startswith("WIT "):
        query = query.replace("WIT ", " ")
    return query


def sql_einsum_query(einsum_notation, tensor_names, evidence, further_tensors=None,
                     path_info=None, order_by=True, complex=False):
    """
    Generates SQL-code for an einstein notation string
    :param einsum_notation: string representation of the einstein notation (example "ab,b->a")
    :param tensor_names: list of arguments of the einstein notation (example ["A", "B"])
    :param evidence: dictionary containing the data to the tensor_names
    :param further_tensors: dictionary of additional tensors, that values are not part of the query
    :param path_info: contraction list, this is optional and can set to a given list, like from opt_einsum
    :param order_by: boolean, if set to False the order by clause is removed
    :param complex: boolean, if set to True complex numbers can be used
    :return: string representing the sql-code
    """
    if complex:
        tensor_definitions = var_list_to_sql(evidence)
        contraction = _einsum_notation_to_opt_sql(einsum_notation, tensor_names, evidence, complex=True, path_info=path_info)
        query = tensor_definitions + ")" + contraction.replace("WITH", ",")
        return query
    # temorary values
    evidence_query = _sql_values_for_tensor(evidence)
    evidences_copy = evidence.copy()
    if not further_tensors is None:
        evidences_copy.update(further_tensors)
    # einsum-summation
    einsum_summation = _einsum_notation_to_opt_sql(einsum_notation, tensor_names, evidences_copy,
                                                   order_by=order_by, path_info=path_info)
    # combine both
    if einsum_summation.startswith(" SELECT"):
        all_sql = f"{evidence_query} {einsum_summation.replace('WITH', '')}" \
            if len(evidence) > 0 else einsum_summation
    else:
        all_sql = f"{evidence_query}, {einsum_summation.replace('WITH', '')}" \
            if len(evidence) > 0 else einsum_summation
    return all_sql
