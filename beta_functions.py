
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
    data_set.dropna(axis=1,inplace=True)#,how='all')
    data_set = data_set.apply(lambda x: x.astype(str).str.lower())
    print(selected_columns)
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
        df_tmp = data_set[(data_set[comb[:-2].index]==comb[:-2].values).all(axis=1)]
        ind_list=np.append(ind_list,df_tmp.sample(n=df['Size'].iloc[i]).index.values)
        i+=1

    data_set['Group-RCT'] = ["Intervention" if x in ind_list else "Control" for x in data_set.index]

    name=filename.rsplit(".")[0]+'_RCT'+'.xlsx'
    data_set.to_excel(name)
    return name


    def update_stratification(data_set,p,selected_columns,filename,new_filename):
    """ 
    Stratified random sampling
    SPECIAL CASE, WHEN THERE IS ONLY ONE STRATUM PER INDIVIDUAL.
    RAISE MANY ERRORS.
    * The test_size = 1 should be greater or equal to the number of classes = 5
    * 
    * Keep this in mind: https://github.com/scikit-learn/scikit-learn/blob/14031f6/sklearn/model_selection/_split.py#L1190
    """

    #data = pd.read_csv('Randomization_short.csv') #'NYU - Franklin JIYA to randomizecaseloads.xlsx'

    import pandas as pd
    import numpy as np
    p = 0.50
    data_set = pd.read_excel('test_RCT.xlsx') # this would actually be csv but whatevs
    data_set.dropna(axis=1,inplace=True)
    data_set = data_set.apply(lambda x: x.astype(str).str.lower())
    data_set.ix[:, data_set.columns != 'Group-RCT']
    data_new = pd.read_excel('test.xlsx')
    data_temp = data_new.append(data_set.ix[:, data_set.columns != 'Group-RCT']) # there will be a problem with indexing, I can see it coming.
    selected_columns = [u'Gender',u'Race']
    print(selected_columns)
    df = data_temp.groupby(selected_columns).count().max(axis=1).reset_index()
    control_pre = pd.crosstab(data_set['Group-RCT'],[pd.Series(data_set[cols]) for cols in selected_columns]).loc['control'].reset_index()
    n = p*len(data_temp)
    df['Size'] = np.ceil(n*(df[df.columns[-1]]/len(data_temp)).values)
    df = df.merge(control_pre)
    df['Missing'] = df['Size'] - df.control
    i=0
    ind_list=np.array([])
    for index,comb in df.iterrows():
        df_tmp = data_new[(data_new[comb[:-4].index]==comb[:-4].values).all(axis=1)]
        ss = min(len(df_tmp),df['Missing'].iloc[int(i)])
        if ss > 0:
            ind_list=np.append(ind_list,df_tmp.sample(n=ss).index.values)
        else:
            pass
        i+=1

    data_new['Group-RCT'] = ["Intervention" if x in ind_list else "Control" for x in data_new.index]


    name=filename.rsplit(".")[0]+'_RCT'+'.xlsx'
    data_new.append(data_set).to_excel(name)
        return name