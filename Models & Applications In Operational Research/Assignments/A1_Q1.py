# Importing packages

import pandas as pd
import gurobipy as gb


# Capacity datasets

df_capacity_direct_prod = pd.read_csv(r'C:\Users\anant\OneDrive\Desktop\MBAN\OMIS 6000\Assignment\1\Capacity_for_Direct_Production_Facilities.csv')
df_capacity_dist_centers = pd.read_csv(r'C:\Users\anant\OneDrive\Desktop\MBAN\OMIS 6000\Assignment\1\Capacity_for_Transship_Distribution_Centers.csv')
df_capacity_trans_prod = pd.read_csv(r'C:\Users\anant\OneDrive\Desktop\MBAN\OMIS 6000\Assignment\1\Capacity_for_Transship_Production_Facilities.csv')


# Costs datasets

df_cost_prod_to_refinement = pd.read_csv(r'C:\Users\anant\OneDrive\Desktop\MBAN\OMIS 6000\Assignment\1\Cost_Production_to_Refinement.csv')
df_cost_prod_to_transshipment = pd.read_csv(r'C:\Users\anant\OneDrive\Desktop\MBAN\OMIS 6000\Assignment\1\Cost_Production_to_Transshipment.csv')
df_cost_transship_to_refinement = pd.read_csv(r'C:\Users\anant\OneDrive\Desktop\MBAN\OMIS 6000\Assignment\1\Cost_Transshipment_to_Refinement.csv')


# Demand dataset

df_refinement_demand = pd.read_csv(r'C:\Users\anant\OneDrive\Desktop\MBAN\OMIS 6000\Assignment\1\Refinement_Demand.csv')


model = gb.Model("Can2Oil")


# x[i, k]: Amount of oil shipped from direct production facility (i) to refinement center (k)

x_direct = model.addVars(df_capacity_direct_prod['ProductionFacility'], 
                         df_refinement_demand['RefinementCenter'], 
                         name="Direct Facility to Refine", 
                         lb=0)


# y[i, j]: Amount of oil shipped from transshipment-required facility (i) to transshipment hub (j)

y_transship = model.addVars(df_capacity_trans_prod['ProductionFacility'], 
                            df_capacity_distr_centers['TransshipmentHub'], 
                            name="Transship Facility to Hub", 
                            lb=0)


# z[j, k]: Amount of oil shipped from transshipment hub (j) to refinement center (k)

z_hub_to_refine = model.addVars(df_capacity_distr_centers['TransshipmentHub'], 
                                df_refinement_demand['RefinementCenter'], 
                                name="Ship Hub to Refine", 
                                lb=0)



# Objective functions

prod_to_refine_objective = gb.quicksum(df_cost_prod_to_refinement.set_index(['ProductionFacility', 'RefinementCenter']).loc[(i, k), 'Cost'] * x_direct[i, k] 
    for i in df_capacity_direct_prod['ProductionFacility'] 
        for k in df_refinement_demand['RefinementCenter'])


prod_to_hub_objective = gb.quicksum(df_cost_prod_to_transshipment.set_index(['ProductionFacility', 'TransshipmentHub']).loc[(i, j), 'Cost'] * y_transship[i, j] 
    for i in df_capacity_trans_prod['ProductionFacility'] 
        for j in df_capacity_dist_centers['TransshipmentHub'])


hub_to_refine_objective = gb.quicksum(df_cost_transship_to_refinement.set_index(['TransshipmentHub', 'RefinementCenter']).loc[(j, k), 'Cost'] * z_hub_to_refine[j, k] 
    for j in df_capacity_dist_centers['TransshipmentHub'] 
        for k in df_refinement_demand['RefinementCenter'])


model.setObjective(prod_to_refine_objective + prod_to_hub_objective + hub_to_refine_objective, gb.GRB.MINIMIZE)


# Supply constraints for direct production facilities

for i in df_capacity_direct_prod['ProductionFacility']:
    model.addConstr(x_direct.sum(i, '*') <= df_capacity_direct_prod.loc[df_capacity_direct_prod['ProductionFacility'] == i, 'Capacity'].iloc[0])


# Supply constraints for transshipment facilities

