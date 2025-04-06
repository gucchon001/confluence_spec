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

:: cursor rules のコピー
if exist "%TEMPLATE_DIR%\rules" (
    mkdir "%PROJECT_NAME%\.cursor"
    mkdir "%PROJECT_NAME%\.cursor\rules"
    xcopy "%TEMPLATE_DIR%\rules" "%PROJECT_NAME%\.cursor\rules" /E /I /Y > nul
    if errorlevel 1 (
         echo [ERROR] cursor rules のコピーに失敗しました。終了します。
         goto END
    )
    attrib -R "%PROJECT_NAME%\.cursor\rules\*" /S /D
    echo [LOG] cursor rules をプロジェクトにコピーしました。
) else (
    echo [WARNING] テンプレートに cursor rules フォルダが存在しません。
)

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
echo NOTIFY_SUCCESS = True
echo NOTIFY_ERROR = True
echo.
echo [production]
echo DEBUG = False
echo LOG_LEVEL = WARNING
echo NOTIFY_SUCCESS = False
echo NOTIFY_ERROR = True
echo.
echo [slack]
echo FOOTER_TEXT = プロジェクト通知
echo ICON_URL = https://platform.slack-edge.com/img/default_application_icon.png
echo DEFAULT_COLOR = #36a64f
echo ERROR_COLOR = #ff0000
echo SUCCESS_COLOR = #2eb886
echo.
echo [SPREADSHEET]
echo SSID = 1fAmsevrYFI1WZsScsFnqtmQsmUKe6RUzS1a0hQ1KZeo
echo TEST_SHEET = data
echo.
echo [SHEET_NAMES]
echo users = users_all
echo entry = entryprocess_all
echo logs = logging
echo.
echo [BROWSER]
echo headless = false
echo auto_screenshot = true
echo screenshot_dir = logs/screenshots
echo screenshot_format = png
echo screenshot_quality = 100
echo screenshot_on_error = true
echo window_width = 1920
echo window_height = 1080
echo page_load_timeout = 30
echo timeout = 10
echo additional_options = --disable-gpu,--no-sandbox
echo.
echo [LOGIN]
echo url = https://example.com/login
echo success_url = /dashboard
echo max_attempts = 3
echo redirect_timeout = 30
echo element_timeout = 10
echo page_load_wait = 2
echo screenshot_on_login = true
echo basic_auth_enabled = false
echo # 以下の認証情報は secrets.env から取得されます
echo # LOGIN_USERNAME, LOGIN_PASSWORD, LOGIN_ACCOUNT_KEY
echo # LOGIN_BASIC_AUTH_USERNAME, LOGIN_BASIC_AUTH_PASSWORD
echo third_field_name = account_key
echo success_element_selector = .welcome-message
echo success_element_type = css
echo error_selector = .error-message
echo error_type = css
echo.
echo [TESTS]
echo DUMMY_LOGIN_URL = 
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
echo # GOOGLE SERVICE
echo GOOGLE_APPLICATION_CREDENTIALS=config/google-service-account.json
echo PROJECT_ID=your-project-id
echo GCS_BUCKET_NAME=auth_gcs_test
echo BIGQUERY_DATASET=auth_test
echo BIGQUERY_TABLE=sample_table
echo.
echo # Slack
echo SLACK_WEBHOOK_DEV=webhook_token_for_development
echo SLACK_WEBHOOK_PROD=webhook_token_for_production
echo SLACK_BOT_TOKEN=xoxb-xxxxxxxxtoken
echo.
echo # OPENAI
echo OPENAI_API_KEY=test_api_key
echo.
echo # テスト用アカウント
echo TEST_ACCOUNT_KEY=DEMO123
echo TEST_USERNAME=testuser@example.com
echo TEST_PASSWORD=password123
echo.
echo # ログイン認証情報
echo LOGIN_USERNAME=your_username
echo LOGIN_PASSWORD=your_secure_password
echo LOGIN_ACCOUNT_KEY=your_account_key
echo LOGIN_BASIC_AUTH_USERNAME=basic_auth_user
echo LOGIN_BASIC_AUTH_PASSWORD=basic_auth_password
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
echo google-cloud-bigquery==2.34.4
echo google-cloud-storage==2.9.0
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

:: utils ディレクトリの作成確認
if not exist "%PROJECT_NAME%\src\utils" (
    mkdir "%PROJECT_NAME%\src\utils"
    echo [LOG] src\utils ディレクトリを作成しました。
)

echo [LOG] テンプレートファイルをsrc/utilsにコピーします...

:: テンプレート接尾辞を持つファイルをコピーして名前を変更
copy "%TEMPLATE_DIR%\python\utils\environment_template.py" "%PROJECT_NAME%\src\utils\environment.py" > nul
if errorlevel 1 echo [ERROR] environment.py のコピーに失敗しました。終了します。 && goto END
attrib -R "%PROJECT_NAME%\src\utils\environment.py"
echo [LOG] environment.py をコピーしました。

copy "%TEMPLATE_DIR%\python\utils\logging_config_template.py" "%PROJECT_NAME%\src\utils\logging_config.py" > nul
if errorlevel 1 echo [ERROR] logging_config.py のコピーに失敗しました。終了します。 && goto END
attrib -R "%PROJECT_NAME%\src\utils\logging_config.py"
echo [LOG] logging_config.py をコピーしました。

copy "%TEMPLATE_DIR%\python\utils\slack_notifier_template.py" "%PROJECT_NAME%\src\utils\slack_notifier.py" > nul
if errorlevel 1 echo [ERROR] slack_notifier.py のコピーに失敗しました。終了します。 && goto END
attrib -R "%PROJECT_NAME%\src\utils\slack_notifier.py"
echo [LOG] slack_notifier.py をコピーしました。

