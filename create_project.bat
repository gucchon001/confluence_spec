@echo off
setlocal enabledelayedexpansion

echo [LOG] �X�N���v�g���J�n���܂�...

:: �e�f�B���N�g���Ɉړ�
cd ..

:: �v���W�F�N�g���̓���
:INPUT_NAME
set /p PROJECT_NAME="�v���W�F�N�g������͂��Ă�������: "

:: ���͒l�̌���
if "%PROJECT_NAME%"=="" (
    echo �v���W�F�N�g������͂��Ă��������B
    goto INPUT_NAME
)

echo [LOG] �v���W�F�N�g�������͂���܂���: %PROJECT_NAME%

:: ���ꕶ����X�y�[�X�̃`�F�b�N
echo %PROJECT_NAME%| findstr /r /c:"[^a-zA-Z0-9_-]" >nul
if not errorlevel 1 (
    echo �G���[: �v���W�F�N�g���ɂ͉p�����A�n�C�t���A�A���_�[�X�R�A�̂ݎg�p�ł��܂��B
    goto INPUT_NAME
)

:: �m�F
echo.
echo �v���W�F�N�g��: %PROJECT_NAME%
echo ���̖��O�Ńv���W�F�N�g���쐬���܂����H (Y/N)
set /p CONFIRM="�I�����Ă�������: "

if /i not "%CONFIRM%"=="Y" goto INPUT_NAME

echo.
echo �v���W�F�N�g�\�����쐬��...
echo.

:: ���C���f�B���N�g���\���̍쐬
if exist "%PROJECT_NAME%" (
    echo �G���[: %PROJECT_NAME% �͊��ɑ��݂��܂��B
    goto END
)

echo [LOG] �f�B���N�g���\���̍쐬���J�n���܂�...

:: �e���v���[�g�f�B���N�g���̐ݒ�
set "TEMPLATE_DIR=%~dp0templates"

:: �e���v���[�g�f�B���N�g���̑��݊m�F
if not exist "%TEMPLATE_DIR%" (
    echo �G���[: �e���v���[�g�f�B���N�g����������܂���: %TEMPLATE_DIR%
    goto END
)

:: �v���W�F�N�g�t�H���_�쐬
mkdir "%PROJECT_NAME%"
echo [LOG] ���C���f�B���N�g�����쐬: %PROJECT_NAME%

:: �T�u�f�B���N�g���쐬
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

echo [LOG] �T�u�f�B���N�g���̍쐬����

:: README.md�̃R�s�[
copy "%TEMPLATE_DIR%\README.md" "%PROJECT_NAME%\README.md" > nul
if errorlevel 1 (
    echo [ERROR] README.md �̃R�s�[�Ɏ��s���܂����B�I�����܂��B
    goto END
)
echo [LOG] README.md ���R�s�[���܂����B

:: __init__.py�t�@�C���̍쐬
echo. > "%PROJECT_NAME%\src\__init__.py"
echo. > "%PROJECT_NAME%\src\utils\__init__.py"
echo. > "%PROJECT_NAME%\src\modules\__init__.py"
echo. > "%PROJECT_NAME%\tests\__init__.py"

echo [LOG] __init__.py�t�@�C���̍쐬����

:: ��f�B���N�g���̒ǐ՗p .gitkeep �쐬
echo. > "%PROJECT_NAME%\logs\.gitkeep"
echo. > "%PROJECT_NAME%\spec_tools\logs\.gitkeep"
echo. > "%PROJECT_NAME%\docs\.gitkeep"

echo [LOG] ��f�B���N�g���̒ǐ՗p .gitkeep ���쐬���܂����B

:: settings.ini �̍쐬
echo [LOG] settings.ini �̍쐬���J�n���܂�...
(
echo [demo]
echo temp = "settings.ini"
echo [DEFAULT]
echo Exclusions = __pycache__,*.log,.env,.venv,*.pyc,*.pyo,*.tmp,.DS_Store,.git,.idea,.vscode
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

echo [LOG] settings.ini ���쐬���܂����B

:: secrets.env �̍쐬
echo [LOG] secrets.env �̍쐬���J�n���܂�...
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

echo [LOG] secrets.env ���쐬���܂����B

:: requirements.txt �̍쐬
(
echo # Required packages
echo pandas
echo pytest
echo requests==2.31.0
echo python-dotenv==1.0.0
echo google-api-python-client==2.108.0
echo google-auth-httplib2==0.1.1
echo google-auth-oauthlib==1.1.0
) > "%PROJECT_NAME%\requirements.txt"

echo [LOG] requirements.txt ���쐬���܂����B

:: spec_tools �X�N���v�g�̃R�s�[
echo [LOG] spec_tools �X�N���v�g�̃R�s�[���J�n���܂�...

:: �R�s�[�Ώۂ̃t�@�C�����X�g
set SPEC_TOOLS_FILES=generate_detailed_spec.py generate_spec.py merge_files.py prompt_generate_detailed_spec.txt prompt_requirements_spec.txt utils.py

for %%F in (%SPEC_TOOLS_FILES%) do (
    copy "%TEMPLATE_DIR%\spec_tools\%%F" "%PROJECT_NAME%\spec_tools\%%F" > nul
    if errorlevel 1 (
        echo [ERROR] %%F �̃R�s�[�Ɏ��s���܂����B�I�����܂��B
        goto END
    )
    echo [LOG] %%F ���R�s�[���܂����B
)

echo [LOG] spec_tools �X�N���v�g�����ׂăR�s�[���܂����B

:: src ���̃t�@�C���쐬
copy "%TEMPLATE_DIR%\python\main_template.py" "%PROJECT_NAME%\src\main.py" > nul
if errorlevel 1 echo [ERROR] main.py �̃R�s�[�Ɏ��s���܂����B�I�����܂��B && goto END

copy "%TEMPLATE_DIR%\python\environment_template.py" "%PROJECT_NAME%\src\utils\environment.py" > nul
if errorlevel 1 echo [ERROR] config.py �̃R�s�[�Ɏ��s���܂����B�I�����܂��B && goto END

copy "%TEMPLATE_DIR%\python\logging_config_template.py" "%PROJECT_NAME%\src\utils\logging_config.py" > nul
if errorlevel 1 echo [ERROR] logging_config.py �̃R�s�[�Ɏ��s���܂����B�I�����܂��B && goto END

echo. > "%PROJECT_NAME%\src\modules\module1.py"
echo. > "%PROJECT_NAME%\src\utils\helpers.py"

echo [LOG] src �f�B���N�g�����̃t�@�C���쐬���������܂����B

:: run_dev.bat �̃R�s�[
copy "%TEMPLATE_DIR%\batch\run_dev.bat" "%PROJECT_NAME%\run_dev.bat" > nul
if errorlevel 1 echo [ERROR] run.bat �̃R�s�[�Ɏ��s���܂����B && goto END
echo [LOG] run.bat ���v���W�F�N�g�ɃR�s�[���܂����B

:: run.bat �̃R�s�[
copy "%TEMPLATE_DIR%\batch\run.bat" "%PROJECT_NAME%\run.bat" > nul
if errorlevel 1 echo [ERROR] run.bat �̃R�s�[�Ɏ��s���܂����B && goto END
echo [LOG] run.bat ���v���W�F�N�g�ɃR�s�[���܂����B

:: spec_tools_run.bat �̃R�s�[
copy "%TEMPLATE_DIR%\batch\spec_tools_run.bat" "%PROJECT_NAME%\spec_tools_run.bat" > nul
if errorlevel 1 echo [ERROR] spec_tools_run.bat �̃R�s�[�Ɏ��s���܂����B && goto END
echo [LOG] spec_tools_run.bat ���v���W�F�N�g�ɃR�s�[���܂����B

:: .gitignore �̃R�s�[
copy "%TEMPLATE_DIR%\.gitignore" "%PROJECT_NAME%\.gitignore" > nul
if errorlevel 1 echo [ERROR] .gitignore �̃R�s�[�Ɏ��s���܂����B && goto END
echo [LOG] .gitignore ���v���W�F�N�g�ɃR�s�[���܂����B

:: �쐬�������b�Z�[�W
echo �v���W�F�N�g %PROJECT_NAME% �̊�{�\�����쐬���܂����B
echo �쐬���ꂽ�f�B���N�g��: %CD%\%PROJECT_NAME%

:END
echo [LOG] �X�N���v�g���I�����܂��B
endlocal
