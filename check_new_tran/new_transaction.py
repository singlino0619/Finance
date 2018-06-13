
# coding: utf-8

# In[89]:


import pandas as pd
import numpy as np
import datetime


# In[134]:


import subprocess
subprocess.run(['jupyter', 'nbconvert', '--to', 'python', 'new_transaction.ipynb'])


# In[90]:


basedate1 = '2018/6/4'
basedate2 = '2018/6/11'


# In[140]:


def date_to_8digit(excel_format_date):
    dt_obj_date = datetime.datetime.strptime(excel_format_date, '%Y/%m/%d')
    date_to_8_digit = dt_obj_date.strftime('%Y%m%d')
    return date_to_8_digit

def import_tran_csv(basedate):
    date = date_to_8digit(basedate)
    df = pd.read_csv('transaction_' + date + '.csv')
    return df

def transaction_by_comp_num(comp_num, basedate):
    str_comp_num = str(compnum)
    df_tran_csv = import_tran_csv(basedate)
    extract_tran_comp_num =  df_tran_scv.query(str_companu_num + '==' + basedate)
    return extract_tran_comp_num


# In[141]:


df= import_tran_csv('2018/06/04')
df_tran = import_tran_csv('2018/06/04')['company_num']


# In[142]:


df.query('company_num == 1234567890')


# In[144]:


transaction_by_comp_num('1234567890', '20180604')

