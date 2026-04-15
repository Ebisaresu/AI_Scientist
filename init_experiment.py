import os
import openai
import argparse
import json
import subprocess

def generate_template(experiment_name, prompt):
    base_dir = os.path.join("templates", experiment_name)
    
    if os.path.exists(base_dir):
        print(f"❌ エラー: '{experiment_name}' というテンプレートは既に存在します。")
        return

    os.makedirs(base_dir, exist_ok=True)
    print(f"📁 テンプレートフォルダを作成しました: {base_dir}")

    client = openai.OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")

    # 1. experiment.py の生成
    print("🤖 LLMにベースラインコード (experiment.py) を執筆させています...")
    system_prompt = """
    You are an expert in Operations Research.
    Based on the user's requirements, create a baseline Python script for mathematical optimization (using PuLP or similar libraries).

    [Mandatory Requirements]

    The script must accept a command-line argument --out_dir and save the results to the specified directory.

    Compile the execution results (e.g., objective function value, solve time) into a dictionary format and save it as final_info.json inside the out_dir.
    Format example: {"objective_value": {"means": 150.0}, "solve_time_seconds": {"means": 0.05}}

    Output ONLY the pure Python code enclosed in a Markdown code block (python ... ). Do NOT provide any explanations or conversational text.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        code = content.split("```python")[1].split("```")[0].strip() if "```python" in content else content.strip()
        
        with open(os.path.join(base_dir, "experiment.py"), "w", encoding="utf-8") as f:
            f.write(code)
        print("  ✅ experiment.py を生成しました。")
        
    except Exception as e:
        print(f"  ❌ experiment.py の生成に失敗しました: {e}")
        return

    # 3. seed_ideas.json の生成
    seed_ideas = [
        {
            "Name": "add_robust_constraints",
            "Title": "Introduce Robust Optimization Constraints",
            "Experiment": "Modify the formulation to account for worst-case scenarios by adding robust constraints.",
            "Condition": "Baseline runs successfully."
        }
    ]
    with open(os.path.join(base_dir, "seed_ideas.json"), "w", encoding="utf-8") as f:
        json.dump(seed_ideas, f, indent=4)
    print("  ✅ seed_ideas.json を生成しました。")
    
    # ★ ご指摘いただいたベースライン(run_0)の自動構築フェーズ ★
    print("\n🚀 生成したコードを用いてベースライン (run_0) を自動構築しています...")
    try:
        # サブプロセスで生成したての experiment.py を走らせる
        subprocess.run(
            ["python", "experiment.py", "--out_dir", "run_0"],
            cwd=base_dir, # 作業ディレクトリを生成したフォルダに指定
            check=True,
            capture_output=True,
            text=True
        )
        print("  ✅ Clean baseline (run_0) created successfully!")
        print(f"\n🎉 準備完了！以下のコマンドでAI-Scientistを起動できます:\n!python launch_scientist.py --experiment {experiment_name} --model gpt-4o-mini")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ ベースラインの作成に失敗しました。AIが生成したコードにバグがある可能性があります。")
        print(f"  エラー詳細:\n{e.stderr}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, required=True, help="作成する実験のフォルダ名")
    parser.add_argument("--prompt", type=str, required=True, help="最適化問題の要件定義プロンプト")
    args = parser.parse_args()
    generate_template(args.name, args.prompt)