# プロジェクト全体のソースコードをテキストファイルに出力する方法

このプロジェクトのソースコード全体を、引越しやレビューのために1つのテキストファイルにまとめるための手順。

## 必要なもの
- Windows PowerShell

## 手順

1.  **PowerShellを開く**
    スタートメニューなどから「PowerShell」を起動する。

2.  **プロジェクトのルートディレクトリに移動する**
    `cd`コマンドを使って、この`albatross`フォルダに移動する。
    （例：デスクトップにある場合）
    ```shell
    cd Desktop\albatross
    ```

3.  **以下のスクリプトを実行する**
    下のPowerShellスクリプトを、まるごと全部コピーして、PowerShellの画面に貼り付けて`Enter`キーを押す。

    ```powershell
    # -------------------- ここからコピー --------------------

    # 出力ファイル名を指定
    $outputFile = "project_summary.txt"

    # もし既に出力ファイルが存在していたら、一旦削除する
    if (Test-Path $outputFile) { Remove-Item $outputFile }

    # テキスト化の対象とするフォルダを指定
    $targetFolders = "accounts", "albatross_app", "logs", "albatross"

    # メインの処理
    Get-ChildItem -Path $targetFolders -Recurse -Include *.py, *.html, *.css, *.js | ForEach-Object {
        # 区切り線とファイルパスを、UTF-8でファイルに追加していく
        Add-Content -Path $outputFile -Value "--------------------------------------------------" -Encoding utf8
        Add-Content -Path $outputFile -Value "File: $($_.FullName.Substring($PWD.Path.Length))" -Encoding utf8
        Add-Content -Path $outputFile -Value "--------------------------------------------------" -Encoding utf8
        
        # ファイルを読み込む時に、UTF-8として読み込むように明示的に指定
        $content = Get-Content $_.FullName -Encoding utf8 -Raw
        
        # 読み込んだ内容を、UTF-8でファイルに追加していく
        Add-Content -Path $outputFile -Value $content -Encoding utf8
        Add-Content -Path $outputFile -Value "" -Encoding utf8
    }

    Write-Host "処理が完了しました！ '$($outputFile)' が作成されました。" -ForegroundColor Green
    
    # -------------------- ここまでコピー --------------------
    ```

4.  **完了を待つ**
    処理が終わると、`処理が完了しました！ 'project_summary.txt' が作成されました。`という緑色のメッセージが表示される。

5.  **ファイルの確認**
    `albatross`フォルダ内に`project_summary.txt`というファイルが作成されていることを確認する。

## 注意事項
- このスクリプトは、`$targetFolders`で指定されたフォルダの中だけを検索します。新しいアプリを追加した場合は、リストに追加してください。
- `venv`や`__pycache__`、`db.sqlite3`などは自動的に除外されます。s