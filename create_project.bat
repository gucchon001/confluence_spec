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
mkdir "%PROJECT_NAME%\spec_tools"
mkdir "%PROJECT_NAME%\spec_tools\logs"

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
echo. > "%PROJECT_NAME%\spec_tools\logs\.gitkeep"
attrib -R "%PROJECT_NAME%\spec_tools\logs\.gitkeep"
echo. > "%PROJECT_NAME%\docs\.gitkeep"
attrib -R "%PROJECT_NAME%\docs\.gitkeep"

echo [LOG] 空ディレクトリの追跡用 .gitkeep を作成しました。

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
echo # Test
echo TEST_API_KEY=test_api_key
echo TEST_API_SECRET=test_api_secret
) > "%PROJECT_NAME%\config\secrets.env"
attrib -R "%PROJECT_NAME%\config\secrets.env"
echo [LOG] secrets.env を作成しました。

:: requirements.txt の作成
(
echo pandas
echo pytest
echo requests==2.31.0
echo python-dotenv==1.0.0
echo google-api-python-client==2.108.0
echo google-auth-httplib2==0.1.1
echo google-auth-oauthlib==1.1.0
echo anytree
echo openai==1.55.0
echo icecream
) > "%PROJECT_NAME%\requirements.txt"
attrib -R "%PROJECT_NAME%\requirements.txt"
echo [LOG] requirements.txt を作成しました。

:: spec_tools スクリプトのコピー
echo [LOG] spec_tools スクリプトのコピーを開始します...

:: コピー対象のファイルリスト
set SPEC_TOOLS_FILES=generate_detailed_spec.py generate_spec.py merge_files.py utils.py
set PROMPT_DIR=spec_tools\prompt

:: spec_tools ファイルのコピー
for %%F in (%SPEC_TOOLS_FILES%) do (
    copy "%TEMPLATE_DIR%\spec_tools\%%F" "%PROJECT_NAME%\spec_tools\%%F" > nul
    if errorlevel 1 (
        echo [ERROR] %%F のコピーに失敗しました。終了します。
        goto END
    )
    attrib -R "%PROJECT_NAME%\spec_tools\%%F"
    echo [LOG] %%F をコピーしました。
)

echo [LOG] spec_tools スクリプトをすべてコピーしました。

:: prompt フォルダと配下のファイルをコピー
if exist "%TEMPLATE_DIR%\%PROMPT_DIR%" (
    xcopy "%TEMPLATE_DIR%\%PROMPT_DIR%" "%PROJECT_NAME%\%PROMPT_DIR%" /E /I /Y > nul
    if errorlevel 1 (
        echo [ERROR] prompt フォルダのコピーに失敗しました。終了します。
        goto END
    )
    attrib -R "%PROJECT_NAME%\%PROMPT_DIR%\*" /S /D
    echo [LOG] prompt フォルダと配下のファイルをコピーしました。
) else (
    echo [ERROR] prompt フォルダが見つかりません。
    goto END
)

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

:: spec_tools_run.bat のコピー
copy "%TEMPLATE_DIR%\batch\spec_tools_run.bat" "%PROJECT_NAME%\spec_tools_run.bat" > nul
if errorlevel 1 echo [ERROR] spec_tools_run.bat のコピーに失敗しました。 && goto END
attrib -R "%PROJECT_NAME%\spec_tools_run.bat"
echo [LOG] spec_tools_run.bat をプロジェクトにコピーしました。

:: .gitignore のコピー
copy "%TEMPLATE_DIR%\.gitignore" "%PROJECT_NAME%\.gitignore" > nul
if errorlevel 1 echo [ERROR] .gitignore のコピーに失敗しました。 && goto END
attrib -R "%PROJECT_NAME%\.gitignore"
echo [LOG] .gitignore をプロジェクトにコピーしました。

:: プロジェクト内の全ファイルとディレクトリの読み取り専用属性を解除
echo [LOG] すべてのファイルから読み取り専用属性を解除します...
attrib -R /S /D "%PROJECT_NAME%\*"

:: 作成完了メッセージ
echo プロジェクト %PROJECT_NAME% の基本構造を作成しました。
echo 作成されたディレクトリ: %CD%\%PROJECT_NAME%

:END
echo [LOG] スクリプトを終了します。
endlocal
