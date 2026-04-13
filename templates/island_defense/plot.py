import matplotlib.pyplot as plt
import json
import os
import glob

# AI dummy
labels = {
    "run_0": "Baseline"
}

def plot_results():
    run_dirs = sorted(glob.glob("run_*"))
    if not run_dirs:
        print("No run directories found.")
        return

    runs_names = []
    risks = []
    times = []

    for run_dir in run_dirs:
        info_path = os.path.join(run_dir, "final_info.json")
        if os.path.exists(info_path):
            with open(info_path, "r") as f:
                data = json.load(f)
                
                display_name = labels.get(run_dir, run_dir)
                
                if len(display_name) > 15:
                    display_name = display_name.replace(" ", "\\n")
                    
                runs_names.append(display_name)
                
                risk_val = data.get("unmitigated_risk", {}).get("means", 0)
                time_val = data.get("solve_time_seconds", {}).get("means", 0)
                risks.append(risk_val)
                times.append(time_val)

    if not runs_names:
        return

    plt.figure(figsize=(12, 6))
    plt.bar(runs_names, risks, color='b')
    plt.xlabel('Experiment Run')
    plt.ylabel('Unmitigated Risk')
    plt.title('Unmitigated Risk by Run')
    plt.xticks(rotation=45, ha='right') # ラベルを斜めにして見やすく
    plt.tight_layout() # はみ出し防止
    plt.savefig('risk_plot.png')

    # 計算時間のグラフ化
    plt.figure(figsize=(12, 6))
    plt.bar(runs_names, times, color='r')
    plt.xlabel('Experiment Run')
    plt.ylabel('Solve Time (seconds)')
    plt.title('Solve Time by Run')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('time_plot.png')
    print("✅ Plots generated successfully!")

if __name__ == "__main__":
    plot_results()