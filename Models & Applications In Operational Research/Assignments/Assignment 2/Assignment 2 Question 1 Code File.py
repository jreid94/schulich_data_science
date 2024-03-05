
import gurobipy as gp
from gurobipy import Model, GRB
import pandas as pd
import numpy as np


path = r'C:\Users\anant\OneDrive\Desktop\MBAN\OMIS 6000\Assignment\2'
file = '\price_response.csv'

file_path = path + file


price_df = pd.read_csv(file_path) 


print(price_df)


# Basic version coefficients

a1, capacity1 = price_df.loc[0, ['Intercept', 'Capacity']]


b1 = -price_df.loc[0, 'Sensitivity']


# Advanced version coefficients

a2, capacity2 = price_df.loc[1, ['Intercept', 'Capacity']]


b2 = -price_df.loc[1, 'Sensitivity']


m = Model("Optimal_Pricing")


# Add variables for prices

p1 = m.addVar(lb=0, name="Price_Basic")
p2 = m.addVar(lb=0, name="Price_Advanced")


# Objective: Maximize total revenue considering the linear price response functions

m.setObjective(p1 * (a1 - b1 * p1) + p2 * (a2 - b2 * p2), GRB.MAXIMIZE)


# Constraint: The Advanced version should have a higher price compared to the Basic one

m.addConstr(p2 >= p1, "Price_Ordering")


# Add capacity constraints

m.addConstr(a1 - b1 * p1 <= capacity1, "Capacity_Basic")


m.addConstr(a2 - b2 * p2 <= capacity2, "Capacity_Advanced")


# Optimize the model

m.optimize()


print(f"Optimal Price for Basic Version: {p1.X}")


print(f"Optimal Price for Advanced Version: {p2.X}")


print(f"Maximized Revenue: {m.ObjVal}")


# 2.


# Initialize prices

p1, p2 = 0, 0


# Step size

step_size = 0.001


# Stopping criterion

tol = 1e-6


delta = 1


while delta > tol:
   
    # Calculate gradients based on the revenue function's derivative
    grad_p1 = a1 - 2 * b1 * p1
    grad_p2 = a2 - 2 * b2 * p2

    # Update prices based on gradients
    new_p1 = p1 + step_size * grad_p1
    new_p2 = p2 + step_size * grad_p2

    # Quadratic programming model for projection
    
    gd_m = Model("gd_Optimal_Pricing")
    proj_p1 = gd_m.addVar(lb=0, ub=capacity1, name="proj_p1")
    proj_p2 = gd_m.addVar(lb=0, ub=capacity2, name="proj_p2")

    # Objective: Minimize the distance between new prices and projected prices
    gd_m.setObjective((proj_p1 - new_p1)*(proj_p1 - new_p1) + (proj_p2 - new_p2)*(proj_p2 - new_p2), GRB.MINIMIZE)

    # Constraints
    gd_m.addConstr(proj_p2 >= proj_p1, "PriceOrdering")

    # Optimize the model
    gd_m.optimize()

    # Extract the projected prices
    updated_p1 = proj_p1.X
    updated_p2 = proj_p2.X

    # Calculate the maximum change in price for the stopping criterion
    delta = max(abs(updated_p1 - p1), abs(updated_p2 - p2))

    # Update the prices for the next iteration
    p1, p2 = updated_p1, updated_p2


print(f"Optimal Price for Basic Version: {p1}")
print(f"Optimal Price for Advanced Version: {p2}")

# 3.


quad_m = Model("quadratic_optimization")


prices = quad_m.addVars(price_df.index, lb=0, name="p")

print(prices)


# Objective: Maximize total revenue considering the price-response function for each product

quad_m.setObjective(sum(prices[i] * (price_df.loc[i, 'Intercept'] + price_df.loc[i, 'Sensitivity'] * prices[i]) for i in price_df.index), GRB.MAXIMIZE)


# Constraints: Price ordering within each product line

