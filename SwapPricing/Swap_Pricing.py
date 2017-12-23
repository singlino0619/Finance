
# coding: utf-8

# # Get discount factor for JPY
# - input: MoneyMarket (short term interest rate), Swap rate.
# - output: discount factors for each tenor listed by MoneMarket and Swap rate.
# 
# ## Pricing
# ### Swap pricing formula
# The value of the exchange between a floot and a fixed side is given by
# $$
# V = \sum_{i = 1}^{N}  L(t_{i-1}, t_{i}) \times DF(t_{i}) \times \delta_{i} - \sum_{i = 1}^{N} SwapRate \times DF(t_{i})\times \delta_{i},
# $$
# where $L(t_{i-1}, t_{i})$ is the floot interest rate between $t_{i-1}$ and $t_{i}$, $DF(t_{i})$ is a discount factor, $\delta_{i}$ is a day-count-fraction and $SwapRate$ is a Swap rate which means a par rate for a swap trade.
# 
# ### Bootstrap method for getting discount factors
# Discount factors as of today can be estimated from a par swap trade which corresponds to $V = 0$ under swap pricing formula. 
# For example, let us consider a swap trade with maturity of 1.5 year. The discount factor for 1.5 year $DF(t_{1.5Y})$ is calculated by solveing the following equation:
# $$
# \sum_{i = 1}^{3}  L(t_{i-1}, t_{i}) \times DF(t_{i}) \times \delta = \sum_{i = 1}^{3} SwapRate(1.5Y) \times DF(t_{i})\times \delta
# $$
# 
# where a quoted swap rate is used for $SwapRate(1.5Y)$, the day-count-fraction $\delta$ is asuumed 6 month and the floot side interest rate is assumed that a following model expressed as
# $$
# L(t_{i-1}, t_{i}) = \frac{1}{\delta} \Big( \frac{ DF(t_{i-1}) }{ DF(t_{i}) } - 1 \Big).
# $$
# The above equation can be solved by using $DF(t_{0.5Y})$, $DF(t_{1.0Y})$ and the floot interest rate which is defined as above equation. As a result, the discount factor $DF(t_{1.5Y})$  is given by
# $$
# DF(t_{1.5Y}) = \frac{1}{(1 + \delta \times SwapRate(1.5Y))} \Big( DF(t_{0}) - SwapRate(1.5Y) \times \delta \times \big(DF(t_{0.5Y}) + DF(t_{1.0Y}) \big) \Big),
# $$
# 
# where $DF(t_{0.5Y})$ and $DF(t_{1.0Y})$ is calculated by using a quoted LIBOR (the rate of Money Market). The short rate of Money Market means spot rate, where the cashflows is expressed as only two terms. For example, $DF(t_{0.5Y})$ is given by
# $$
# DF(t_{0.5Y}) = \frac{1}{( 1 + \delta \times L(0.0Y, 0.5Y))},
# $$
# 
# where $L(0.0Y, 0.5Y)$ is the LIBOR rate between today and 6 month later.
# Discount factors after $t_{1.5Y}$ can be calculated by the same way as the derivation of $DF(t_{1.5Y})$.
# This method of getting discount factors gradually is called Bootstrap method.
# 
# [](
# Continuously, let us consider a T/N swap trade. When $V = 0$ under the swap pricing formula, it is written by 
# $$
# FixedRate(T/N)\ ( DF(t_{O/N}) \times \delta_{1} + DF(t_{T/N}) \times \delta_{2} ) \\
#  = ( DF(t_{O/N}) - DF(t_{0}) ) \delta_{1} + (DF(t_{T/N}) - DF(t_{O/N})) \delta_{2}, 
# $$  
# \
# where $\delta_2$ is a day-count-fraction between $t_{O/N}$ and $t_{T/N}$ and a quoted Tomorrow-Next Rate is used for $FixedRate(T/N)$. 
# This equation can be solved for $DF(t_{T/N})$ by using $DF(t_{O/N})$ which is derived from the above equation. 
# In this way, discount factors at each tenor is calculated. This method for getiing discount factors is called as Bootstrap method. 
# The expression of $DF(t_{T/N})$ is given by 
# $$
# DF(t_{T/N}) = \frac{ FixedRate(T/N)\times DF(t_{O/N}) + DF(t_0) }{ 1 - FixedRate(T/N) } 
# $$
# )

# In[11]:


