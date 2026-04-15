import matplotlib.pyplot as plt
import json
import os
import glob

def plot_results():
    run_dirs = sorted(glob.glob("run_*"))
    if not run_dirs: return
    runs_names, objs, times = [], [], []

    for run_dir in run_dirs:
        info_path = os.path.join(run_dir, "final_info.json")
        if os.path.exists(info_path):
            with open(info_path, "r") as f:
                data = json.load(f)
                runs_names.append(run_dir)
                obj_key = list(data.keys())[0] if data else None
                obj_val = data.get(obj_key, {}).get("means", 0) if obj_key else 0
                time_val = data.get("solve_time_seconds", {}).get("means", 0)
                objs.append(obj_val)
                times.append(time_val)

    if not runs_names: return

    plt.figure(figsize=(10, 5))
    plt.bar(runs_names, objs, color='b')
    plt.xticks(rotation=45, ha='right')
    plt.title('Objective Value by Run')
    plt.tight_layout()
    plt.savefig('risk_plot.png')

    plt.figure(figsize=(10, 5))
    plt.bar(runs_names, times, color='r')
    plt.xticks(rotation=45, ha='right')
    plt.title('Solve Time by Run')
    plt.tight_layout()
    plt.savefig('time_plot.png')

if __name__ == "__main__":
    plot_results()