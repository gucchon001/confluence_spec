from utils.environment import EnvironmentUtils as env
from utils.logging_config import get_logger
import configparser
from dotenv import dotenv_values

# 名前付きロガーを取得
logger = get_logger(__name__)

def setup_configurations():
    """設定ファイルと機密情報の設定を行い、取得したデータを返す"""
    # 環境変数のロード
    env.load_env()

    # settings.ini のパス取得と読み込み
    settings_path = env.get_settings_path()
    config = configparser.ConfigParser()
    config.read(settings_path)
    temp_value = config['demo']['temp']
    logger.info(f"[demo] temp: {temp_value}")

    # secrets.env のパス取得と読み込み
    secrets_path = env.get_secrets_path()
    secrets = dotenv_values(secrets_path)
    secrets_demo = secrets['secrets_demo']
    logger.info(f"secrets_demo: {secrets_demo}")

    # 現在の環境の取得とログファイルのパス確認
    environment = env.get_environment()
    log_path = env.get_log_path(environment)
    logger.info(f"ログファイルのパス確認: {log_path} は存在します。")
    logger.info(f"Current environment: {environment}")

    return temp_value, secrets_demo, environment

def main() -> None:
    """メイン処理"""
    # 実行時にプロジェクト名を表示
    print("Hello,newProject!!")  # バッチファイルで置換されます
    logger.info("Hello, newProject!!")

    # 設定ファイルと機密情報の設定
    temp, secrets_demo, environment = setup_configurations()

    # 設定完了のメッセージを表示
    print(f'設定ファイルの設定完了{{"demo": "{temp}"}}')
    print(f'機密情報ファイルの設定完了{{"demo": "{secrets_demo}"}}')
    print('ログ設定完了')

if __name__ == "__main__":
    main()