for i in df_capacity_trans_prod['ProductionFacility']:
    model.addConstr(y_transship.sum(i, '*') <= df_capacity_trans_prod.loc[df_capacity_trans_prod['ProductionFacility'] == i, 'Capacity'].iloc[0])


# Demand constraints for each refinement center

for k in df_refinement_demand['RefinementCenter']:
    model.addConstr(x_direct.sum('*', k) + z_hub_to_refine.sum('*', k) == df_refinement_demand.loc[df_refinement_demand['RefinementCenter'] == k, 'Demand'].iloc[0])


# Transshipment constraints for each hub

for j in df_capacity_dist_centers['TransshipmentHub']:
    model.addConstr(y_transship.sum('*', j) == z_hub_to_refine.sum(j, '*'))


# Solve the model

model.optimize()


# Number of variables in the model

print("Number of Decision Variables: ", model.numVars)


print("Total Transportation cost: ", prod_to_refine_objective.getValue() + prod_to_hub_objective.getValue() + hub_to_refine_objective.getValue())


print("Optimal total transportation cost:", model.objVal)


# Print the decision variables

print(model.printAttr('X'))

# 2. In the optimal solution, what proportion of canola oil is transshipped?


total_transshipped = sum(y_transship[i, j].X for i in df_capacity_trans_prod['ProductionFacility'] for j in df_capacity_dist_centers['TransshipmentHub'])
total_transshipped


total_shipped = sum(x_direct[i, k].X for i in df_capacity_direct_prod['ProductionFacility'] for k in df_refinement_demand['RefinementCenter']) + total_transshipped
total_shipped


round((total_transshipped / total_shipped) * 100, 2)

# 3. The model does not currently limit that amount of canola oil that is transshipped. How would you modify the objective function to account for this? Formulate and solve this model.


# We'll assign a penalty cost per unit of oil transshipped. We'll define a parameter C_penalty to account for this
# The reason we've picked 3.4 is because the average cost is ~ 1.7 per unit of oil transshiped, and a penalty of 2x seems like a good place to start 

C_penalty = 3.4


model_objective = gb.Model("Can2Oil with modified Obj Function")


# x[i, k]: Amount of oil shipped from direct production facility (i) to refinement center (k)

x_direct = model_objective.addVars(df_capacity_direct_prod['ProductionFacility'], 
                         df_refinement_demand['RefinementCenter'], 
                         name="Direct Facility to Refine", 
                         lb=0)


# y[i, j]: Amount of oil shipped from transshipment-required facility (i) to transshipment hub (j)

y_transship = model_objective.addVars(df_capacity_trans_prod['ProductionFacility'], 
                            df_capacity_distr_centers['TransshipmentHub'], 
                            name="Transship Facility to Hub", 
                            lb=0)


# z[j, k]: Amount of oil shipped from transshipment hub (j) to refinement center (k)

z_hub_to_refine = model_objective.addVars(df_capacity_distr_centers['TransshipmentHub'], 
                                df_refinement_demand['RefinementCenter'], 
                                name="Ship Hub to Refine", 
                                lb=0)


# Objective functions

prod_to_refine_objective = gb.quicksum(df_cost_prod_to_refinement.set_index(['ProductionFacility', 'RefinementCenter']).loc[(i, k), 'Cost'] * x_direct[i, k] 
    for i in df_capacity_direct_prod['ProductionFacility'] 
        for k in df_refinement_demand['RefinementCenter'])


# Modifying the prod_to_hub_objective 

prod_to_hub_objective_with_penalty = gb.quicksum(
    (df_cost_prod_to_transshipment.set_index(['ProductionFacility', 'TransshipmentHub']).loc[(i, j), 'Cost'] + C_penalty) * y_transship[i, j]
    for i in df_capacity_trans_prod['ProductionFacility'] 
    for j in df_capacity_dist_centers['TransshipmentHub'])


hub_to_refine_objective = gb.quicksum(df_cost_transship_to_refinement.set_index(['TransshipmentHub', 'RefinementCenter']).loc[(j, k), 'Cost'] * z_hub_to_refine[j, k] 
    for j in df_capacity_dist_centers['TransshipmentHub'] 
        for k in df_refinement_demand['RefinementCenter'])


