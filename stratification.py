import pandas as pd 
from sklearn.model_selection import StratifiedShuffleSplit
import numpy as np

data = pd.read_csv('Randomization_short.csv')




sample_size=3
strat_columns=['Sex']

# data['fake'] = 'CONTROL'
# data['fake'][[5, 0, 7, 8]] = 'TEST'
# data_list = []
# for cols in strat_columns:
#     data_pre = data[data[cols].isin(data[cols].value_counts()[data[cols].value_counts()<2].index)]
#     data_list.append(data_pre)
#     del(data_pre)
# data_pre = pd.concat(data_list)
sss = StratifiedShuffleSplit(n_splits=1, test_size=sample_size, random_state=2)
#y = np.array(data[~data.isin(data_pre).T.any()][strat_columns])
y = np.array(data[strat_columns])
X = np.array([0] * y.shape[0])

for train_index, test_index in sss.split(X, y):
    print("TRAIN:", train_index, "TEST:", test_index)
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

X = X.astype("string")
X[train_index] = "Control"
X[test_index] = "Test"
data['Trial'] = X
#(prefix, sep, suffix) = filename.rpartition('.')
#data.to_csv(prefix + '_RCT.csv')
