
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import datetime


# In[2]:


import subprocess
subprocess.run(['jupyter', 'nbconvert', '--to', 'python', 'calc_KVA.ipynb'])


# In[8]:


df_ead_profile = pd.read_csv('SACCR_EAD_profile.csv')
df_ead_profile


# In[9]:


array_data_grid = df_ead_profile.columns.values.tolist()
del array_data_grid[0]
array_data_grid


# In[10]:


array_ead = df_ead_profile.iloc[0].values.tolist()
del array_ead[0]
array_ead


# In[22]:


def trapezoidal_rule(array_func_i, array_func_ip1):
    function = (array_func_i + array_func_ip1)/2
    return function

def calc_KVA(capital_cost, risk_weight, alpha, array_EAD_profile, array_grid, netting_effect):
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
        KVA = KVA + capital_cost / alpha * risk_weight * DF * delta_t * trapezoidal_rule(array_ead[i], array_ead[i+1])
    if(netting_effect==True):
        KVA = KVA * 0.5
    else:
        KVA = KVA
    return KVA


# In[23]:


calc_KVA(0.6, 0.02, 1.4, array_ead, array_data_grid, False)

