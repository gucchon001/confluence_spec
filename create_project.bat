@echo off
setlocal enabledelayedexpansion

chcp 65001 >nul

echo [LOG] スクリプトを開始します...

:: 親ディレクトリに移動
cd ..

:: プロジェクト名の入力
:INPUT_NAME
set /p PROJECT_NAME="プロジェクト名を入力してください: "

:: 入力値の検証
if "%PROJECT_NAME%"=="" (
    echo プロジェクト名を入力してください。
    goto INPUT_NAME
)

echo [LOG] プロジェクト名が入力されました: %PROJECT_NAME%

:: 特殊文字やスペースのチェック
echo %PROJECT_NAME%| findstr /r /c:"[^a-zA-Z0-9_-]" >nul
if not errorlevel 1 (
    echo エラー: プロジェクト名には英数字、ハイフン、アンダースコアのみ使用できます。
    goto INPUT_NAME
)

:: 確認
echo.
echo プロジェクト名: %PROJECT_NAME%
echo この名前でプロジェクトを作成しますか？ (Y/N)
set /p CONFIRM="選択してください: "

if /i not "%CONFIRM%"=="Y" goto INPUT_NAME

echo.
echo プロジェクト構造を作成中...
echo.

:: メインディレクトリ構造の作成
if exist "%PROJECT_NAME%" (
    echo エラー: %PROJECT_NAME% は既に存在します。
    goto END
)

echo [LOG] ディレクトリ構造の作成を開始します...

:: テンプレートディレクトリの設定
set "TEMPLATE_DIR=%~dp0templates"

:: テンプレートディレクトリの存在確認
if not exist "%TEMPLATE_DIR%" (
    echo エラー: テンプレートディレクトリが見つかりません: %TEMPLATE_DIR%
    goto END
)

:: テンプレートディレクトリ内のファイルの読み取り専用属性を解除
attrib -R "%TEMPLATE_DIR%\*" /S /D

:: プロジェクトフォルダ作成
mkdir "%PROJECT_NAME%"
echo [LOG] メインディレクトリを作成: %PROJECT_NAME%

:: サブディレクトリ作成
mkdir "%PROJECT_NAME%\src"
mkdir "%PROJECT_NAME%\src\utils"
mkdir "%PROJECT_NAME%\src\modules"
mkdir "%PROJECT_NAME%\tests"
mkdir "%PROJECT_NAME%\data"
mkdir "%PROJECT_NAME%\logs"
mkdir "%PROJECT_NAME%\config"
mkdir "%PROJECT_NAME%\docs"

echo [LOG] サブディレクトリの作成完了

:: README.mdのコピー
copy "%TEMPLATE_DIR%\README.md" "%PROJECT_NAME%\README.md" > nul
if errorlevel 1 (
    echo [ERROR] README.md のコピーに失敗しました。終了します。
    goto END
)
attrib -R "%PROJECT_NAME%\README.md"
echo [LOG] README.md をコピーしました。

:: __init__.pyファイルの作成
echo. > "%PROJECT_NAME%\src\__init__.py"
attrib -R "%PROJECT_NAME%\src\__init__.py"
echo. > "%PROJECT_NAME%\src\utils\__init__.py"
attrib -R "%PROJECT_NAME%\src\utils\__init__.py"
echo. > "%PROJECT_NAME%\src\modules\__init__.py"
attrib -R "%PROJECT_NAME%\src\modules\__init__.py"
echo. > "%PROJECT_NAME%\tests\__init__.py"
attrib -R "%PROJECT_NAME%\tests\__init__.py"

echo [LOG] __init__.pyファイルの作成完了

:: 空ディレクトリの追跡用 .gitkeep 作成
echo. > "%PROJECT_NAME%\logs\.gitkeep"
attrib -R "%PROJECT_NAME%\logs\.gitkeep"
echo. > "%PROJECT_NAME%\docs\.gitkeep"
attrib -R "%PROJECT_NAME%\docs\.gitkeep"

