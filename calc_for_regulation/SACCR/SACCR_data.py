
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[11]:


import subprocess
subprocess.run(['jupyter', 'nbconvert', '--to', 'python', 'SACCR_data.ipynb'])


# ### 1. Import SA-CCR data

# In[2]:


df_output = pd.read_csv('SACCR_output.csv')
df_output.head()


# ### 2. Get length of GCIF and GCIF itself without duplication.

# In[3]:


GCIF_LEN = len(df_output[df_output['PROPERTY']=='EAD'])
array_GCIF = df_output[~df_output['GCIF'].duplicated()]['GCIF'].values.tolist()
array_GCIF


# ### 3. Get length of item(EAD, RWA, M)  and array of item

# In[4]:


len_item = len(df_output[~df_output['PROPERTY'].duplicated()])
array_item = df_output[~df_output['PROPERTY'].duplicated()]['PROPERTY'].values.tolist()
array_item


# ### 4. make dictionary SA-CCR data

# In[9]:


array_values = ['' for i in range(3)] # make empty 2 dimensional array using by List Comprehensions
dict_saccr = {'01_GCIF' : array_GCIF}
col_num_values = 2 # place of values in original output data.
for i in range(0, len_item):
    item_name = array_item[i]
    array_values[i] = df_output.iloc[GCIF_LEN*i : GCIF_LEN*(i+1), col_num_values].values.tolist()
    dict_saccr['0{}_'.format(i+2) + array_item[i]] = array_values[i]


# In[10]:


pd.DataFrame(dict_saccr).head()


# ## in case of using CSV reader

# In[12]:


import csv


# In[87]:


with open('SACCR_output.csv', 'r') as csvfile:
    obj_reader = csv.reader(csvfile)
    data = [i for i in obj_reader]


# In[63]:


data

