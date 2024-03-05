
import gurobipy as gp
from gurobipy import Model, GRB
import pandas as pd
import numpy as np


path = r'C:\Users\anant\OneDrive\Desktop\MBAN\OMIS 6000\Assignment\2'
file = '\BasketballPlayers.csv'

file_path = path + file


df = pd.read_csv(file_path) 



m = gp.Model("BasketballTeamSelection")


# Add decision variables

players = df.index.tolist()
player_vars = m.addVars(players, vtype=GRB.BINARY, name="Player")


# Constraints

# Guard and Forward/Center allocation constraints
guards = df[df['Position'].isin(['G', 'G/F'])].index
forward_centers = df[df['Position'].isin(['F', 'C', 'F/C'])].index
m.addConstr(player_vars.sum(guards) >= 0.3 * 21, "MinGuards")
m.addConstr(player_vars.sum(forward_centers) >= 0.4 * 21, "MinForwardCenters")


# Skill average constraints

skills = ['Ball Handling', 'Shooting', 'Rebounding', 'Defense', 'Athletic Ability', 'Toughness', 'Mental Acuity']

for skill in skills:
    total_skill_points = gp.quicksum(player_vars[i] * df.at[i, skill] for i in players)
    m.addConstr(total_skill_points >= 2.05 * 21, f"Skill_{skill}_Adjusted")


# Exclusive invitation constraints

group1 = list(range(20, 25))
group2 = list(range(72, 79))
group3 = list(range(105, 115))
group4 = list(range(45, 50))
group5 = list(range(65, 70))
m.addConstr(gp.quicksum(player_vars[i] for i in group1) * gp.quicksum(player_vars[i] for i in group2) == 0, "Exclusive1")
m.addConstr(gp.quicksum(player_vars[i] for i in group3) <= (gp.quicksum(player_vars[i] for i in group4) + gp.quicksum(player_vars[i] for i in group5)), "DependentInvitations")


# At least one player from each range constraint

for start in range(1, 141, 10):
    end = start + 9
    m.addConstr(gp.quicksum(player_vars[i] for i in range(start, end+1)) >= 1, f"AtLeastOne_{start}-{end}")


m.addConstr(player_vars.sum() == 21, "Exactly21Invitations")


m.setObjective(gp.quicksum(player_vars[i] * df.loc[i, skills].sum() for i in players), GRB.MAXIMIZE)


# Optimize the model

m.optimize()


# Extract the solution

selected_players = [i for i in players if player_vars[i].X > 0.5]
print("Selected Players:", selected_players)


len(selected_players)


optimal_value = m.objVal

print(f"Optimal Objective Function Value: {optimal_value}")


num_guards_invited = sum(player_vars[i].X for i in guards)
print(f"Number of Guards Invited: {num_guards_invited}")


def adjust_and_solve_model(min_invitations):
    
    m = gp.Model("BasketballTeamSelection")
    
    # Define variables
    players = df.index.tolist()
    player_vars = m.addVars(players, vtype=GRB.BINARY, name="Player")
    
    # Guards and Forward/Center allocation constraints based on current 'min_invitations'
    guards = df[df['Position'].isin(['G', 'G/F'])].index
    forward_centers = df[df['Position'].isin(['F', 'C', 'F/C'])].index
    m.addConstr(player_vars.sum(guards) >= 0.3 * min_invitations, "MinGuards")
    m.addConstr(player_vars.sum(forward_centers) >= 0.4 * min_invitations, "MinForwardCenters")
    
    # Skill average constraints adjusted for 'min_invitations'
    for skill in skills:
        total_skill_points = gp.quicksum(player_vars[i] * df.at[i, skill] for i in players)
        m.addConstr(total_skill_points >= 2.05 * min_invitations, f"Skill_{skill}_Adjusted")
    
    # Exclusive invitation and dependent invitations constraints
    m.addConstr(gp.quicksum(player_vars[i] for i in group1) * gp.quicksum(player_vars[i] for i in group2) == 0, "Exclusive1")
    m.addConstr(gp.quicksum(player_vars[i] for i in group3) <= (gp.quicksum(player_vars[i] for i in group4) + gp.quicksum(player_vars[i] for i in group5)), "DependentInvitations")

    m.addConstr(player_vars.sum() == 21, "Exactly21Invitations")

    # At least one player from each range constraint
    for start in range(1, 141, 10):
        end = start + 9
        m.addConstr(gp.quicksum(player_vars[i] for i in range(start, end+1)) >= 1, f"AtLeastOne_{start}-{end}")
    
    # Set objective
    m.setObjective(gp.quicksum(player_vars[i] * df.loc[i, skills].sum() for i in players), GRB.MAXIMIZE)
    
    # Solve the model
    m.optimize()
    
    return m


min_invitations = 21


while min_invitations > 0:
    model = adjust_and_solve_model(min_invitations)
    if model.status == GRB.INFEASIBLE:
        print(f"Model becomes infeasible with {min_invitations} invitations.")
        model.computeIIS()  
        for c in model.getConstrs():
            if c.IISConstr:
                print(f"Infeasible constraint: {c.constrName}")
    else:
        min_invitations -= 1


