
# coding: utf-8

# In[145]:


get_ipython().magic('matplotlib inline')
import numpy as np
import random
import math
import matplotlib.pyplot as plt

def BlackSholes(drift, vola, init, t, rand):
    S_t = init * math.exp((drift - vola**2 / 2) * t + vola * math.sqrt(t) * rand )
    return S_t

drift = 0.3
vola = 0.3
maturity = 1 # unit: year
NumberOfPath = 100000
StockPrice = np.zeros(NumberOfPath)
StockPrice[0] = 100
delta_t = maturity / NumberOfPath
for i in range(1, NumberOfPath):
    StockPrice[i] = BlackSholes(drift, vola, StockPrice[i-1], delta_t, random.gauss(0,1))
    
#plt.plot(StockPrice)
#Result = sum()
#print(StockPrice)


# In[144]:


#TODO make class for returning process of Stock Price.
#TODO write code for deriving call option price in the balck-sholes model.