for line in range(1, 4):  # Assuming 3 lines
    for version in range(1, 3):  # Basic to Advanced, Advanced to Premium
        quad_m.addConstr(prices[(line-1)*3 + version - 1] <= prices[(line-1)*3 + version], name=f"ordering_{line}_{version}")


# Adding capacity constraints

for i in price_df.index:
    demand = price_df.loc[i, 'Intercept'] + price_df.loc[i, 'Sensitivity'] * prices[i]
    quad_m.addConstr(demand <= price_df.loc[i, 'Capacity'], name=f"capacity_{i}")



# Optimize the model

quad_m.optimize()


for constr in quad_m.getConstrs():
    print(f"Name: {constr.ConstrName}, Expression: {quad_m.getRow(constr)}")


# Extract optimal prices and calculate total revenue

optimal_prices = {v.VarName: v.X for v in quad_m.getVars()}
optimal_revenue = quad_m.ObjVal


print(optimal_prices)
print(optimal_revenue)


# 4.


quad_m_b = Model("quadratic_optimization_all_constraints")


prices = quad_m_b.addVars(price_df.index, lb=0, name="p")


# Objective: Maximize total revenue considering the price-response function for each product

quad_m_b.setObjective(sum(prices[i] * (price_df.loc[i, 'Intercept'] + price_df.loc[i, 'Sensitivity'] * prices[i]) for i in price_df.index), GRB.MAXIMIZE)


# Constraints: Price ordering within each product line

for line in range(1, 4):  # Assuming 3 lines
    for version in range(1, 3):  # Basic to Advanced, Advanced to Premium
        quad_m_b.addConstr(prices[(line-1)*3 + version - 1] <= prices[(line-1)*3 + version], name=f"ordering_within_{line}_{version}")



# Adding capacity constraints

for i in price_df.index:
    demand = price_df.loc[i, 'Intercept'] + price_df.loc[i, 'Sensitivity'] * prices[i]
    quad_m_b.addConstr(demand <= price_df.loc[i, 'Capacity'], name=f"capacity_{i}")


# Constraints for price increases across product lines for the same version

for version in range(3):
    quad_m_b.addConstr(prices[version] <= prices[version + 3], name=f"cross_ordering_1_to_2_{version}")
    quad_m_b.addConstr(prices[version + 3] <= prices[version + 6], name=f"cross_ordering_2_to_3_{version}")


# Optimize the model

quad_m_b.optimize()


for constr in quad_m_b.getConstrs():
    print(f"Name: {constr.ConstrName}, Expression: {quad_m_b.getRow(constr)}")


# Extract optimal prices and calculate total revenue

optimal_prices = {v.VarName: v.X for v in quad_m_b.getVars()}
optimal_revenue = quad_m_b.ObjVal


print(optimal_prices)
print(optimal_revenue)


# 5.

# - Scenario (d) added constraints to ensure that prices increase not only within each product line but also across the different versions of the products (ensuring, for example, that a FusionBook Elite is more expensive than an InfiniteEdge Notebook, which in turn is more expensive than an EvoTech Pro).
# 
# - This approach provides a consistent pricing logic across the entire product range, potentially simplifying the overall pricing structure and making it easier for customers to navigate choices across different product lines.
# 
# -  It allows TechEssentials Inc. to clearly differentiate between its product lines, making it easier for consumers to understand the hierarchy and value proposition of each product.
# 
# - It aligns with customer expectations that a product with more features or from a supposedly higher-end line should cost more.


# 6.

# - The model assumes a linear relationship between price and demand, which is a simplification. In reality, the relationship might be non-linear. For example, small price changes might not significantly affect demand until a certain threshold is reached, beyond which demand might drop sharply. Including non-linear effects could provide a more accurate representation of how price changes affect demand.
# 
# - The model uses a single sensitivity value for each product, which assumes uniform price sensitivity across all potential customers. However, different customer segments may have varying sensitivities to price changes. A model that differentiates between these segments could allow for more nuanced and effective pricing strategies.


