
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
    def __init__(self, libor_rate, start_day, end_day):
        self.libor_rate = libor_rate
        self.start_day = start_day
        self.end_day = end_day
        self.datetime_obj_start = datetime.datetime.strptime(start_day, '%Y/%m/%d')
        self.datetime_obj_end = datetime.datetime.strptime(end_day, '%Y/%m/%d')
        self.daycount = (self.datetime_obj_end - self.datetime_obj_start).days / 360
        self.discount_factor = 0
    
    def getDF(self):
        self.discount_factor = [1 / (1 + self.daycount * self.libor_rate), self.start_day, self.end_day]
        return self.discount_factor


# In[12]:


DF = getDF_moneymarket(0.2, '2017/12/18', '2019/12/30')
print(DF.discount_factor)
print(DF.getDF())
print(DF.discount_factor)


# In[3]:


DF1 = getDF_moneymarket(0.3, '2017/12/18', '2018/3/20')
DF1.getDF()