echo [LOG] 空ディレクトリの追跡用 .gitkeep を作成しました。

:: spec.md のコピー
copy "%TEMPLATE_DIR%\docs\spec.md" "%PROJECT_NAME%\docs\spec.md" > nul
if errorlevel 1 (
    echo [WARNING] spec.md のコピーに失敗しました。テンプレートが存在しない可能性があります。
) else (
    attrib -R "%PROJECT_NAME%\docs\spec.md"
    echo [LOG] spec.md をコピーしました。
)

:: settings.ini の作成
echo [LOG] settings.ini の作成を開始します...
(
echo [demo]
echo temp = "settings.ini"
echo [DEFAULT]
echo Exclusions = __pycache__,*.log,.env,.venv,*.pyc,*.pyo,*.tmp,.DS_Store,.git,.idea,.vscode,venv
echo.
echo [development]
echo DEBUG = True
echo LOG_LEVEL = DEBUG
echo.
echo [production]
echo DEBUG = False
echo LOG_LEVEL = WARNING
echo.
) > "%PROJECT_NAME%\config\settings.ini"
attrib -R "%PROJECT_NAME%\config\settings.ini"
echo [LOG] settings.ini を作成しました。

:: secrets.env の作成
echo [LOG] secrets.env の作成を開始します...
(
echo # secrets_demo
echo secrets_demo=demo
echo.
echo # SpreadSheetJson
echo SERVICE_ACCOUNT_FILE=config/spreadsheet.json
echo.
echo # Slack
echo SLACK_WEBHOOK=webhook_token
echo SLACK_BOT_TOKEN=xoxb-xxxxxxxxtoken
echo.
echo # OPENAI
echo OPENAI_API_KEY=test_api_key
) > "%PROJECT_NAME%\config\secrets.env"
attrib -R "%PROJECT_NAME%\config\secrets.env"
echo [LOG] secrets.env を作成しました。

:: requirements.txt の作成
(
echo numpy==1.26.2
echo pandas==2.1.3
echo matplotlib==3.8.2
echo openpyxl==3.1.2
echo requests==2.31.0
echo python-dotenv==1.0.0
echo pyyaml==6.0.1
echo google-api-python-client==2.108.0
echo google-auth-httplib2==0.1.1
echo google-auth-oauthlib==1.1.0
echo anytree==2.9.1
echo tqdm==4.66.1
echo loguru==0.7.2
echo pytest==7.4.3
echo pytest-cov==4.1.0
echo pytest-mock==3.12.0
echo black==23.11.0
echo flake8==6.1.0
echo mypy==1.7.1
) > "%PROJECT_NAME%\requirements.txt"
attrib -R "%PROJECT_NAME%\requirements.txt"
echo [LOG] requirements.txt を作成しました。

:: src 内のファイル作成
copy "%TEMPLATE_DIR%\python\main_template.py" "%PROJECT_NAME%\src\main.py" > nul
if errorlevel 1 echo [ERROR] main.py のコピーに失敗しました。終了します。 && goto END
attrib -R "%PROJECT_NAME%\src\main.py"

copy "%TEMPLATE_DIR%\python\environment_template.py" "%PROJECT_NAME%\src\utils\environment.py" > nul
if errorlevel 1 echo [ERROR] environment.py のコピーに失敗しました。終了します。 && goto END
attrib -R "%PROJECT_NAME%\src\utils\environment.py"

copy "%TEMPLATE_DIR%\python\logging_config_template.py" "%PROJECT_NAME%\src\utils\logging_config.py" > nul
if errorlevel 1 echo [ERROR] logging_config.py のコピーに失敗しました。終了します。 && goto END
attrib -R "%PROJECT_NAME%\src\utils\logging_config.py"

echo. > "%PROJECT_NAME%\src\modules\module1.py"
attrib -R "%PROJECT_NAME%\src\modules\module1.py"

echo. > "%PROJECT_NAME%\src\utils\helpers.py"
attrib -R "%PROJECT_NAME%\src\utils\helpers.py"

