import os

# --- 設定 ---
OUTPUT_FILENAME = "project_source_code.txt"
TARGET_FOLDERS = ["accounts", "albatross_app", "albatross", "lp"]
TARGET_FILES = ["manage.py", "requirements.txt", "fly.toml", "Dockerfile"]
EXCLUDE_DIRS = ["__pycache__", "migrations"]
INCLUDE_EXTENSIONS = [".py", ".html", ".css", ".js"]
# --- 設定ここまで ---

def get_all_filepaths(folders, files):
    """指定されたフォルダとファイルから、対象となるファイルのパスを全て取得する"""
    filepaths = []
    # フォルダの中を再帰的に探索
    for folder in folders:
        for root, dirs, files_in_dir in os.walk(folder):
            # 除外フォルダをスキップ
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for filename in files_in_dir:
                if any(filename.endswith(ext) for ext in INCLUDE_EXTENSIONS):
                    filepaths.append(os.path.join(root, filename))
    # ルートのファイルを追加
    for filename in files:
        if os.path.exists(filename):
            filepaths.append(filename)
    return filepaths

def main():
    """メインの処理"""
    all_files = get_all_filepaths(TARGET_FOLDERS, TARGET_FILES)
    
    # ★★★ ここがポイント！ ★★★
    # open()関数で、encoding='utf-8' を、ちゃんと指定して、ファイルを開く！
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f_out:
        for filepath in all_files:
            try:
                f_out.write("--------------------------------------------------\n")
                f_out.write(f"File: {filepath.replace(os.sep, '/')}\n")
                f_out.write("--------------------------------------------------\n")
                
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f_in:
                    f_out.write(f_in.read())
                    
                f_out.write("\n\n")
            except Exception as e:
                print(f"Error processing file {filepath}: {e}")

    print(f"処理が完了しました！ '{OUTPUT_FILENAME}' が作成されました。")

if __name__ == "__main__":
    main()
    