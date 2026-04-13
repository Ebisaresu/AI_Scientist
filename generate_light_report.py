import os
import glob
import json
import openai

def generate_report():
    # 1. スクリプトの場所を基準に絶対パスを構築
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_base_dir = os.path.join(script_dir, "results", "nanoGPT")
    
    print(f"🔍 検索ベースディレクトリ: {target_base_dir}")
    
    result_dirs = glob.glob(os.path.join(target_base_dir, "202*"))
    
    # ideas.json があるフォルダだけを抽出
    valid_dirs = []
    for d in result_dirs:
        # ideas.json に修正
        idea_path = os.path.join(d, "ideas.json") 
        if os.path.exists(idea_path):
            valid_dirs.append(d)
            
    if not valid_dirs:
        print("\n❌ エラー: ideas.json を含む有効な実験フォルダが見つかりませんでした。")
        return
        
    #latest_dir = max(valid_dirs, key=os.path.getmtime)
    latest_dir = max(valid_dirs)
    print(f"\n🎯 最終ターゲット決定: {os.path.basename(latest_dir)}\n")

    # 2. アイデア情報の読み込み（リスト対応版）
    idea_data = {}
    try:
        with open(os.path.join(latest_dir, "ideas.json"), "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            
        # JSONがリストの場合
        if isinstance(raw_data, list):
            # フォルダ名と一致する 'Name' を持つアイデアを探す
            for item in raw_data:
                if isinstance(item, dict) and item.get("Name") in latest_dir:
                    idea_data = item
                    break
            # もし一致するものがなければ、安全策としてリストの最初の要素を取得
            if not idea_data and len(raw_data) > 0:
                idea_data = raw_data[0]
        # JSONが単一の辞書の場合（念のため対応）
        elif isinstance(raw_data, dict):
            idea_data = raw_data
            
    except Exception as e:
        print(f"ideas.json の読み込みに失敗しました: {e}")
        return

    # 3. 全ての実験ログ (run_0, run_1...) をかき集める
    experiment_logs = ""
    run_dirs = sorted(glob.glob(os.path.join(latest_dir, "run_*")))
    
    if run_dirs:
        for run_dir in run_dirs:
            notes_path = os.path.join(run_dir, "notes.txt")
            if os.path.exists(notes_path):
                with open(notes_path, "r", encoding="utf-8") as f:
                    experiment_logs += f"\n\n--- 【{os.path.basename(run_dir)} の試行ログ】 ---\n"
                    experiment_logs += f.read()
    
    if not experiment_logs.strip():
         experiment_logs = "詳細なログファイルは見つかりませんでしたが、実験は実行されました。"

    # 4. Qwen2.5-Coderへのプロンプト作成
    prompt = f"""
    あなたは優秀なデータサイエンティストであり、オペレーションズ・リサーチの専門家です。
    以下の実験アイデアと実行ログを元に、日本語で簡潔な実験レポートをMarkdown形式で作成してください。
    
    # 構成案
    1. 実験の目的とアイデア（何を解決しようとしたか）
    2. 実施したアプローチ（AIがどのような試行錯誤やコード修正を行ったか）
    3. 結果と考察（数値はどう変化したか、最終的な結論）

    # 実験データ
    【タイトル】: {idea_data.get('Title', 'タイトル不明')}
    【アイデア詳細】: {idea_data.get('Experiment', '詳細不明')}
    【実験ログ・結果】:
    {experiment_logs}
    """

    # 5. Ollama経由でQwenにリクエスト
    print("🤖 Qwen2.5-Coder にレポート執筆を依頼しています...")
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
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        
        print(f"🎉 レポート出力完了: {report_path}")
        print("\n--- レポートのプレビュー ---\n")
        print(report_text[:600] + "...\n\n(続きはファイルブラウザから確認してください)")
        
    except Exception as e:
        print(f"レポート生成中にエラーが発生しました: {e}")

if __name__ == "__main__":
    generate_report()