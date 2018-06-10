
# coding: utf-8

# In[117]:


import pandas as pd
import numpy as np
import datetime


# In[ ]:


import subprocess
subprocess.run(['jupyter', 'nbconvert', '--to', 'python', 'calc_KVA.ipynb'])


# In[118]:


df_ead_profile = pd.read_csv('SACCR_EAD_profile.csv')
df_ead_profile


# In[119]:


array_data_grid = df_ead_profile.columns.values.tolist()
del array_data_grid[0]
array_data_grid


# In[111]:


array_ead = df_ead_profile.iloc[0].values.tolist()
del array_ead[0]
array_ead


# In[120]:


def calc_KVA(capital_cost, risk_weight, alpha, array_EAD_profile, array_grid):
    int_num = len(array_grid)
    maturity_date = array_grid[int_num-1]
    KVA = 0.0
    datetime_obj_maturity = datetime.datetime.strptime(maturity_date, '%Y/%m/%d')
    for i in range(0, int_num -1):
        datetime_obj_date_i = datetime.datetime.strptime(array_grid[i], '%Y/%m/%d')
        datetime_obj_date_i_p1 = datetime.datetime.strptime(array_grid[i+1], '%Y/%m/%d')
        remaining_maturity = ((datetime_obj_maturity - datetime_obj_date_i).days) /365
        DF = (1.0 - np.exp(-0.05*remaining_maturity)/(0.05*remaining_maturity))
        delta_t = ((datetime_obj_date_i_p1 - datetime_obj_date_i).days) /365
        KVA = KVA + capital_cost / alpha * risk_weight * float(array_ead[i]) * DF * delta_t
    return KVA


# In[121]:


calc_KVA(0.6, 0.02, 1.4, array_ead, array_data_grid)

