%%writefile /content/AI-Scientist/generate_light_report.py
import os
import glob
import json
import openai

def generate_report():
    # 1. 最新の実験フォルダを取得
    result_dirs = glob.glob("results/nanoGPT/202*") # 年号が変わっても動くように微修正
    if not result_dirs:
        print("エラー: 実験フォルダが見つかりません。")
        return
    latest_dir = max(result_dirs, key=os.path.getmtime)
    print(f"対象フォルダ: {latest_dir}")

    # 2. アイデア情報の読み込み
    try:
        with open(os.path.join(latest_dir, "idea.json"), "r") as f:
            idea_data = json.load(f)
    except Exception as e:
        print(f"idea.json の読み込みに失敗しました: {e}")
        return

    # 3. 全ての実験ログ (run_0, run_1, run_2...) をかき集める
    experiment_logs = ""
    # run_ フォルダを番号順にソートして取得
    run_dirs = sorted(glob.glob(os.path.join(latest_dir, "run_*")))
    
    if run_dirs:
        for run_dir in run_dirs:
            notes_path = os.path.join(run_dir, "notes.txt")
            if os.path.exists(notes_path):
                with open(notes_path, "r") as f:
                    experiment_logs += f"\n\n--- 【{os.path.basename(run_dir)} の試行ログ】 ---\n"
                    experiment_logs += f.read()
    
    if not experiment_logs.strip():
         experiment_logs = "詳細なログファイル(notes.txt)が見つかりませんでしたが、実験は実行されました。"

    # 4. Qwen2.5-Coderへのプロンプト作成
    prompt = f"""
    あなたは優秀なデータサイエンティストであり、オペレーションズ・リサーチの専門家です。
    以下の実験アイデアと実行ログを元に、日本語で簡潔な実験レポートをMarkdown形式で作成してください。
    
    # 構成案
    1. 実験の目的とアイデア（何を解決しようとしたか）
    2. 実施したアプローチ（AIがどのような試行錯誤やコード修正を行ったか）
    3. 結果と考察（数値はどう変化したか、最終的な結論）

    # 実験データ
    【タイトル】: {idea_data.get('Title')}
    【アイデア詳細】: {idea_data.get('Experiment')}
    【実験ログ・結果】:
    {experiment_logs}
    """

    # 5. Ollama経由でQwenにリクエスト
    print("Qwen2.5-Coder にレポート執筆を依頼しています...")
    client = openai.OpenAI(
        api_key="ollama",
        base_url="http://localhost:11434/v1"
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.3
        )

        report_text = response.choices[0].message.content
        report_path = os.path.join(latest_dir, "light_report.md")
        
        with open(report_path, "w") as f:
            f.write(report_text)
        
        print(f"🎉 レポート出力完了: {report_path}")
        print("\n--- レポートのプレビュー ---\n")
        print(report_text[:600] + "...\n\n(続きは左のファイルブラウザからダウンロードして確認してください)")
        
    except Exception as e:
        print(f"レポートの生成中にエラーが発生しました: {e}")

if __name__ == "__main__":
    generate_report()