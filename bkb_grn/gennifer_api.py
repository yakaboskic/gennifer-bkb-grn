import os
import contextlib
import pandas as pd
import numpy as np

from pybkb.learn import BKBLearner

from .zenodo import load_file
from .discretize import ClusterDiscretizer


def make_bkb_data(discretized_edata):
    feature_states = set()
    for (_, col_data) in discretized_edata.iteritems():
        for fs in col_data.items():
            feature_states.add(fs)
    feature_states = list(feature_states)
    feature_states_map = {fs: idx for idx, fs in enumerate(feature_states)}
    bkb_data = []
    srcs = []
    for (src, col_data) in discretized_edata.iteritems():
        srcs.append(src)
        row = np.zeros(len(feature_states))
        for fs in col_data.items():
            row[feature_states_map[fs]] = 1
        bkb_data.append(row)
    bkb_data = np.array(bkb_data)
    return bkb_data, feature_states, srcs

def generateInputs(zenodo_id):
    '''
    Function to generate desired inputs for PyBKB.
    '''
    ExpressionData = load_file(zenodo_id, 'ExpressionData.csv')
    discretizer = ClusterDiscretizer()
    discretized_edata = discretizer.discretize(ExpressionData)
    return make_bkb_data(discretized_edata)

    
def run(data, feature_states, srcs, palim):
    '''
    Function to run BKB learning algorithm.
    '''
    with contextlib.redirect_stderr(open(os.devnull, 'w')):
        bkb_learner = bkb_learner = BKBLearner(backend='gobnilp', score='mdl_ent', distributed=False, palim=palim)
        bkb_learner.fit(data, feature_states, srcs=srcs, collapse=True)

    # Return networkx data
    return bkb_learner.learned_bkb.construct_nx_graph(only_rvs=True, show_num_edges=True)

def parseOutput(nx_data):
    '''
    Function to parse outputs from BKB NetworkX data to result format.
    ''' 
    results = {'Gene1': [], 
               'Gene2': [],
               'EdgeWeight': []}

    for gene1, gene2, edge_data in nx_data.edges.data():
        results['Gene1'].append(gene1)
        results['Gene2'].append(gene2)
        results['EdgeWeight'].append(str(edge_data['count']))
    
    return results
