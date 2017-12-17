
# coding: utf-8

# # Get discount factor for JPY
# - input: MoneyMarket (short term interest rate), Swap rate.
# - output: discount factors for each tenor listed by MoneMarket and Swap rate.
# 
# ## Pricing
# ### Swap pricing formula
# The value of the exchange between a floot and a fixed side is given by
# $$
# V = \sum_{i = 1}^{N}  L(t_{i-1}, t_{i}) \times DF(t_{i}) \times \delta_{i} - \sum_{i = 1}^{N} FixedRate \times DF(t_{i})\times \delta_{i},
# $$
# where $L(t_{i-1}, t_{i})$ is the Libor rate between $t_{i-1}$ and $t_{i}$, $DF(t_{i})$ is a discount factor, $\delta_{i}$ is a day-count-fraction and $FixedRate$ is a MoneyMarket rate or Swap rate which means a par rate for a swap trade.
# 
# ### Bootstrap method for getting discount factors
# Discount factors as of today can be estimated from a par swap trade which corresponds to $V = 0$ under swap pricing formula. 
# For example, let us consider a O/N swap trade. The discount factor of O/N $DF(t_{O/N})$ is calculated by
# $$
# DF(t_{O/N}) = \frac{ DF(t_{0}) } { 1 - FixedRate(O/N) },
# $$
# 
# where a quoted Overnight Rate is used for $FixedRate(O/N)$ and $DF(t_{0}) = 1$. Continuously, let us consider a T/N swap trade. When $V = 0$ under the swap pricing formula, it is written by
# $$
# FixedRate(T/N)\ ( DF(t_{O/N}) \times \delta_{1} + DF(t_{T/N}) \times \delta_{2} ) \\
#  = ( DF(t_{O/N}) - DF(t_{0}) ) \delta_{1} + (DF(t_{T/N}) - DF(t_{O/N})) \delta_{2},
# $$
# 
# where $\delta_2$ is a day-count-fraction between $t_{O/N}$ and $t_{T/N}$ and a quoted Tomorrow-Next Rate is used for $FixedRate(T/N)$.
# This equation can be solved for $DF(t_{T/N})$ by using $DF(t_{O/N})$ which is derived from the above equation. In this way, discount factors at each tenor is calculated. This method for getiing discount factors is called as Bootstrap method. The expression of $DF(t_{T/N})$ is given by
# 
# $$
# DF(t_{T/N}) = \frac{ FixedRate(T/N)\times DF(t_{O/N}) + DF(t_0) }{ 1 - FixedRate(T/N) }
# $$
