
#!/usr/bin/python2.7

import numpy as np    
from sklearn.model_selection import StratifiedShuffleSplit, StratifiedKFold

def stratify(data_set,n,selected_columns=['Sex']):
    """ 
    Stratified random sampling
    SPECIAL CASE, WHEN THERE IS ONLY ONE STRATUM PER INDIVIDUAL.
    RAISE MANY ERRORS.
    - The test_size = 1 should be greater or equal to the number of classes = 5
    - 
    """

    return None
    # if data_set is not None:
    #     try:    
    #         sss = StratifiedShuffleSplit(n_splits=1, test_size=n, random_state=2)
    #         #y = np.array(data_set[~data_set.isin(data_set_pre).T.any()][strat_columns])
    #         y = np.array(data_set[selected_columns])
    #         X = np.array([0] * y.shape[0])

    #         for train_index, test_index in sss.split(X, y):
    #             print("TRAIN:", train_index, "TEST:", test_index)
    #             X_train, X_test = X[train_index], X[test_index]
    #             y_train, y_test = y[train_index], y[test_index]

    #         X = X.astype("string")
    #         X[train_index] = "Control"
    #         X[test_index] = "Test"
    #         data_set['Trial'] = X
    #         (prefix, sep, suffix) = filename.rpartition('.')
    #         data_set.to_csv(prefix + '_RCT.csv')
    #         return prefix
    #     except:
    #         return None

        

def parse_column_names(data_set):
    """
    Unify names
    """
    return data_set