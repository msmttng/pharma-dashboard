@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

:: .envファイルから設定を読み込みます
if exist ".env" (
    echo .envファイルから設定を読み込みます...
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        set %%a=%%b
    )
)

echo.
echo 1. 各サイトから最新のデータを取得しています... (数分かかる場合があります)
call .\venv\Scripts\python fetch_data.py
if %ERRORLEVEL% neq 0 (
    echo エラーが発生しました。データ取得に失敗しました。
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo 2. ダッシュボードを生成しています...
call .\venv\Scripts\python generate_dashboard.py
if %ERRORLEVEL% neq 0 (
    echo エラーが発生しました。ダッシュボードの生成に失敗しました。
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo 3. 通知データを送信しています...
call .\venv\Scripts\python sync_to_gas.py
if %ERRORLEVEL% neq 0 (
    echo 通知データの送信中にエラーが発生しました（スキップします）。
)

echo.
echo 4. ブラウザでダッシュボードを開きます...
start dashboard.html

echo.
echo 完了しました！何かキーを押すと閉じます。
pause