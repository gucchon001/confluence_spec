# tests/conftest.py

import os
import sys
import pytest
from pathlib import Path

# プロジェクトルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# src ディレクトリをPYTHONPATHに追加
src_path = project_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# 便宜上、テスト用に環境変数を設定
os.environ["APP_ENV"] = os.environ.get("APP_ENV", "development")

# テスト用のフィクスチャとして env を提供
@pytest.fixture(scope="session")
def environment():
    """環境設定を提供するフィクスチャ"""
    from src.utils.environment import env
    return env
