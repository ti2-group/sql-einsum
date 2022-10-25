import numpy as np

from experiments.util import sql_commands

if __name__ == "__main__":

    einstein_notation = "ab,bc,c->a"
    paramater_names = ["A", "B", "C"]
    tensors = {
        "A": np.random.rand(2,2),
        "B": np.random.rand(2,5),
        "C": np.random.rand(5)
    }

    # help(sql_commands.sql_einsum_query)
    query = sql_commands.sql_einsum_query(einstein_notation,  paramater_names, evidence=tensors)

    print(query)
