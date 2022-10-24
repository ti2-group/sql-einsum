
import os

import pandas as pd
import numpy as np

_filepath = "breast-cancer.data"


def get_tensor_for_feature_value(feature, value):
    size = len(meta['catuniques'][feature])
    var_tensor = np.zeros(size)
    var_tensor[value] = 1
    return var_tensor


def get_value_for_id(feature, id):
    reverse = {id: value for value, id in meta['catval2ind'][feature].items()}
    return reverse[id]


def get_id_for_value(feature, value):
    return meta['catval2ind'][feature][value]


def get_values_of_feature(feature):
    return meta["catuniques"][feature]


def get_number_of_variables():
    return meta['n_cat']


def get_variable_sizes():
    variable_sizes = []
    for feature in meta['catuniques']:
        variable_sizes.append(len(meta['catuniques'][feature]))
    return variable_sizes


def get_data():
    # load data
    data = pd.read_csv(os.path.join(os.path.dirname(__file__), _filepath))
    # replace values with ids
    for feature in data:
        data[feature] = data[feature].map(meta['catval2ind'][feature])
    return data


def create_evidence_tensors(evidence, replace=None):
    tensors = []
    for feature in evidence:
        feature_tensor = []
        for value in evidence[feature]:
            if isinstance(replace, dict):
                if feature in replace:
                    value = replace[feature]
            feature_tensor.append(get_tensor_for_feature_value(feature, value))
        tensors.append(np.array(feature_tensor))
    return tensors


meta = {'n_cat': 10, 'n_cg': 0, 'n_data': 286,
        'categoricals': ['Class', 'age', 'menopause', 'tumor-size', 'inv-nodes', 'node-caps', 'deg-malig', 'breast',
                         'breast-quad', 'irradiat'], 'numerical': [],
        'catval2ind': {'Class': {'no-recurrence-events': 0, 'recurrence-events': 1},
                       'age': {'l20-29': 0, 'l30-39': 1, 'l40-49': 2, 'l50-59': 3, 'l60-69': 4, 'l70-79': 5},
                       'menopause': {'ge40': 0, 'lt40': 1, 'premeno': 2},
                       'tumor-size': {'10-14': 0, '50-54': 1, 'l0-4': 2, 'l15-19': 3, 'l20-24': 4, 'l25-29': 5,
                                      'l30-34': 6, 'l35-39': 7, 'l40-44': 8, 'l45-49': 9, 'l5-9': 10},
                       'inv-nodes': {'12-14': 0, '15-17': 1, '24-26': 2, '6-8': 3, '9-11': 4, 'l0-2': 5, 'l3-5': 6},
                       'node-caps': {'?': 0, 'no': 1, 'yes': 2}, 'deg-malig': {'l1': 0, 'l2': 1, 'l3': 2},
                       'breast': {'left': 0, 'right': 1},
                       'breast-quad': {'?': 0, 'central': 1, 'left_low': 2, 'left_up': 3, 'right_low': 4,
                                       'right_up': 5}, 'irradiat': {'no': 0, 'yes': 1}}, 'cat_in_indexform': False,
        'cat_glims': list([0, 2, 8, 11, 22, 29, 32, 35, 37, 43, 45]), 'sizes': [2, 6, 3, 11, 7, 3, 3, 2, 6, 2],
        'catuniques': {'Class': ['no-recurrence-events', 'recurrence-events'],
                       'age': ['l20-29', 'l30-39', 'l40-49', 'l50-59', 'l60-69', 'l70-79'],
                       'menopause': ['ge40', 'lt40', 'premeno'],
                       'tumor-size': ['10-14', '50-54', 'l0-4', 'l15-19', 'l20-24', 'l25-29', 'l30-34', 'l35-39',
                                      'l40-44', 'l45-49', 'l5-9'],
                       'inv-nodes': ['12-14', '15-17', '24-26', '6-8', '9-11', 'l0-2', 'l3-5'],
                       'node-caps': ['?', 'no', 'yes'], 'deg-malig': ['l1', 'l2', 'l3'], 'breast': ['left', 'right'],
                       'breast-quad': ['?', 'central', 'left_low', 'left_up', 'right_low', 'right_up'],
                       'irradiat': ['no', 'yes']}}
