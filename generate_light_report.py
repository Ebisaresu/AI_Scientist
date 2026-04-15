import os
import glob
import json
import openai
import argparse

def generate_report(experiment_name, overwrite):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_base_dir = os.path.join(script_dir, "results", experiment_name)
    
    print(f"🔍 検索ベースディレクトリ: {target_base_dir}")
    
    if not os.path.exists(target_base_dir):
        print(f"\n❌ エラー: 指定された実験フォルダ '{experiment_name}' が存在しません。")
        return

    result_dirs = glob.glob(os.path.join(target_base_dir, "202*"))
    valid_dirs = [d for d in result_dirs if os.path.exists(os.path.join(d, "ideas.json"))]
            
    if not valid_dirs:
        print("\n❌ エラー: ideas.json を含む有効な実験フォルダが見つかりませんでした。")
        return
        
    print(f"\n📂 対象となる実験フォルダ数: {len(valid_dirs)}件\n")

    client = openai.OpenAI(
        api_key="ollama",
        base_url="http://localhost:11434/v1"
    )

    # 全フォルダをアルファベット順（古い順）にループ処理
    for target_dir in sorted(valid_dirs):
        dir_name = os.path.basename(target_dir)
        report_path = os.path.join(target_dir, "light_report.md")

        # 上書きモードでなく、既にレポートがある場合はスキップ
        if not overwrite and os.path.exists(report_path):
            print(f"⏩ スキップ: {dir_name} (既にレポートが存在します)")
            continue

        print(f"🎯 レポート生成開始: {dir_name}")

        # 2. アイデア情報の読み込み
        idea_data = {}
        try:
            with open(os.path.join(target_dir, "ideas.json"), "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                
            if isinstance(raw_data, list):
                for item in raw_data:
                    if isinstance(item, dict) and item.get("Name") in target_dir:
                        idea_data = item
                        break
                if not idea_data and len(raw_data) > 0:
                    idea_data = raw_data[0]
            elif isinstance(raw_data, dict):
                idea_data = raw_data
        except Exception as e:
            print(f"  [エラー] ideas.json の読み込みに失敗: {e}")
            continue

        # 3. ログのかき集め
        experiment_logs = ""
        run_dirs = sorted(glob.glob(os.path.join(target_dir, "run_*")))
        
        if run_dirs:
            for run_dir in run_dirs:
                notes_path = os.path.join(run_dir, "notes.txt")
                if os.path.exists(notes_path):
                    with open(notes_path, "r", encoding="utf-8") as f:
                        experiment_logs += f"\n\n--- 【{os.path.basename(run_dir)} の試行ログ】 ---\n"
                        experiment_logs += f.read()
        
        # ★ハルシネーション（捏造）対策★
        if not experiment_logs.strip():
             experiment_logs = "【システムからの警告】詳細な実行ログ（notes.txt）が一つも見つかりませんでした。コードの構文エラー等で実験が途中で異常終了（クラッシュ）した可能性が高いです。成功したと捏造せず、失敗・エラー終了した旨を正直に記載してください。"

        # 4. プロンプト作成
        prompt = f"""
        あなたは優秀なデータサイエンティストであり、オペレーションズ・リサーチの専門家です。
        以下の実験アイデアと実行ログを元に、日本語で簡潔な実験レポートをMarkdown形式で作成してください。
        
        # 構成案
        1. 実験の目的とアイデア（何を解決しようとしたか）
        2. 実施したアプローチと結果（ログに「警告」がある場合は、エラー終了した旨を正直に記載すること）
        3. 考察と次のステップ

        # 実験データ
        【タイトル】: {idea_data.get('Title', 'タイトル不明')}
        【アイデア詳細】: {idea_data.get('Experiment', '詳細不明')}
        【実験ログ・結果】:
        {experiment_logs}
        """

        # 5. Ollama経由でQwenにリクエスト
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            report_text = response.choices[0].message.content
            
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_text)
            
            print(f"  🎉 出力完了: {report_path}")
        except Exception as e:
            print(f"  [エラー] レポート生成中に問題が発生: {e}")

    print("\n✅ すべてのレポート処理が完了しました！")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI-Scientistの実験結果からレポートを一括生成します。")
    parser.add_argument("--experiment", type=str, default="island_defense", help="対象フォルダ名")
    parser.add_argument("--overwrite", action="store_true", help="既存のレポートを強制的に上書き生成する")
    args = parser.parse_args()
    
    generate_report(args.experiment, args.overwrite)