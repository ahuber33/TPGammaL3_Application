import numpy as np

def load_branch_data(tree, branch_name):
    data = tree[branch_name].array(library="np")
    return data[data > 0]

def apply_resolution(data, E_ref, R_ref):
    resolution = R_ref * np.sqrt(E_ref / data)
    sigma_array = (data * 0.01 * resolution) / 2.355
    return np.random.normal(loc=data, scale=sigma_array)
