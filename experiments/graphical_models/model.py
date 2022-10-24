import os
import string

import numpy as np
import opt_einsum as oe

from datasets.breastcancer import get_data, get_variable_sizes, get_number_of_variables, \
    get_tensor_for_feature_value, get_values_of_feature, get_id_for_value, get_value_for_id, \
    create_evidence_tensors


def pairwise():
    # read the pairwise parameter matrix
    q = np.load("pairwise.npy")
    n = 9
    var_sizes = [2, 6, 3, 11, 7, 3, 3, 2, 6, 2]
    used_variables = {v: False for v in range(n)}
    indices = []
    tensors = []
    chars = string.ascii_lowercase
    cum_sums = np.cumsum(var_sizes)
    cum_sums = np.insert(cum_sums, 0, 0)

    # create a tensor network
    for i in range(n):
        for j in range(i + 1, n):
            slice = q[cum_sums[i]:cum_sums[i + 1], cum_sums[j]:cum_sums[j + 1]]
            # check if all entries are zero
            if not np.allclose(slice, np.zeros(slice.shape)):
                used_variables[i] = True
                used_variables[j] = True
                tensors.append(np.exp(slice))
                indices.append(f'{chars[i]}{chars[j]}')

    # calculate the normalisation constant of the network
    einsum_string = ','.join(indices) + '->'
    print(einsum_string)
    norm = np.einsum(einsum_string, *tensors)
    print(norm)

    # infer the unnormalized class probabilities given some variables
    evidence_tensors = []
    evidence = [4, 1, 8, 2, 1, 1, 1, 1, 1]

    for var_size, observed in zip(var_sizes[1:], evidence):
        variable_tensor = np.zeros(var_size)
        variable_tensor[observed] = 1
        evidence_tensors.append(variable_tensor)

    einsum_string = ','.join(indices) + ', b, c, d, e, f, g, h, i, j->a'
    print(einsum_string)
    poe = np.einsum(einsum_string, *(tensors + evidence_tensors))
    print(poe, np.argmax(poe))


def get_normalization_constant(einsum_notation, parameter_tensors):
    einsum_notation += "->"
    constant = oe.contract(einsum_notation, *parameter_tensors)
    return constant

def get_density(einsum_notation, tensors):
    return oe.contract(einsum_notation, *tensors)


def tensor():
    # read the parameter tensor
    Q = np.load("tensor.npy")
    var_sizes = Q.shape
    chars = string.ascii_lowercase

    # calculate the normalisation constant
    einsum_string = "".join([chars[i] for i, j in enumerate(var_sizes)]) + '->'
    print(einsum_string)
    norm = np.einsum(einsum_string, Q)
    print(norm)

    # infer the unnormalized class probabilities given some variables p(A|B=4, C=1, D=8, E=2, F=1, G=1, H=1, I=1, J=1)
    evidence_tensors = []
    evidence = [4, 1, 8, 2, 1, 1, 1, 1, 1]

    for var_size, observed in zip(var_sizes[1:], evidence):
        variable_tensor = np.zeros(var_size)
        variable_tensor[observed] = 1
        evidence_tensors.append(variable_tensor)

    query_einsum = "abcdefghij, b, c, d, e, f, g, h, i, j->a"
    query_result = np.einsum(query_einsum, Q, *evidence_tensors)
    print(query_result, np.argmax(query_result))



def get_tensornetwork_from_pairwise_matrix(q, n=-1, var_sizes=-1):
    n = get_number_of_variables() if n == -1 else n
    var_sizes = get_variable_sizes() if var_sizes == -1 else var_sizes
    used_variables = {v: False for v in range(n)}
    indices = []
    tensors = []
    chars = string.ascii_lowercase
    chars = chars[8:] + chars[:8]
    cum_sums = np.cumsum(var_sizes)
    cum_sums = np.insert(cum_sums, 0, 0)

    # create a tensor network
    for i in range(n):
        for j in range(i + 1, n):
            slice = q[cum_sums[i]:cum_sums[i + 1], cum_sums[j]:cum_sums[j + 1]]
            # check if all entries are zero
            if not np.allclose(slice, np.zeros(slice.shape)):
                used_variables[i] = True
                used_variables[j] = True
                # tensors.append(np.exp(slice))
                tensors.append(np.exp(slice))
                indices.append(f'{chars[i]}{chars[j]}')

    # generate einsum_notation
    einsum_notation = ','.join(indices)

    # return notation and parameter tensors
    return einsum_notation, tensors


def classify_test():
    # load breast cancer data set
    data = get_data()

    # split into target and evidence
    targets = data['Class']
    evidences = data.drop('Class', axis=1)

    # load pairwise parameter
    for file in os.listdir("models"):
        if file.endswith('npy'):
            q = np.load(os.path.join("models", file))

            # create the tensor network
            einsum_notation, tensors = get_tensornetwork_from_pairwise_matrix(q)

            # perform classification task
            success = 0
            for target, evidence in zip(targets, evidences.iterrows()):
                evidence_tensors = create_evidence_tensors(evidence)
                predictions = oe.contract(einsum_notation + ",b,c,d,e,f,g,h,i,j->a", *tensors, *evidence_tensors)
                prediction = np.argmax(predictions)
                success += 1 if prediction == target else 0

            print("Accuracy:", success/len(evidences), "with", len(tensors+evidence_tensors), "tensors")


def predict_tumor_size_given_age():
    # load the best model
    q = np.load(os.path.join("models", "pairwise_Q_0.5.npy"))

    # create the tensor network
    einsum_notation, tensors = get_tensornetwork_from_pairwise_matrix(q)

    # age is the second feature described by index 'b' all other are marginalized out, tumor-size is described by 'd'
    einsum_notation += ",b->d"

    # for each age calculate the tumor size
    for age in get_values_of_feature("age"):
        age_evidence_tensor = get_tensor_for_feature_value("age", get_id_for_value("age", age))
        predictions = oe.contract(einsum_notation, *tensors, age_evidence_tensor)
        tumor_size_prediction = get_value_for_id("tumor-size", np.argmax(predictions))
        print("At age", age, "you probably have a tumor-size of", tumor_size_prediction)


def predict_menopause_given_age():
    # load the best model
    q = np.load(os.path.join("models", "pairwise_Q_0.5.npy"))

    # create the tensor network
    einsum_notation, tensors = get_tensornetwork_from_pairwise_matrix(q)

    # age is the second feature described by index 'b' all other are marginalized out, menopause is described by 'c'
    einsum_notation += ",b->c"

    # for each age calculate the tumor size
    for age in get_values_of_feature("age"):
        age_evidence_tensor = get_tensor_for_feature_value("age", get_id_for_value("age", age))
        predictions = oe.contract(einsum_notation, *tensors, age_evidence_tensor)
        prediction = get_value_for_id("menopause", np.argmax(predictions))
        print("At age", age, "you probably are in", prediction)


if __name__ == "__main__":
    print("Tumor-size given age prediction.")
    predict_tumor_size_given_age()
    print()
    print("Menopause status given age prediction")
    predict_menopause_given_age()
    print()
    print("Accuracy calculations")
    classify_test()
    # pairwise()
    # tensor()