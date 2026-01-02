
    # 出力ファイル名を指定
    $outputFile = "project_summary-20251229.txt"

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
    