import matplotlib.pyplot as plt
import numpy as np
import datetime

class getDF_moneymarket:
'''    def __init__(self, libor_rate, start_day, end_day):
        self.libor_rate = libor_rate
        self.start_day = start_day
        self.end_day = end_day
        self.datetime_obj_start = datetime.datetime.strptime(start_day, '%Y/%m/%d')
        self.datetime_obj_end = datetime.datetime.strptime(end_day, '%Y/%m/%d')
        self.daycount = (self.datetime_obj_end - self.datetime_obj_start).days / 360
        self.discount_factor = 0
'''
    def __init__(self, today, array_ccy):
            self._start_day = today

    def getDF(self, seq_moneymarket):
        


# In[12]:


DF = getDF_moneymarket(0.2, '2017/12/18', '2019/12/30')
print(DF.discount_factor)
print(DF.getDF())
print(DF.discount_factor)


# In[3]:


DF1 = getDF_moneymarket(0.3, '2017/12/18', '2018/3/20')
DF1.getDF()


# In[66]:


get_ipython().magic('matplotlib inline')
import numpy as np
import csv
import time
import datetime
import matplotlib.pyplot as plt

with open('sample_moneymarket.csv', 'r') as csvfile:
    reader_obj = csv.reader(csvfile)
    # rewritten header_obj by using next method(???)
    header_obj = next(reader_obj)
    mm_list = []
    for row in reader_obj:
        mm_list.append(row)
        
mm_list




def get_DF(money_market_list):
    list_len = len(money_market_list)
    discount_factor = np.zeros(list_len*2).reshape(list_len, 2)
    discount_factor = [["",0.0] for i in range(list_len)]
    day_count_fraction = np.zeros(list_len)
    # substitution the kinf of trade
    for i in range(0,list_len):
             discount_factor[i][0] = money_market_list[i][0]
    # calc daycount-fraction
    convention = 360.0
    for i in range(0, len(day_count_fraction)):
        day_count_fraction[i] = calc_daycount(money_market_list[i][1], money_market_list[i][2], convention)
    # calculate DF of O/N
    discount_factor[0][1] = 1.0 / (1.0 + day_count_fraction[0] * float(money_market_list[0][3]))
    # calculate DF of  T/N
    discount_factor[1][1] = discount_factor[0][1] /(1.0 + day_count_fraction[1]*float(money_market_list[1][3]))
    # calculate DF after 1W
    for i in range(2, list_len):
        discount_factor[i][1] = discount_factor[1][1] / (1.0 + day_count_fraction[i] * float(money_market_list[i][3]))
    return discount_factor
                                   
def calc_daycount(start_day, end_day, convention):
    datetime_obj_start = datetime.datetime.strptime(start_day, '%Y/%m/%d')
    datetime_obj_end = datetime.datetime.strptime(end_day, '%Y/%m/%d')
    daycount = (datetime_obj_end - datetime_obj_start).days / convention
    return daycount

def draw_DF(seq_discount_factor):
        list_len = len(seq_discount_factor)
        seq_DF = np.zeros(list_len)
        for i in range(0, list_len):
            seq_DF[i] = seq_discount_factor[i][1]
        plt.plot(seq_DF)
        plt.ylim([0,1.0])
        
                                   
list_discountfactor = get_DF(mm_list)
draw_DF(list_discountfactor)


# In[43]:


[[] for i in range(5)]


# In[55]:


calc_daycount(mm_list[0][1], mm_list[0][2], 360)
calc_daycount(mm_list[5][1], mm_list[5][2], 360)


# In[56]:


float(mm_list[0][3])


# ### エラーメッセージ
# 
# ---
# TypeError                                 Traceback (most recent call last)
# <ipython-input-29-8d376080b34d> in <module>()
#      33     return daycount
#      34 
# ---> 35 get_DF(mm_list)
# 
# <ipython-input-29-8d376080b34d> in get_DF(money_market_list)
#      24     convention = 360.0
#      25     day_count_fraction[0] = calc_daycount(money_market_list[0][1], money_market_list[0][2], convention)
# ---> 26     discount_factor[0][1] = 1.0 / (1.0 + day_count_fraction[0] * money_market_list[0][3])
#      27     return discount_factor
#      28 
# 
# TypeError: 'numpy.float64' object cannot be interpreted as an integer
# 
# ---
# ### 解決策
# - 数値と文字列が混ざっているのでどちらかに統一すべし
