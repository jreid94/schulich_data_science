"""
@author: Adam Diamant (2023)
"""

import matplotlib.pyplot as plt
from gurobipy import GRB
import gurobipy as gb
import pandas as pd
import yfinance as yf
import numpy as np
from math import sqrt

# Read the ticker symbols of the S&P 500 from the file
symbols = pd.read_csv("symbols.csv")
stocks = symbols["Symbol"].values.tolist()

# Download two years worth of data for each stock from Yahoo Finance
data = yf.download(stocks, period='2y')

# Matrix of daily closing prices for each stock in the S&P 500
closes = np.transpose(np.array(data.Close)) 

# The absolute change in daily closing prices for each stock on the S&P 500
absdiff = np.diff(closes)                   

# Compute the daily return for each stock on the S&P 500 by dividing the 
# absolute difference in closes prices by the starting share price. Note
# that this normalizes the return so it doesn't depend on share prices.
reldiff = np.divide(absdiff, closes[:,:-1]) 

# The mean return for each stoch on the S&P 5007
mu = np.mean(reldiff, axis=1)

# The standard deviation of returns (diagonal of the covariance matrix)
std = np.std(reldiff, axis=1)               

# The convariance matrix associated with the returns 
sigma = np.cov(reldiff)                     

# Find the nan values for mu and std
nan_indices_mu = np.isnan(mu)
nan_indices_std = np.isnan(std)
nan_indices_combined = np.logical_or(nan_indices_mu, nan_indices_std) 

# Remove the nan values for mu, std, and sigma
mu = mu[~nan_indices_combined]
std = std[~nan_indices_combined]
sigma = sigma[~nan_indices_combined][:, ~nan_indices_combined]

# Create an empty model
model = gb.Model('Portfolio Optimization')

# Add matrix variable for the stocks
stock_index = range(len(mu))
x = model.addVars(stock_index, lb=0, vtype=gb.GRB.CONTINUOUS, name="Fraction")

# Objective is to minimize risk (squared).  This is modeled using the
# covariance matrix, which measures the historical correlation between stocks
portfolio_risk = gb.quicksum(x[i]*x[j]*sigma[i,j] for i in stock_index for j in stock_index)
model.setObjective(portfolio_risk, GRB.MINIMIZE)

# The proportion constraints
model.addConstr(gb.quicksum(x[i] for i in stock_index) == 1)

# Optimize model to find the minimum risk portfolio
model.optimize()

# Flatten
x_flat = np.array([x[i].x for i in stock_index])

# Comptue the minimum risk and the return
minrisk_volatility = sqrt(model.objval)
minrisk_return = mu @ x_flat

# Create an expression representing the expected return for the portfolio
target = model.addConstr(gb.quicksum(mu[i]*x[i] for i in stock_index) >= minrisk_return, 'target')

# Solve for efficient frontier by varying the mean return
filtered_stocks = [stock for i, stock in enumerate(stocks) if not nan_indices_combined[i]]
frontier = np.empty((2,0))
for r in np.linspace(mu.min(), mu.max(), 25):
    target.rhs = r
    model.optimize()
    frontier = np.append(frontier, [[sqrt(model.objval)],[r]], axis=1)


# Plot the efficient frontier
fig, ax = plt.subplots(figsize=(10,8))

# Plot volatility versus expected return for individual stocks
ax.scatter(x=std, y=mu, color='Blue', label='Individual Stocks')
for i, stock in enumerate(filtered_stocks):
    ax.annotate(stock, (std[i], mu[i]))

# Plot volatility versus expected return for minimum risk portfolio
ax.scatter(x=minrisk_volatility, y=minrisk_return, color='DarkGreen')
ax.annotate('Minimum\nRisk\nPortfolio', (minrisk_volatility, minrisk_return), horizontalalignment='right')

# Plot efficient frontier
ax.plot(frontier[0], frontier[1], label='Efficient Frontier', color='DarkGreen')

# Format and display the final plot
ax.axis([frontier[0].min()*0.7, frontier[0].max()*1.3, mu.min()*1.2, mu.max()*1.2])
ax.set_xlabel('Volatility (standard deviation)')
ax.set_ylabel('Expected Return')
ax.legend()
ax.grid()
plt.show()