

def to_3_sat(clauses):
    used_vars = set([abs(var) for clause in clauses for var in clause])
    sat_clauses = []

    for clause in clauses:
        if len(clause) <= 3:
            sat_clauses.append(clause)
        else:
            gen_3_sat_clauses, used_vars = _to_3_sat(clause, used_vars)
            sat_clauses += gen_3_sat_clauses
    return sat_clauses


def _to_3_sat(clause, used_vars):
    gen_clauses = []
    unused = max(used_vars) + 1
    new_vars = [unused]
    gen_clauses.append([clause[0], clause[1], unused])
    for i in range(2, len(clause)-2):
        new_clauses = [-unused, clause[i], unused+1]
        gen_clauses.append(new_clauses)
        unused = unused + 1
        new_vars.append(unused)
    gen_clauses.append([-unused, clause[-2], clause[-1]])
    used_vars = used_vars.union(set(new_vars))
    return gen_clauses, used_vars