copy "%TEMPLATE_DIR%\python\utils\spreadsheet_template.py" "%PROJECT_NAME%\src\utils\spreadsheet.py" > nul
if errorlevel 1 echo [ERROR] spreadsheet.py のコピーに失敗しました。終了します。 && goto END
attrib -R "%PROJECT_NAME%\src\utils\spreadsheet.py"
echo [LOG] spreadsheet.py をコピーしました。

copy "%TEMPLATE_DIR%\python\utils\bigquery_template.py" "%PROJECT_NAME%\src\utils\bigquery.py" > nul
if errorlevel 1 echo [ERROR] bigquery.py のコピーに失敗しました。終了します。 && goto END
attrib -R "%PROJECT_NAME%\src\utils\bigquery.py"
echo [LOG] bigquery.py をコピーしました。

:: テンプレート接尾辞のないファイルをそのままコピー
copy "%TEMPLATE_DIR%\python\utils\git_batch.py" "%PROJECT_NAME%\src\utils\git_batch.py" > nul
if errorlevel 1 echo [ERROR] git_batch.py のコピーに失敗しました。終了します。 && goto END
attrib -R "%PROJECT_NAME%\src\utils\git_batch.py"
echo [LOG] git_batch.py をコピーしました。

copy "%TEMPLATE_DIR%\python\utils\openai_git_helper.py" "%PROJECT_NAME%\src\utils\openai_git_helper.py" > nul
if errorlevel 1 echo [ERROR] openai_git_helper.py のコピーに失敗しました。終了します。 && goto END
attrib -R "%PROJECT_NAME%\src\utils\openai_git_helper.py"
echo [LOG] openai_git_helper.py をコピーしました。

:: 追加のヘルパーファイル作成
echo. > "%PROJECT_NAME%\src\modules\module1.py"
attrib -R "%PROJECT_NAME%\src\modules\module1.py"

echo. > "%PROJECT_NAME%\src\utils\helpers.py"
attrib -R "%PROJECT_NAME%\src\utils\helpers.py"

:: selenium モジュールのコピー
if exist "%TEMPLATE_DIR%\python\selenium" (
    echo [LOG] selenium モジュールをコピーします...
    xcopy "%TEMPLATE_DIR%\python\selenium" "%PROJECT_NAME%\src\modules\selenium" /E /I /Y > nul
    if errorlevel 1 (
        echo [ERROR] selenium モジュールのコピーに失敗しました。
        goto END
    )
    attrib -R "%PROJECT_NAME%\src\modules\selenium\*" /S /D
    echo [LOG] selenium モジュールを src\modules\ にコピーしました。
) else (
    echo [WARNING] selenium モジュールのディレクトリが見つかりません: %TEMPLATE_DIR%\python\selenium
)

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

:: bigquery_auth テストファイル処理
if exist "%PROJECT_NAME%\tests\test_bigquery_auth.py" (
    del "%PROJECT_NAME%\tests\test_bigquery_auth.py"
    echo [LOG] 古い test_bigquery_auth.py を削除しました。
)

:: 新しいGoogle Cloud認証テストファイルをコピー
copy "%TEMPLATE_DIR%\tests\test_google_cloud_auth.py" "%PROJECT_NAME%\tests\test_google_cloud_auth.py" > nul
if errorlevel 1 echo [ERROR] test_google_cloud_auth.py のコピーに失敗しました。終了します。 && goto END
attrib -R "%PROJECT_NAME%\tests\test_google_cloud_auth.py"
echo [LOG] test_google_cloud_auth.py をコピーしました。

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

:: run_git_ai.bat のコピー
copy "%TEMPLATE_DIR%\batch\run_git_ai.bat" "%PROJECT_NAME%\run_git_ai.bat" > nul
if errorlevel 1 echo [ERROR] run_git_ai.bat のコピーに失敗しました。 && goto END
attrib -R "%PROJECT_NAME%\run_git_ai.bat"
echo [LOG] run_git_ai.bat をプロジェクトにコピーしました。

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

:: テスト用サンプルファイルのディレクトリを作成
echo [LOG] テスト用サンプルファイルディレクトリを作成します...
mkdir "%PROJECT_NAME%\tests\sample_files" 2>nul
if errorlevel 1 (
    echo [WARN] tests\sample_files ディレクトリの作成に失敗しました。既に存在する可能性があります。
) else (
    echo [LOG] tests\sample_files ディレクトリを作成しました。
)

:: テスト用サンプルファイルを作成
(
echo これはGCSアップロードテスト用のサンプルファイルです。
echo.
echo このファイルはproject作成時に自動生成されています。
echo GCSへのファイルアップロード機能をテストするために使用されます。
echo.
echo 作成日時: %date% %time%
) > "%PROJECT_NAME%\tests\sample_files\sample.txt"
echo [LOG] テスト用サンプルファイル sample.txt を作成しました。

:: selectors.csv ファイルの作成
echo [LOG] selectors.csv ファイルを作成します...
(
echo group,name,selector_type,selector_value,description
echo login,account_key,id,account_key,アカウントキー入力欄
echo login,username,id,username,ユーザー名入力欄
echo login,password,id,password,パスワード入力欄
echo login,login_button,css,.loginbtn,ログインボタン
) > "%PROJECT_NAME%\config\selectors.csv"
echo [LOG] selectors.csv ファイルを作成しました。

:: 作成完了メッセージ
echo プロジェクト %PROJECT_NAME% の基本構造を作成しました。

:END
echo [LOG] スクリプトを終了します。
endlocal
