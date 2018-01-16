
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

# In[2]:


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
        


# In[3]:


DF = getDF_moneymarket(0.2, '2017/12/18', '2019/12/30')
print(DF.discount_factor)
print(DF.getDF())
print(DF.discount_factor)


# In[4]:


DF1 = getDF_moneymarket(0.3, '2017/12/18', '2018/3/20')
DF1.getDF()


# In[5]:


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




def get_DF_MM(money_market_list):
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

def get_DF_SW(money_market_list, swap_rate_list):
    DF_moneymarket = get_DF_MM(money_market_list)


    
                                   
list_discountfactor = get_DF(mm_list)
list_discountfactor
# draw_DF(list_discountfactor)


# In[6]:


with open('sample_moneymarket.csv', 'r') as csvfile:
    reader_obj = csv.reader(csvfile)
    # rewritten header_obj by using next method(???)
    header_obj = next(reader_obj)
    mm_list = []
    for row in reader_obj:
        mm_list.append(row)
       
mm_list


# # 1/15
# - データの加工
#     - 小数点表記 ("{:.1f}".format())
#     - 文字列の結合　（+でできる）
# - 空のリスト作成
#     - 内包表記 -> [5 for i in range(10)] -> 5が１０個のリスト

# In[7]:


with open('sample_swaprate.csv', 'r') as csvfile:
    reader_obj = csv.reader(csvfile)
    # rewritten header_obj by using next method(???)
    header_obj = next(reader_obj)
    swap_rate_list = []
    for row in reader_obj:
        swap_rate_list.append(row)
    temp_num = [[] for i in range(len(swap_rate_list))] # comprehension expression for making null list.
    ### proceccing the expression for the type of 1Y to 1.0Y.
    for i in range(len(swap_rate_list)):
        if (len(swap_rate_list[i][0]) == 2):
            temp_num[i] = "{:.1f}".format(int(swap_rate_list[i][0][0])) + swap_rate_list[i][0][1]
            swap_rate_list[i][0] = temp_num[i]
        elif (len(swap_rate_list[i][0]) == 3):
            temp_num[i] = "{:.1f}".format(int(swap_rate_list[i][0][0:2])) + swap_rate_list[i][0][2]
            swap_rate_list[i][0] = temp_num[i]
        else:
            break

swap_rate_list


# In[8]:


"{:.1f}".format(132)


# In[9]:


[[1] for i in range(4)]


# In[10]:


calc_daycount(mm_list[0][1], mm_list[0][2], 360)
calc_daycount(mm_list[5][1], mm_list[5][2], 360)


# In[11]:


float(mm_list[0][3])


# # 1/15
# - エクセルのVlookup風の作業
#     - 半年置きのテナーで，空のswap rateのリストを作成
#     - 外部データとして存在する，加工済みの（1Y->1.0Y）データとマッチする行はそのまま置き換え
#     - マッチしない行は据え置きでデフォルトの0を代入したままのリストを作成
#     
# # 1/16
# - get_end_day()関数の作成
#     - 祝日，　土日勘案はせず．(ってかどうやるの？)

# In[75]:


def get_end_day(maturity, start_day):
    datetime_obj_start = datetime.datetime.strptime(start_day, '%Y/%m/%d')
    effective_days = float(maturity[0:len(maturity)-1])*365
    end_day = datetime_obj_start + datetime.timedelta(days=effective_days)
    return end_day.strftime('%Y/%m/%d')

def get_DF_SW(money_market_list, swap_rate_list, tenor):
    seq_len_of_swap_rate = int(30/tenor - 1)
    array_swap_rate = [["", 0, 0, 0] for i in range(seq_len_of_swap_rate )]
    for i in range(2,seq_len_of_swap_rate +2):
        array_swap_rate[i-2][0] = "{}Y".format(i*0.5)
    ## for sentence is nested...
    ## I wanna reviese code, but I have not an idea. Please tell me better coding if you have.
    for i in range(len(array_swap_rate)):
        array_swap_rate[i][1] = swap_rate_list[0][1]
        array_swap_rate[i][2] = get_end_day(array_swap_rate[i][0], array_swap_rate[i][1])
        for j in range(len(swap_rate_list)):
            if (array_swap_rate[i][0] in swap_rate_list[j][0]):
                array_swap_rate[i] = swap_rate_list[j]
                break
                
    return array_swap_rate


# In[76]:


get_DF_SW(mm_list, swap_rate_list, 1/2)


# In[74]:


def get_end_day(maturity, start_day):
    datetime_obj_start = datetime.datetime.strptime(start_day, '%Y/%m/%d')
    effective_days = float(maturity[0:len(maturity)-1])*365
    end_day = datetime_obj_start + datetime.timedelta(days=effective_days)
    return end_day.strftime('%Y/%m/%d')


# In[48]:


import datetime
now = datetime.datetime.today()
d = now + datetime.timedelta(days=10)
d.strftime('%Y/%m/%d')


# In[63]:


get_end_day('2017/12/25', '1.5Y')


# In[108]:


import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
x = np.linspace(0, 10, num=11, endpoint=True)
y = np.cos(-x**2/9.0)
f = interp1d(x, y)
xnew = np.linspace(0, 10, num=41, endpoint=True)
plt.plot(x, y, 'o', xnew, f(xnew), '-')


# In[ ]:


x = np.array([0,1,2,3,4,5,6,7,8,9,10])
y = np.array([20,20,15,14,1,4,2,6,1,1,1])
f = interp1d(x,y)


# In[134]:


x = []
y = []
for i in range(len(swap_rate_list)):
    x.append(float(swap_rate_list[i][0][0:len(swap_rate_list[i][0])-1]))
    y.append(float(swap_rate_list[i][3]))
print(x)
print(y)
f = interp1d(x,y)
xnew = np.linspace(1, 30, num=30, endpoint=True)
plt.plot(xnew, f(xnew), '-')
f(2.1)


# In[116]:


a = []
a.append([1,2])
a.append([2,3])
a


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
