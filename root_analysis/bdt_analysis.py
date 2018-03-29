import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt


plt.style.use('ggplot')

def get_data(process):
    return pd.read_table('/tmp/'+process+'_features.txt',
         usecols= [
            "pt_l1"  , "eta_l1"  , "phi_l1"  , "e_l1"  ,
            "pt_l2"  , "eta_l2"  , "phi_l2"  , "e_l2"  ,
            "pt_tau" , "eta_tau" , "phi_tau" , "e_tau" ,
            "pt_b1"  , "eta_b1"  , "phi_b1"  , "e_b1"  ,
            "MET", "mH", "mC"
        ])

def calculate_significance(process, train_size, train_sets, test_sets):
    train_sets = {}
    test_sets = {}

    bgs = ['tttautau']
    processes = [process] + bgs

    train_sets[process], test_sets[process] = train_test_split(get_data(process))
    train_sets['tttautau'], test_sets['tttautau'] = train_test_split(get_data('tttautau'),
                                                                 train_size=0.3)

    processes = [process, 'tttautau']
    X_train = pd.concat([train_sets[p] for p in processes])
    X_test = pd.concat([test_sets[p] for p in processes])

    y_train_signal = [np.ones(train_sets[process].shape[0])]
    y_train_bgs = [np.zeros(train_sets[bg].shape[0]) for bg in bgs]
    y_train = np.concatenate(tuple(y_train_signal+y_train_bgs))

    y_test_signal = [np.ones(test_sets[process].shape[0])]
    y_test_bgs = [np.zeros(test_sets[bg].shape[0]) for bg in bgs]
    y_test = np.concatenate(tuple(y_test_signal+y_test_bgs))

    clf = GradientBoostingClassifier()
    clf.fit(X_train, y_train)

    def get_decisions(p):
        return clf.decision_function(test_sets[p])

    def apply_cut(decisions, cutoff):
        return [x for x in decisions if x > cutoff]
        
    decisions={}

    for p in [process, 'tttautau']:
        decisions[p] = clf.decision_function(test_sets[p]) 


if __name__ == '__main__':
    get_train_test_data(sys.argv[1], 0.75, train_sets, test_sets)
