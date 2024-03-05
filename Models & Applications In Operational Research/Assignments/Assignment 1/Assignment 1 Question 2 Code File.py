# %% [markdown]
# # Assignment 1, Question 2

# %%
from gurobipy import GRB
import gurobipy as gb

# %%
# Create the optimization model
model = gb.Model("SunnyShore Bay")

# %% [markdown]
# ### Decision Variables

# %%
C = model.addVars(4, lb=0, vtype=GRB.CONTINUOUS, name="Cash Balance")
B = model.addVars(6, lb=0, vtype=GRB.CONTINUOUS, name="Borrow")

# %% [markdown]
# ### Objective Function

# %%
# Define the objective function (minimize total repayment)
model.setObjective(1.0175 * B[0] + 1.0225 * B[1] + 1.0275 * B[2] + 1.0175 * B[3] + 1.0225 * B[4] + 1.0175 * B[5], GRB.MINIMIZE)

# %% [markdown]
# ### Constraints

# %% [markdown]
# 1 month rate = B[0], B[3], B[5]
# 
# 2 month rate = B[1], B[4]
# 
# 3 month rate = B[2]

# %%
model.addConstr(C[0] == 140000 + 180000 - 300000 + B[0] + B[1] + B[2], "May")
model.addConstr(C[1] == C[0] + 260000 - 400000 + B[3] + B[4] - 1.0175 * B[0], "June")
model.addConstr(C[2] == C[1] + 420000 - 350000 + B[5] - 1.0225 * B[1] - 1.0175 * B[3], "July")
model.addConstr(C[3] == C[2] + 580000 - 200000 - 1.0275 * B[2] - 1.0225 * B[4] - 1.0175 * B[5], "August")

# %%
# Borrowing limits
model.addConstr(B[0] + B[1] + B[2] <= 250000, "Borrow_Limit_May")
model.addConstr(B[3] + B[4] <= 150000, "Borrow_Limit_June")
model.addConstr(B[5] <= 350000, "Borrow_Limit_July")

# %%
# Minimum cash balances
model.addConstr(C[0] >= 25000, "Min_Cash_Balance_May")
model.addConstr(C[1] >= 20000, "Min_Cash_Balance_June")
model.addConstr(C[2] >= 35000, "Min_Cash_Balance_July")
model.addConstr(C[3] >= 18000, "Min_Cash_Balance_August")

# %%
# Cash balance ratio constraint at the end of July
model.addConstr(C[2] >= 0.65 * (C[0] + C[1]), "July_Ratio_Constraint")

# %%
# Optimize the model
model.optimize()

# %%
# The status of the model (Optimization Status Codes)
print("Model Status: ", model.status)

# %%
# Number of variables in the model
print("Number of Decision Variables: ", model.numVars)

# %%
# Value of the objective function
print("Total Amount of Money: ", round(model.objVal, 2)) 

# %%
# Print the decision variables
print(model.printAttr('X'))

# %% [markdown]
# ### (a) How many different investments can be made over the 4-month period?

# %% [markdown]
# 6 Investments can be made over the 4 month period
# 
# May: 3
# 
# June: 2 
# 
# July: 1

# %% [markdown]
# ### (b) Write down the cash balance constraint for money on-hand at the end of June.

# %% [markdown]
# June Cash Balance >= 20000 
# 
# OR 
# 
# C[1] >= 20000

# %% [markdown]
# ### (c) Write down the linear ratio constraint associated with the cash balance at the end of July.

# %% [markdown]
# 0.65(C[0] + C[1]) <= C[2] 
# 
# OR 
# 
# 0.65(May Cash Balance + June Cash Balance) <= July Cash Balance

# %% [markdown]
# ### (d) What is the total amount that Sunnyshore Bay has to repay to the bank over the entire season?

# %% [markdown]
# Amount Borrowed: $140,000.00
# 
# Amount Repayed: $142,904.73

# %% [markdown]
# ### (e) How much money does Sunnyshore Bay withdraw in May from all loans?

