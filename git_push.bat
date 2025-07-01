@echo off
REM GitHubリポジトリをクローン（初回のみ使う）
REM git clone git@github.com:ユーザー名/リポジトリ名.git

REM 変更をステージに追加
git add .

REM コミットメッセージを指定してコミット
git commit -m "Update from batch file"

REM リモートのmainブランチへプッシュ
git push origin main

pause
