
#!/usr/bin/python2.7
import pandas as pd
import numpy as np

def stratify(data_set,p,selected_columns,filename):
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

    n = np.ceil((p/100.)*len(data_set))

    # How to ensure sample size when rounding like this.
    df['Size'] = np.ceil(n*(df[df.columns[-1]]/len(data_set)).values)


    # And then cut from the larger groups.
    i=0
    ind_list=np.array([])
    for index,comb in df.iterrows():
        df_tmp = data_set[(data_set[comb[:-2].index]==comb[:-2].values).all(axis=1)]
        ind_list=np.append(ind_list,df_tmp.sample(n=df['Size'].iloc[i]).index.values)
        i+=1

    data_set['group-rct'] = ["intervention" if x in ind_list else "control" for x in data_set.index]

    name=filename.rsplit(".")[0]+","+",".join(selected_columns)+'-'+str(p)+'_RCT'+'.xlsx'
    data_set.to_excel(name)
    return name


def update_stratification(data_rct,data_new,sample_p,selected_columns,filename1):
    """ 
    Stratified random sampling
    SPECIAL CASE, WHEN THERE IS ONLY ONE STRATUM PER INDIVIDUAL.
    RAISE MANY ERRORS.
    * The test_size = 1 should be greater or equal to the number of classes = 5
    * 
    * Keep this in mind: https://github.com/scikit-learn/scikit-learn/blob/14031f6/sklearn/model_selection/_split.py#L1190
    """

    #data = pd.read_csv('Randomization_short.csv') #'NYU - Franklin JIYA to randomizecaseloads.xlsx'

    global my_data

    #data_set = pd.read_excel('Randomized/Originals Aug 22/NYU - Franklin JIYA JUNE 20,   AGE,Gender, Race,RISK Score-50_RCT.xlsx')
    #data_new = pd.read_excel('To randomize Aug 22/Franklin County list to randomzie 8-15-17.xlsx')

    p = int(sample_p)/100.
    print("p")
    print(sample_p)
    print("Existing data")
    print(data_rct.head())

    print("New data")
    print(data_new.head())

    data_set = data_rct#pd.read_excel(filename)
    #data_new = pd.read_excel(new_filename)#
    data_set.dropna(axis=0,inplace=True,how='all',subset=data_set.columns[2:])
    data_set.dropna(axis=1,inplace=True,how='all')
    try:
        data_set = data_set.apply(lambda x: x.astype(str).str.lower())
    except UnicodeEncodeError:
        pass

    data_new.dropna(axis=0,inplace=True,how='all',subset=data_new.columns[2:])
    try:
        data_new = data_new.apply(lambda x: x.astype(str).str.lower())
    except UnicodeEncodeError:
        pass

    data_new.columns = [x.lower() for x in data_new.columns]
    data_new.columns = data_new.columns.str.replace('\s+', '')



    #data_set.ix[:, data_set.columns != 'group-rct']
    #data_new = pd.read_excel('test.xlsx')
    data_temp = data_new.append(data_set.ix[:, data_set.columns != 'group-rct']) # there will be a problem with indexing, I can see it coming.
    #selected_columns = [u'Gender',u'Race']
    print(selected_columns)

    print("RCT data:")
    print(data_set.head())

    print("New data:")
    print(data_new.head())

    df = data_temp.groupby(selected_columns).size().reset_index()
    label = str(data_set['group-rct'].value_counts().idxmin())
    control_pre = pd.crosstab(data_set['group-rct'],[pd.Series(data_set[cols]) for cols in selected_columns]).loc[label].reset_index()
    n = np.ceil(p*len(data_temp)) # desired size
    df['Size'] = np.ceil(n*(df[df.columns[-1]]/len(data_temp)).values)
    df = df.merge(control_pre)
    df['Missing'] = df['Size'] - df[label] # parar la llenadera cuando se cumpla la proporcion deseada!
    ind_list=np.array([]) #  Maybe shuffle data_new a little bit
    diff = n - (data_set['group-rct']==label).sum() 
    assigned = 0
    print("Missing")
    print(df['Missing'])
    for index,comb in df.iterrows():
        if assigned < diff:
            df_tmp = data_new[(data_new[comb[:-4].index]==comb[:-4].values).all(axis=1)]  # Combinations of factors.
            sz = len(df_tmp)
            ss = min([sz,df['Missing'].loc[index],diff]) # What I have vs. what I am missing.
            if ss > 0:
                ind_list=np.append(ind_list,df_tmp.sample(n=ss).index.values)
                #need to trim this at the end
                assigned += ss
                if assigned > diff:
                    ind_list = ind_list[:int(diff)]
            else:
                pass
            print("assigned")
            print(assigned)
    print("Len diff")
    print(diff)
    print("Assigned")
    print(assigned)
    print("ind_list")
    print(ind_list)
    ind_list=np.append(ind_list,df[df.index.values in ind_list].sample(n=assigned).index.values) 
    if label == 'control':
        data_new['group-rct'] = ["control" if x in ind_list else "intervention" for x in data_new.index]
    else:
        data_new['group-rct'] = ["intervention" if x in ind_list else "control" for x in data_new.index]


    name=filename1.rsplit(".")[0]+'.xlsx'
    data_new.append(data_set).to_excel(name)
    return name