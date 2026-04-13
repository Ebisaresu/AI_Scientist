import pulp
import time
import json
import argparse
import os

def run_experiment(out_dir):
    # Ensure output directory exists
    os.makedirs(out_dir, exist_ok=True)
    start_time = time.time()
    
    # Dummy data for Island Defense
    islands = ["Island_Alpha", "Island_Bravo", "Island_Charlie", "Island_Delta", "Island_Echo"]
    value = {"Island_Alpha": 100, "Island_Bravo": 80, "Island_Charlie": 50, "Island_Delta": 70, "Island_Echo": 90}
    threat_prob = {"Island_Alpha": 0.8, "Island_Bravo": 0.5, "Island_Charlie": 0.9, "Island_Delta": 0.3, "Island_Echo": 0.7}
    cost = {"Island_Alpha": 5, "Island_Bravo": 3, "Island_Charlie": 8, "Island_Delta": 4, "Island_Echo": 6}
    
    total_budget = 200
    defense_effectiveness = 1.5

    # Initialize the LP model
    prob = pulp.LpProblem("Island_Defense_Resource_Allocation", pulp.LpMinimize)
    
    # Decision Variables
    x = pulp.LpVariable.dicts("x", islands, lowBound=0, cat='Continuous')
    u = pulp.LpVariable.dicts("u", islands, lowBound=0, cat='Continuous')

    # Objective Function
    prob += pulp.lpSum([u[i] for i in islands]), "Total_Unmitigated_Risk"
    
    # Budget Constraint
    prob += pulp.lpSum([cost[i] * x[i] for i in islands]) <= total_budget, "Budget_Constraint"

    # Risk Calculation Constraints
    for i in islands:
        initial_threat = value[i] * threat_prob[i]
        prob += u[i] >= initial_threat - defense_effectiveness * x[i], f"Risk_Calc_{i}"

    # Solve the model with a 60-second time limit to prevent hangs
    prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=60))
    
    solve_time = time.time() - start_time
    final_risk = pulp.value(prob.objective)
    
    # Standard output for logging
    print(f"Status: {pulp.LpStatus[prob.status]}")
    print(f"Final Score: unmitigated_risk={final_risk}, solve_time_seconds={solve_time}")
    
    # Formatted output for AI-Scientist evaluation
    results = {
        "unmitigated_risk": {"means": final_risk},
        "solve_time_seconds": {"means": solve_time}
    }
    
    # Save to final_info.json
    with open(os.path.join(out_dir, "final_info.json"), "w") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", type=str, default="run_0", help="Output directory")
    args = parser.parse_args()
    run_experiment(args.out_dir)