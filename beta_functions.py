
#!/usr/bin/python2.7
import pandas as pd
import numpy as np

def stratify(data_set,n,selected_columns,filename):
    """ 
    Stratified random sampling
    SPECIAL CASE, WHEN THERE IS ONLY ONE STRATUM PER INDIVIDUAL.
    RAISE MANY ERRORS.
    * The test_size = 1 should be greater or equal to the number of classes = 5
    * 
    * Keep this in mind: https://github.com/scikit-learn/scikit-learn/blob/14031f6/sklearn/model_selection/_split.py#L1190
    """

    #data = pd.read_csv('Randomization_short.csv') #'NYU - Franklin JIYA to randomizecaseloads.xlsx'
    return None
    #data_set.dropna(axis=1,inplace=True)#,how='all')
    #print(selected_columns)
    #print(data_set.head())
    """
    df = data_set.groupby(selected_columns).count().max(axis=1)
    # Create exception here
    df = df.reset_index()
    df[df.columns[-1]]

    # How to ensure sample size when rounding like this.
    df['Size'] = np.ceil(n*(df[df.columns[-1]]/len(data_set)).values)

    # And then cut from the larger groups.
    i=0
    ind_list=np.array([])
    for index,comb in df.iterrows():
        print(comb)
        df_tmp = data_set[(data_set[comb[:-2].index]==comb[:-2].values).all(axis=1)]
        ind_list=np.append(ind_list,df_tmp.sample(n=df['Size'].iloc[i]).index.values)
        i+=1

    data_set['Group'] = ["Intervention" if x in ind_list else "Control" for x in data_set.index]

    name=filename+'_RCT'
    data_set.to_excel(name+'.xlsx')

    return name
    """



        

def parse_column_names(data_set):
    """
    Unify names
    """
    return data_set