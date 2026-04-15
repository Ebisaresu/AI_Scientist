import os
import glob
import json
import openai
import argparse

def generate_report(experiment_name, overwrite):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_base_dir = os.path.join(script_dir, "results", experiment_name)
    
    print(f"🔍 Searching in: {target_base_dir}")
    if not os.path.exists(target_base_dir):
        print(f"\n❌ Error: '{experiment_name}' does not exist.")
        return

    result_dirs = glob.glob(os.path.join(target_base_dir, "202*"))
    valid_dirs = [d for d in result_dirs if os.path.exists(os.path.join(d, "ideas.json"))]
            
    if not valid_dirs:
        print("\n❌ Error: No valid experiment directories found.")
        return
        
    client = openai.OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")

    for target_dir in sorted(valid_dirs):
        dir_name = os.path.basename(target_dir)
        report_path = os.path.join(target_dir, "light_report.md")

        if not overwrite and os.path.exists(report_path):
            print(f"⏩ Skipped: {dir_name}")
            continue

        print(f"🎯 Generating report for: {dir_name}")

        # 1. Load Idea
        idea_data = {}
        with open(os.path.join(target_dir, "ideas.json"), "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            if isinstance(raw_data, list):
                for item in raw_data:
                    if isinstance(item, dict) and item.get("Name") in target_dir:
                        idea_data = item
                        break
                if not idea_data: idea_data = raw_data[0]
            else: idea_data = raw_data

        # 2. Gather Logs and Code
        experiment_logs = ""
        main_notes_path = os.path.join(target_dir, "notes.txt")
        if os.path.exists(main_notes_path):
            with open(main_notes_path, "r", encoding="utf-8") as f:
                experiment_logs += "--- [Experiment Notes] ---\n" + f.read() + "\n\n"

        current_code = ""
        exp_py_path = os.path.join(target_dir, "experiment.py")
        if os.path.exists(exp_py_path):
            with open(exp_py_path, "r", encoding="utf-8") as f:
                current_code = f.read()

        run_dirs = sorted(glob.glob(os.path.join(target_dir, "run_*")))
        if run_dirs:
            experiment_logs += "--- [Final Scores of Each Run] ---\n"
            for run_dir in run_dirs:
                info_path = os.path.join(run_dir, "final_info.json")
                if os.path.exists(info_path):
                    with open(info_path, "r", encoding="utf-8") as f:
                        experiment_logs += f"[{os.path.basename(run_dir)}]: {f.read()}\n"

        if "--- [Final Scores" not in experiment_logs:
             experiment_logs = "[SYSTEM WARNING] No detailed execution logs (notes.txt or final_info.json) were found. The experiment most likely crashed due to syntax errors. DO NOT hallucinate success; state honestly that the experiment failed."

        # 3. English Prompt for Maximum Accuracy
        prompt = f"""
        You are an expert Operations Research scientist and data analyst.
        Based on the provided Python code and experiment logs, write a formal "Technical Report" in Markdown format.

        # STRICT RULES
        1. You MUST include the following two exact image links in the "3. Experimental Results" section:
           - `![Unmitigated Risk](risk_plot.png)`
           - `![Solve Time](time_plot.png)`
        2. Quote specific metrics from the "Final Scores of Each Run" to compare the baseline (Run 0) with subsequent runs.
        3. If the logs contain a SYSTEM WARNING about missing files, state honestly that the experiment failed or crashed. Do not hallucinate success.

        # REPORT STRUCTURE
        1. Introduction: Background and objective of the experiment.
        2. Mathematical Formulation: Extract and format the math from the Python code.
           - Sets and Indices
           - Parameters
           - Decision Variables
           - Objective Function & Constraints (Use LaTeX formatting like `$x_i$` and `$$\min Z$$`, and explain the mathematical meaning of each equation).
        3. Experimental Results: 
           - Embed the image links here.
           - Analyze the numerical changes.
        4. Conclusion & Future Work

        # EXPERIMENT DATA
        [Title]: {idea_data.get('Title')}
        
        [Code (experiment.py)]:
        {current_code}
        
        [Logs & Results]:
        {experiment_logs}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.2
            )
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(response.choices[0].message.content)
            print(f"  🎉 Output complete: {report_path}")
        except Exception as e:
            print(f"  [Error]: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", type=str, default="island_defense")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    generate_report(args.experiment, args.overwrite)