model_objective.setObjective(prod_to_refine_objective + prod_to_hub_objective_with_penalty + hub_to_refine_objective , gb.GRB.MINIMIZE)


# Supply constraints for direct production facilities

for i in df_capacity_direct_prod['ProductionFacility']:
    model_objective.addConstr(x_direct.sum(i, '*') <= df_capacity_direct_prod.loc[df_capacity_direct_prod['ProductionFacility'] == i, 'Capacity'].iloc[0])


# Supply constraints for transshipment facilities

for i in df_capacity_trans_prod['ProductionFacility']:
    model_objective.addConstr(y_transship.sum(i, '*') <= df_capacity_trans_prod.loc[df_capacity_trans_prod['ProductionFacility'] == i, 'Capacity'].iloc[0])



# Demand constraints for each refinement center

for k in df_refinement_demand['RefinementCenter']:
    model_objective.addConstr(x_direct.sum('*', k) + z_hub_to_refine.sum('*', k) == df_refinement_demand.loc[df_refinement_demand['RefinementCenter'] == k, 'Demand'].iloc[0])


# Transshipment constraints for each hub

for j in df_capacity_dist_centers['TransshipmentHub']:
    model_objective.addConstr(y_transship.sum('*', j) == z_hub_to_refine.sum(j, '*'))


model_objective.optimize()


print("Optimal total transportation cost with transshipment limit (objective function): ", model_objective.objVal)

# 4. Instead of modifying the objective function, how would you modify the constraint set to reduce the proportion of canola oil that is transshipped? Formulate and solve this model.


# Defining a new constraint. For this let's assume that the proportion cannot exceed 40%. We'll define a parameter P to account for this

P = 0.4


total_transshipped = gb.quicksum(y_transship[i, j] for i in df_capacity_trans_prod['ProductionFacility'] for j in df_capacity_dist_centers['TransshipmentHub'])


total_shipped = gb.quicksum(x_direct[i, k] for i in df_capacity_direct_prod['ProductionFacility'] for k in df_refinement_demand['RefinementCenter']) + total_transshipped


model.addConstr(total_transshipped <= P * total_shipped, "Transshipment Limit - Canola Oil")


model.setObjective(prod_to_refine_objective + prod_to_hub_objective + hub_to_refine_objective , gb.GRB.MINIMIZE)


model.optimize()


print("Optimal total transportation cost with transshipment limit (added constraint): ", model.objVal)


total_transshipped = sum(y_transship[i, j].X for i in df_capacity_trans_prod['ProductionFacility']
                             for j in df_capacity_dist_centers['TransshipmentHub'])
total_transshipped


sourcing_direct = sum(x_direct[i, k].X for i in df_capacity_direct_prod['ProductionFacility']
                          for k in range(1, 6))
sourcing_direct


# 5. Which of the two modeling approaches would you recommend the company take to determine a transportation plan that reduces the amount of canola oil that is transshipped?

# A. The cost with transshipment limit is lower than the cost associated with a penalty to the objective function. 
# However, it is possible that the current penalty that has been assigned to the objective function might be a little too high. 
# If we were to reduce this and perform some sensitivity analysis with different penalties, it is possible that it could change. 



# 6. Re-shoring is the practice of transferring overseas business operations closer to the home country. Given its prevalence in today’s economy, how would you alter the original model to favor producers closer to North America? Formulate and solve this model.

# Even though these production facilities haven't been indexed with the names of the countries, let's assume that facilities indexed 1 to 15 are from Canada, the US and Mexico


# We'll assign a parameter to reduce the transportation costs in the objective function from these facilities. Let's assume this to be 10%

reduction_percentage = 0.1 


closer_producers = list(range(1, 16))


model_reshoring = gb.Model("Can2Oil With ReShoring")


# x[i, k]: Amount of oil shipped from direct production facility (i) to refinement center (k)

x_direct = model_reshoring.addVars(df_capacity_direct_prod['ProductionFacility'], 
                         df_refinement_demand['RefinementCenter'], 
                         name="Direct Facility to Refine", 
                         lb=0)


