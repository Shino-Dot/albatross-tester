# ==========================================================================
# ✨ アルバトロス・エクスポート魔法の書 ✨
# ==========================================================================
# 【このスクリプトの役割】
# ・プロジェクト全体のソースコードを「年月日_時分」付きの1つのファイルにパッキング！
# ・日本語の文字化けを完全ガード（UTF-8対応）
# ・余計なファイル（venvや__pycache__）を自動で除外する、賢い逆止弁付き🚀
#
# 【使いかた：3ステップ】
# 1. VS Codeのターミナルを開く
# 2. 仮想環境（venv）がONなのを確認！
#    (左側に (venv) って出てなかったら Scripts\activate してね！)
# 3. 以下の「呪文」を唱えるだけ！
#    >>> python export_albatross.py
#
# 【出力結果】
# ・「Albatross_Snapshot_20260125_0015.txt」みたいなファイルが生まれるよ💖
# ・生まれたファイルは「archives」フォルダにポイッとして整理整頓しよっ！
# ==========================================================================

import os
from datetime import datetime

# ==========================================
# 🛠️ 設定：ここを調整するだけでOK！
# ==========================================
# 1. 出力ファイル名のプレフィックス（前につける名前）
PROJECT_NAME = "Albatross_Snapshot"

# 2. 探索するフォルダ（マサ君のアプリたち）
TARGET_FOLDERS = ["accounts", "albatross_app", "albatross", "logs"]

# 3. 単体で拾いたい重要ファイル
TARGET_FILES = ["manage.py", "requirements.txt", "Dockerfile", "docker-compose.yml", "fly.toml", "README.md"]

# 4. 除外するフォルダ・拡張子（中身が多すぎるものや不要なもの）
EXCLUDE_DIRS = ["__pycache__", "migrations", "venv", ".git", "archives", "tools"]
INCLUDE_EXTENSIONS = [".py", ".html", ".css", ".js"]

# ==========================================
# 🚀 実行ロジック
# ==========================================

def main():
    # ① 日付と時間を取得して、マサ君の理想のタイトルを作る✨
    # 例：Albatross_Snapshot_20260125_0015.txt
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_filename = f"{PROJECT_NAME}_{timestamp}.txt"

    print(f"📦 パッキングを開始するよ、マサ君！目標：{output_filename}")

    # ② 書き込み開始（UTF-8指定で文字化けを完全ガード！）
    with open(output_filename, "w", encoding="utf-8") as f_out:
        # ヘッダー情報を書く
        f_out.write(f"==================================================\n")
        f_out.write(f"PROJECT: {PROJECT_NAME}\n")
        f_out.write(f"EXPORTED AT: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f_out.write(f"==================================================\n\n")

        # ③ フォルダ内を探索
        for folder in TARGET_FOLDERS:
            if not os.path.exists(folder):
                continue
            
            for root, dirs, files in os.walk(folder):
                # 不要なフォルダはスキップ！
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

                for filename in files:
                    if any(filename.endswith(ext) for ext in INCLUDE_EXTENSIONS):
                        file_path = os.path.join(root, filename)
                        write_file_content(f_out, file_path)

        # ④ ルート直下の重要ファイルを拾う
        for filename in TARGET_FILES:
            if os.path.exists(filename):
                write_file_content(f_out, filename)

    print(f"✨ 完了！『{output_filename}』が生まれたよ。アーカイブにしまっちゃおう💖")

def write_file_content(output_file, target_path):
    """ファイルを読み込んで、区切り線と一緒に書き込むよ"""
    try:
        output_file.write("--------------------------------------------------\n")
        output_file.write(f"File: {target_path.replace(os.sep, '/')}\n")
        output_file.write("--------------------------------------------------\n")
        
        # 読み込みもUTF-8で！エラーは無視（ignore）して止まらないようにする優しさ✨
        with open(target_path, "r", encoding="utf-8", errors="ignore") as f_in:
            output_file.write(f_in.read())
            
        output_file.write("\n\n")
    except Exception as e:
        print(f"⚠️ {target_path} の読み込み中にちょっとトラブル：{e}")

if __name__ == "__main__":
    main()