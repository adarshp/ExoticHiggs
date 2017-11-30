import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

train_sets = {}; test_sets = {}

plt.style.use('ggplot')
def get_data(process):
    return pd.read_table(process+'/features.txt',
        usecols=['pt_l1','m_Whad','pt_tau', 'pt_b'])

def get_train_test_data(process, train_size):
    df = pd.read_table(process+'/features.txt',
        usecols=['pt_l1','m_Whad','pt_tau', 'pt_b'])
    train_sets[process], test_sets[process] = train_test_split(df, train_size=train_size)

bgs = ['tt_full', 'tt_semi']
processes = ['Signal'] + bgs

train_sets['Signal'], test_sets['Signal'] = train_test_split(get_data('Signal'))
train_sets['tt_full'], test_sets['tt_full'] = train_test_split(get_data('tt_full'), train_size=0.3)
train_sets['tt_semi'], test_sets['tt_semi'] = train_test_split(get_data('tt_semi'), train_size=0.3)

X_train = pd.concat([train_sets[p] for p in processes])
X_test = pd.concat([test_sets[p] for p in processes])

y_train_signal = [np.ones(train_sets['Signal'].shape[0])]
y_train_bgs = [np.zeros(train_sets[bg].shape[0]) for bg in bgs]
y_train = np.concatenate(tuple(y_train_signal+y_train_bgs))

y_test_signal = [np.ones(test_sets['Signal'].shape[0])]
y_test_bgs = [np.zeros(test_sets[bg].shape[0]) for bg in bgs]
y_test = np.concatenate(tuple(y_test_signal+y_test_bgs))

clf = GradientBoostingClassifier(
                        n_estimators = 1000,
                        learning_rate = 0.025,
                        verbose = 3,
                        )
print(X_train, y_train)
clf.fit(X_train, y_train)

decisions={}
fig, ax = plt.subplots()

for p in ['Signal', 'tt_full']:
    decisions[p] = clf.decision_function(test_sets[p]) 
    ax.hist(decisions[p], label=p, alpha = 0.4, normed=True)

ax.legend()
plt.savefig('bdt_histo.pdf')

