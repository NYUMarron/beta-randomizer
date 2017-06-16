import pandas as pd 
from sklearn.model_selection import StratifiedShuffleSplit
import numpy as np

#data = pd.read_csv('Randomization_short.csv')
data=pd.read_excel('NYU - Franklin JIYA to randomizecaseloads.xlsx')
# Use regular expressions first to clean up the data

data.dropna(axis=1,inplace=True)#,how='all')

# Keep this in mind: https://github.com/scikit-learn/scikit-learn/blob/14031f6/sklearn/model_selection/_split.py#L1190

sample_size=40
#strat_columns=['Sex','Race','Risk']
strat_columns = ['Gender','RISK Score']

df = data.groupby(strat_columns).count().max(axis=1)
# Create exception here
df = df.reset_index()
df[df.columns[-1]]

# How to ensure sample size when rounding like this.
df['Size'] = np.ceil(sample_size*(df[df.columns[-1]]/len(data)).values)

# And then cut from the larger groups.
i=0
ind_list=np.array([])
for index,comb in df.iterrows():
	df_tmp = data[(data[comb[:-2].index]==comb[:-2].values).all(axis=1)]
	print(df['Size'].iloc[i])
	ind_list=np.append(ind_list,df_tmp.sample(n=df['Size'].iloc[i]).index.values)
	i+=1

data['Group'] = ["Intervention" if x in ind_list else "Control" for x in data.index]