# %% [markdown]
# May Loan Withdraw: $5,000

# %% [markdown]
# ### (f) What is the cash balance at the end of August?

# %% [markdown]
# End of August Cash Balance: $327,095

# %% [markdown]
# ### (g) Due to potential unexpected repairs, one of the managers has suggested increasing the minimum cash balance for June to $27,500. How much will now have to be repaid if this change is approved?

# %%
June_model = gb.Model("SunnyShore Bay June Increase")

C = June_model.addVars(4, lb=0, vtype=GRB.CONTINUOUS, name="Cash Balance")
B = June_model.addVars(6, lb=0, vtype=GRB.CONTINUOUS, name="Borrow")

June_model.setObjective(1.0175 * B[0] + 1.0225 * B[1] + 1.0275 * B[2] + 1.0175 * B[3] + 1.0225 * B[4] + 1.0175 * B[5], GRB.MINIMIZE)

June_model.addConstr(C[0] == 140000 + 180000 - 300000 + B[0] + B[1] + B[2], "May")
June_model.addConstr(C[1] == C[0] + 260000 - 400000 + B[3] + B[4] - 1.0175 * B[0], "June")
June_model.addConstr(C[2] == C[1] + 420000 - 350000 + B[5] - 1.0225 * B[1] - 1.0175 * B[3], "July")
June_model.addConstr(C[3] == C[2] + 580000 - 200000 - 1.0275 * B[2] - 1.0225 * B[4] - 1.0175 * B[5], "August")

June_model.addConstr(B[0] + B[1] + B[2] <= 250000, "Borrow_Limit_May")
June_model.addConstr(B[3] + B[4] <= 150000, "Borrow_Limit_June")
June_model.addConstr(B[5] <= 350000, "Borrow_Limit_July")

June_model.addConstr(C[0] >= 25000, "Min_Cash_Balance_May")
June_model.addConstr(C[1] >= 27500, "Min_Cash_Balance_June")
June_model.addConstr(C[2] >= 35000, "Min_Cash_Balance_July")
June_model.addConstr(C[3] >= 18000, "Min_Cash_Balance_August")

June_model.addConstr(C[2] >= 0.65 * (C[0] + C[1]), "July_Ratio_Constraint")

June_model.optimize()

# %%
print("Model Status: ", June_model.status)
print("Number of Decision Variables: ", June_model.numVars)

# %%
print("Total Amount of Money: ", round(June_model.objVal, 2)) 
print(June_model.printAttr('X'))

# %% [markdown]
# Initial Amount Repayed: $142,904.73
# 
# Amount Repayed with Increase in June minimum cash balance: $150,536.62

# %% [markdown]
# ### (h) Formulate and solve the dual linear program demonstrating that the model you create is, indeed, the correct dual problem of the primal formulation.

# %%
import gurobipy as gb

# Create the optimization model for the dual problem
dual_model = gb.Model("Sunnyshore Bay Dual")

# Create dual variables for each constraint in the primal model
May_Balance = dual_model.addVar(lb=0, vtype=gb.GRB.CONTINUOUS, name="May_Balance")
June_Balance = dual_model.addVar(lb=0, vtype=gb.GRB.CONTINUOUS, name="June_Balance")
July_Balance = dual_model.addVar(lb=0, vtype=gb.GRB.CONTINUOUS, name="July_Balance")
August_Balance = dual_model.addVar(lb=0, vtype=gb.GRB.CONTINUOUS, name="August_Balance")

Borrow_Limit_May = dual_model.addVar(lb=0, vtype=gb.GRB.CONTINUOUS, name="Borrow_Limit_May")
Borrow_Limit_June = dual_model.addVar(lb=0, vtype=gb.GRB.CONTINUOUS, name="Borrow_Limit_June")
Borrow_Limit_July = dual_model.addVar(lb=0, vtype=gb.GRB.CONTINUOUS, name="Borrow_Limit_July")

