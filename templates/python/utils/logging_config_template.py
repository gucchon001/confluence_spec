# logging_config.py
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional
from src.utils.environment import env  # 追加: env をインポート

class LoggingConfig:
    _initialized = False

    def __init__(self):
        """
        ログ設定を初期化します。
        """
        if LoggingConfig._initialized:
            return  # 再初期化を防止

        # ログディレクトリはプロジェクトルートからの相対パス
        self.log_dir = Path("logs")
        
        # 設定ファイルからログレベルを取得
        log_level_str = env.get_log_level()
        
        # 文字列からログレベルに変換
        log_level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        self.log_level = log_level_map.get(log_level_str, logging.INFO)
        
        self.log_format = "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"

        self.setup_logging()

        LoggingConfig._initialized = True  # 初期化済みフラグを設定

    def setup_logging(self) -> None:
        """
        ロギング設定をセットアップします。
        日単位でログファイルを作成します。
        """
        if not self.log_dir.exists():
            self.log_dir.mkdir(parents=True, exist_ok=True)

        # 日付を含んだログファイル名を作成
        today = datetime.now().strftime('%Y%m%d')
        log_file = self.log_dir / f"app_{today}.log"

        handlers = [
            # ファイルハンドラ - 日付入りのファイル名で保存
            logging.FileHandler(
                log_file, mode='a', encoding="utf-8"
            ),
            # 標準出力ハンドラ
            logging.StreamHandler(),
        ]

        logging.basicConfig(
            level=self.log_level,
            format=self.log_format,
            handlers=handlers,
        )

        logging.getLogger().info(f"Logging setup complete. Log file: {log_file}")
        logging.getLogger().info(f"Log level: {logging.getLevelName(self.log_level)}")


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    名前付きロガーを取得します。

    Args:
        name (Optional[str]): ロガー名

    Returns:
        logging.Logger: 名前付きロガー
    """
    LoggingConfig()
    return logging.getLogger(name)