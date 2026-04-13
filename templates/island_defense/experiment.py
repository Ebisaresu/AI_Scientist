import pulp
import time
import json

def run_experiment():
    start_time = time.time()

    # 1. Define dummy data for Island Defense
    islands = ["Island_Alpha", "Island_Bravo", "Island_Charlie", "Island_Delta", "Island_Echo"]
    
    # Strategic value of each island (e.g., population, infrastructure)
    value = {"Island_Alpha": 100, "Island_Bravo": 80, "Island_Charlie": 50, "Island_Delta": 70, "Island_Echo": 90}
    
    # Threat probability / Enemy attack likelihood (0.0 to 1.0)
    threat_prob = {"Island_Alpha": 0.8, "Island_Bravo": 0.5, "Island_Charlie": 0.9, "Island_Delta": 0.3, "Island_Echo": 0.7}
    
    # Deployment cost per unit of defense resource (varies by distance from mainland)
    cost = {"Island_Alpha": 5, "Island_Bravo": 3, "Island_Charlie": 8, "Island_Delta": 4, "Island_Echo": 6}
    
    total_budget = 200
    defense_effectiveness = 1.5  # Threat reduced per 1 unit of resource

    # 2. Initialize the optimization model (Minimize Unmitigated Risk)
    prob = pulp.LpProblem("Island_Defense_Resource_Allocation", pulp.LpMinimize)

    # 3. Decision Variables
    # x[i]: units of defense resource allocated to island i (Continuous for baseline)
    x = pulp.LpVariable.dicts("x", islands, lowBound=0, cat='Continuous')

    # Dummy variables for unmitigated risk per island (must be >= 0)
    u = pulp.LpVariable.dicts("u", islands, lowBound=0, cat='Continuous')

    # 4. Objective Function: Minimize total unmitigated risk across all islands
    prob += pulp.lpSum([u[i] for i in islands]), "Total_Unmitigated_Risk"

    # 5. Constraints
    # Budget constraint: Total cost cannot exceed budget
    prob += pulp.lpSum([cost[i] * x[i] for i in islands]) <= total_budget, "Budget_Constraint"

    # Risk calculation constraints
    # Unmitigated risk = (Value * Threat) - (Effectiveness * Resources)
    for i in islands:
        initial_threat = value[i] * threat_prob[i]
        prob += u[i] >= initial_threat - defense_effectiveness * x[i], f"Risk_Calc_{i}"

    # 6. Solve the model (Using standard CBC solver, Gurobi is disabled)
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    solve_time = time.time() - start_time

    # 7. Output metrics for AI-Scientist to evaluate
    final_risk = pulp.value(prob.objective)
    
    results = {
        "unmitigated_risk": final_risk,
        "solve_time_seconds": solve_time,
        "status": pulp.LpStatus[prob.status]
    }
    
    # AI-Scientist reads standard output to evaluate the model
    print(f"Final Score: {json.dumps(results)}")

if __name__ == "__main__":
    run_experiment()