# y[i, j]: Amount of oil shipped from transshipment-required facility (i) to transshipment hub (j)

y_transship = model_reshoring.addVars(df_capacity_trans_prod['ProductionFacility'], 
                            df_capacity_distr_centers['TransshipmentHub'], 
                            name="Transship Facility to Hub", 
                            lb=0)


# z[j, k]: Amount of oil shipped from transshipment hub (j) to refinement center (k)

z_hub_to_refine = model_reshoring.addVars(df_capacity_distr_centers['TransshipmentHub'], 
                                df_refinement_demand['RefinementCenter'], 
                                name="Ship Hub to Refine", 
                                lb=0)


prod_to_refine_objective_with_incentive = gb.quicksum(df_cost_prod_to_refinement.set_index(['ProductionFacility', 'RefinementCenter']).loc[(i, k), 'Cost'] * 
                (1 - reduction_percentage if i in closer_producers else 1) * x_direct[i, k] 
                for i in df_capacity_direct_prod['ProductionFacility'] 
                for k in df_refinement_demand['RefinementCenter'])


prod_to_hub_objective = gb.quicksum(df_cost_prod_to_transshipment.set_index(['ProductionFacility', 'TransshipmentHub']).loc[(i, j), 'Cost'] * y_transship[i, j] 
    for i in df_capacity_trans_prod['ProductionFacility'] 
        for j in df_capacity_dist_centers['TransshipmentHub'])


hub_to_refine_objective = gb.quicksum(df_cost_transship_to_refinement.set_index(['TransshipmentHub', 'RefinementCenter']).loc[(j, k), 'Cost'] * z_hub_to_refine[j, k] 
    for j in df_capacity_dist_centers['TransshipmentHub'] 
        for k in df_refinement_demand['RefinementCenter'])


model_reshoring.setObjective(prod_to_refine_objective_with_incentive + prod_to_hub_objective + hub_to_refine_objective, gb.GRB.MINIMIZE)


# Supply constraints for direct production facilities

for i in df_capacity_direct_prod['ProductionFacility']:
    model_reshoring.addConstr(x_direct.sum(i, '*') <= df_capacity_direct_prod[df_capacity_direct_prod['ProductionFacility'] == i]['Capacity'].iloc[0])


# Supply constraints for transshipment facilities

for i in df_capacity_trans_prod['ProductionFacility']:
    model_reshoring.addConstr(y_transship.sum(i, '*') <= df_capacity_trans_prod[df_capacity_trans_prod['ProductionFacility'] == i]['Capacity'].iloc[0])


# Demand constraints for each refinement center

for k in df_refinement_demand['RefinementCenter']:
    model_reshoring.addConstr(x_direct.sum('*', k) + z_hub_to_refine.sum('*', k) == df_refinement_demand[df_refinement_demand['RefinementCenter'] == k]['Demand'].iloc[0])



# Transshipment constraints for each hub

for j in df_capacity_dist_centers['TransshipmentHub']:
    model_reshoring.addConstr(y_transship.sum('*', j) == z_hub_to_refine.sum(j, '*'))


# Solve the model

model_reshoring.optimize()


print("Optimal total transportation cost with reshoring: ", model_reshoring.objVal)


total_transshipped = sum(y_transship[i, j].X for i in df_capacity_trans_prod['ProductionFacility']
                             for j in df_capacity_dist_centers['TransshipmentHub'])
total_transshipped


sourcing_direct = sum(x_direct[i, k].X for i in df_capacity_direct_prod['ProductionFacility']
                          for k in range(1, 6))
sourcing_direct

# 7. Do you expect the optimal solution to the re-shoring model to be similar to the optimal solution of the model that attempts to reduce transshipment? Why or why not? 

# A. We'll compare the reshoring solution to the solution with the added constraints instead of the one where we add a penalty to the objective function, since the costs associated are lower

# Reshoring Model - 
# 
# - Total transportation cost: 22682.24
# - Total Transshipped: 3505
# - Direct Facilities: 5223

# Optimal Transshipment Model - 
# 
# - Total transportation cost: 23577.11
# - Total Transshipped: 3491.2
# - Direct Facilities: 5236.8