Min_Cash_Balance_May = dual_model.addVar(lb=0, vtype=gb.GRB.CONTINUOUS, name="Min_Cash_Balance_May")
Min_Cash_Balance_June = dual_model.addVar(lb=0, vtype=gb.GRB.CONTINUOUS, name="Min_Cash_Balance_June")
Min_Cash_Balance_July = dual_model.addVar(lb=0, vtype=gb.GRB.CONTINUOUS, name="Min_Cash_Balance_July")
Min_Cash_Balance_August = dual_model.addVar(lb=0, vtype=gb.GRB.CONTINUOUS, name="Min_Cash_Balance_August")

July_Ratio_Constraint = dual_model.addVar(lb=0, vtype=gb.GRB.CONTINUOUS, name="July_Ratio_Constraint")

# Set the objective function for the dual problem
dual_model.setObjective(180000 * May_Balance + 260000 * June_Balance + 420000 * July_Balance + 580000 * August_Balance
                        + 250000 * Borrow_Limit_May + 150000 * Borrow_Limit_June + 350000 * Borrow_Limit_July
                        - 25000 * Min_Cash_Balance_May - 20000 * Min_Cash_Balance_June
                        - 35000 * Min_Cash_Balance_July - 18000 * Min_Cash_Balance_August
                        - 0.65 * (140000 + 180000) * July_Ratio_Constraint, gb.GRB.MAXIMIZE)

# Add constraints corresponding to the primal problem
dual_model.addConstr(May_Balance + Borrow_Limit_May <= 1.0175 * May_Balance + 1.0225 * June_Balance + 1.0275 * July_Balance + 1.0175 * August_Balance, "May_Constraint")
dual_model.addConstr(June_Balance + Borrow_Limit_June <= June_Balance + 1.0225 * Borrow_Limit_May + 1.0275 * Borrow_Limit_June, "June_Constraint")
dual_model.addConstr(July_Balance + Borrow_Limit_July <= July_Balance + 1.0275 * Borrow_Limit_May + 1.0225 * Borrow_Limit_June + 1.0175 * Borrow_Limit_July, "July_Constraint")
dual_model.addConstr(August_Balance <= August_Balance + 1.0275 * Borrow_Limit_May + 1.0225 * Borrow_Limit_June + 1.0175 * Borrow_Limit_July, "August_Constraint")

# Add non-negativity constraints for dual variables
dual_model.addConstr(May_Balance >= 0, "Nonneg_May")
dual_model.addConstr(June_Balance >= 0, "Nonneg_June")
dual_model.addConstr(July_Balance >= 0, "Nonneg_July")
dual_model.addConstr(August_Balance >= 0, "Nonneg_August")
dual_model.addConstr(Borrow_Limit_May >= 0, "Nonneg_Borrow_Limit_May")
dual_model.addConstr(Borrow_Limit_June >= 0, "Nonneg_Borrow_Limit_June")
dual_model.addConstr(Borrow_Limit_July >= 0, "Nonneg_Borrow_Limit_July")
dual_model.addConstr(Min_Cash_Balance_May >= 0, "Nonneg_Min_Cash_Balance_May")
dual_model.addConstr(Min_Cash_Balance_June >= 0, "Nonneg_Min_Cash_Balance_June")
dual_model.addConstr(Min_Cash_Balance_July >= 0, "Nonneg_Min_Cash_Balance_July")
dual_model.addConstr(Min_Cash_Balance_August >= 0, "Nonneg_Min_Cash_Balance_August")
dual_model.addConstr(July_Ratio_Constraint >= 0, "Nonneg_July_Ratio_Constraint")

# Optimize the dual model
dual_model.optimize()

# %% [markdown]
# ### (i) Which formulation, the primal or the dual model, do you think is easier to solve?

# %% [markdown]
# In our case the dual model has more constraints with 13 than the primal model with 12. The more constraints a model has, the more computational power required to successfully run the model. For this reason it is easier to solve the primal problem than the dual problem in this scenario. 


