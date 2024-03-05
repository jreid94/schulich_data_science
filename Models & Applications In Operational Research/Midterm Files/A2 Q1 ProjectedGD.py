# -*- coding: utf-8 -*-
"""
OMIS 6000 - Assignment 2 - Question 1
@author: Adam Diamant (2023)
"""

import gurobipy as gp
from gurobipy import GRB, QuadExpr
import math

# Set the stopping criterion
stopping_criterion = 1e-6

# Hard code the price-response function coefficients
a0 = 35234.54578551236
b0 = -45.89644970638436
a1 = 37790.24083213697
b1 = -8.22779417263456

# Starting prices
x0 = 0
x1 = 0

# Step size parameter
eta = 0.001

# Create a new model
model = gp.Model("Pricing")

# Create decision variables
p = model.addVars(2, lb=0, name="prices", vtype=GRB.CONTINUOUS)

# Set the Gurobi environment parameter to not print output
model.setParam('OutputFlag', 0)

# Avoid an infinite loop 
for i in range(5000):
    
    # Save the old pricing values
    x0_old = x0
    x1_old = x1
    
    # Create new values from gradient descent
    x0 += eta*(a0+2*b0*x0)
    x1 += eta*(a1+2*b1*x1)
    
    # Set the objective function which changes in each iteration because the prices are updated
    objective = QuadExpr((p[0] - x0)*(p[0] - x0) + (p[1] - x1)*(p[1] - x1))
    model.setObjective(objective, GRB.MINIMIZE)
    
    # Add constraints including demand non-negativity and price-ordering
    model.addConstr(a0+b0*p[0] >= 0)
    model.addConstr(a1+b1*p[1] >= 0)
    model.addConstr(p[0] <= p[1])
    
    # Optimize model which projects the current solution back onto the constraint set
    model.optimize()
    
    # Get the projected solution
    x0 = p[0].x
    x1 = p[1].x
    
    # Compute the norm to determine stopping condition. You can also use the function numpy.linalg.norm, for instance.
    if math.sqrt((x0 - x0_old)*(x0 - x0_old) + (x1 - x1_old)*(x1 - x1_old)) < stopping_criterion:        
        break
    
    # Reset the model
    model.reset()
    
print(i, x0, x1)
    