echo [LOG] src ディレクトリ内のファイル作成を完了しました。

:: tests フォルダのコピー
echo [LOG] tests フォルダをテンプレートからコピーします...
xcopy "%TEMPLATE_DIR%\tests" "%PROJECT_NAME%\tests" /E /I /Y > nul
if errorlevel 1 (
    echo [ERROR] tests フォルダのコピーに失敗しました。終了します。
    goto END
)
attrib -R "%PROJECT_NAME%\tests\*" /S /D
echo [LOG] tests フォルダをコピーしました。

:: run_dev.bat のコピー
copy "%TEMPLATE_DIR%\batch\run_dev.bat" "%PROJECT_NAME%\run_dev.bat" > nul
if errorlevel 1 echo [ERROR] run_dev.bat のコピーに失敗しました。 && goto END
attrib -R "%PROJECT_NAME%\run_dev.bat"
echo [LOG] run_dev.bat をプロジェクトにコピーしました。

:: run.bat のコピー
copy "%TEMPLATE_DIR%\batch\run.bat" "%PROJECT_NAME%\run.bat" > nul
if errorlevel 1 echo [ERROR] run.bat のコピーに失敗しました。 && goto END
attrib -R "%PROJECT_NAME%\run.bat"
echo [LOG] run.bat をプロジェクトにコピーしました。

:: update_libraries.bat のコピー
copy "%TEMPLATE_DIR%\batch\update_libraries.bat" "%PROJECT_NAME%\update_libraries.bat" > nul
if errorlevel 1 echo [ERROR] update_libraries.bat のコピーに失敗しました。 && goto END
attrib -R "%PROJECT_NAME%\update_libraries.bat"
echo [LOG] update_libraries.bat をプロジェクトにコピーしました。

:: .gitignore のコピー
copy "%TEMPLATE_DIR%\.gitignore" "%PROJECT_NAME%\.gitignore" > nul
if errorlevel 1 echo [ERROR] .gitignore のコピーに失敗しました。 && goto END
attrib -R "%PROJECT_NAME%\.gitignore"
echo [LOG] .gitignore をプロジェクトにコピーしました。

:: Git 初期化と改行コード設定
echo [LOG] Git リポジトリを初期化します...
cd "%PROJECT_NAME%"
git init > nul
if errorlevel 1 (
    echo [WARNING] Git リポジトリの初期化に失敗しました。
) else (
    echo [LOG] Git リポジトリを初期化しました。
    
    :: 改行コード設定
    git config core.autocrlf true > nul
    if errorlevel 1 (
        echo [WARNING] Git の改行コード設定に失敗しました。
    ) else (
        echo [LOG] Git の改行コード設定を完了しました。
    )
    
    :: .gitattributes ファイルの作成
    echo [LOG] .gitattributes ファイルを作成します...
    (
    echo # Auto detect text files and perform LF normalization
    echo * text=auto
    echo.
    echo # Explicitly declare text files you want to always be normalized and converted
    echo # to native line endings on checkout.
    echo *.py text
    echo *.md text
    echo *.txt text
    echo *.ini text
    echo *.env text
    echo.
    echo # Declare files that will always have CRLF line endings on checkout.
    echo *.bat text eol=crlf
    echo.
    echo # Denote all files that are truly binary and should not be modified.
    echo *.png binary
    echo *.jpg binary
    echo *.jpeg binary
    echo *.gif binary
    echo *.pdf binary
    echo *.zip binary
    ) > .gitattributes
    echo [LOG] .gitattributes ファイルを作成しました。
)
cd ..

:: プロジェクト内の全ファイルとディレクトリの読み取り専用属性を解除
echo [LOG] すべてのファイルから読み取り専用属性を解除します...
attrib -R /S /D "%PROJECT_NAME%\*"

:: 作成完了メッセージ
echo プロジェクト %PROJECT_NAME% の基本構造を作成しました。

:END
echo [LOG] スクリプトを終了します。
endlocal
