
# プロジェクト生成スクリプト

このフォルダには、新しいPythonプロジェクトを生成するためのテンプレートとスクリプトが含まれています。

## ディレクトリ構造

```
99_create_project/
├── create_project.bat          # プロジェクト生成スクリプト
├── templates/                  # テンプレートファイル
│   ├── README.md               # プロジェクトREADMEテンプレート
│   ├── python/                 # Pythonソースコードテンプレート
│   │   ├── config_template.py
│   │   ├── logging_config_template.py
│   │   └── main_template.py
│   ├── spec_tools/             # 仕様書生成ツールテンプレート
│   │   ├── merge_files.py
│   │   ├── generate_spec.py
│   │   ├── generate_detailed_spec.py
│   │   └── utils.py
│   └── batch/                  # バッチファイルテンプレート
│       ├── run.bat
│       └── spec_tools_run.bat
```

## 使用方法

1. `create_project.bat` を実行してプロジェクトの基本構造を生成します。
2. 生成されたプロジェクトの中で `run.bat` を実行して環境を設定し、アプリケーションを起動します。
3. 必要に応じて `spec_tools_run.bat` を使用し、仕様書生成ツールを実行します。

## 生成されるプロジェクト構造

```
project_name/
├── README.md                 # プロジェクト概要と使い方
├── src/
│   ├── main.py               # プログラムのエントリーポイント
│   ├── utils/
│   │   ├── environment.py         # 設定管理
│   │   └── logging_config.py # ログ設定
│   └── modules/
│       └── module1.py        # サンプルモジュール
├── tests/
│   ├── __init__.py           # テストモジュール
├── logs/
│   ├── .gitkeep              # 空ディレクトリをGitで追跡
├── docs/
│   ├── .gitkeep              # 空ディレクトリをGitで追跡
├── config/
│   ├── settings.ini          # 環境設定
│   └── secrets.env           # 機密情報 (例: APIキー)
├── data/
│   ├── .gitkeep              # 空ディレクトリをGitで追跡
├── spec_tools/
│   ├── merge_files.py
│   ├── generate_spec.py
│   ├── generate_detailed_spec.py
│   ├── utils.py
│   └── logs/
│       └── .gitkeep
├── requirements.txt          # 必要なパッケージ
├── run.bat                   # 実行用バッチファイル
└── spec_tools_run.bat        # 仕様書生成用バッチファイル
```

## 注意事項

- プロジェクト名には英数字、ハイフン、アンダースコアのみ使用可能です。
- 既存のプロジェクト名と重複する場合はエラーとなります。
- `secrets.env` には機密情報が含まれるため、`.gitignore` に追加されています。
- プロジェクトを生成するには `create_project.bat` を管理者権限で実行することを推奨します。

## サポート情報

- 問題や提案がある場合は、担当者までご連絡ください。
