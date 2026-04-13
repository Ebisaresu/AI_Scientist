import matplotlib.pyplot as plt
import json
import os
import glob

def plot_results():
    # 存在する run_ フォルダを自動で全て探す
    run_dirs = sorted(glob.glob("run_*"))
    if not run_dirs:
        print("No run directories found.")
        return

    runs = []
    risks = []
    times = []

    for run_dir in run_dirs:
        info_path = os.path.join(run_dir, "final_info.json")
        if os.path.exists(info_path):
            with open(info_path, "r") as f:
                data = json.load(f)
                runs.append(run_dir)
                # 入れ子構造から安全に値を取得
                risk_val = data.get("unmitigated_risk", {}).get("means", 0)
                time_val = data.get("solve_time_seconds", {}).get("means", 0)
                risks.append(risk_val)
                times.append(time_val)

    if not runs:
        return

    # リスクのグラフ化
    plt.figure(figsize=(10, 5))
    plt.bar(runs, risks, color='b')
    plt.xlabel('Run')
    plt.ylabel('Unmitigated Risk')
    plt.title('Unmitigated Risk by Run')
    plt.savefig('risk_plot.png')

    # 計算時間のグラフ化
    plt.figure(figsize=(10, 5))
    plt.bar(runs, times, color='r')
    plt.xlabel('Run')
    plt.ylabel('Solve Time (seconds)')
    plt.title('Solve Time by Run')
    plt.savefig('time_plot.png')
    print("✅ Plots generated successfully!")

if __name__ == "__main__":
    plot_results()