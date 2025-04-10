# プロジェクト生成スクリプト

このフォルダには、新しいPythonプロジェクトを生成するためのテンプレートとスクリプトが含まれています。

## ディレクトリ構造

```
99_create_project/
├── create_project.bat          # プロジェクト生成スクリプト
├── templates/                  # テンプレートファイル
│   ├── README.md               # プロジェクトREADMEテンプレート
│   ├── python/                 # Pythonソースコードテンプレート
│   │   ├── environment_template.py
│   │   ├── logging_config_template.py
│   │   ├── main_template.py
│   │   └── utils/              # ユーティリティスクリプト
│   │       ├── git_batch.py    # Git一括操作モジュール
│   │       └── openai_git_helper.py # OpenAI API連携Git支援モジュール
│   ├── tests/                  # テストコードテンプレート
│   └── batch/                  # バッチファイルテンプレート
│       ├── run.bat             # 基本実行用バッチファイル
│       ├── run_dev.bat         # 開発環境用高機能バッチファイル
│       ├── update_libraries.bat # ライブラリアップデート用バッチファイル
│       └── run_git_ai.bat      # AI支援Git操作バッチファイル
```

## 使用方法

1. `create_project.bat` を実行してプロジェクトの基本構造を生成します。
2. 生成されたプロジェクトの中で `run.bat` または `run_dev.bat` を実行して環境を設定し、アプリケーションを起動します。
3. ライブラリを最新版にアップデートする場合は `update_libraries.bat` を実行します。
4. Git操作を一括で行う場合や、AI支援機能を使用するには `run_git_ai.bat` を実行します。

## 生成されるプロジェクト構造

```
project_name/
├── README.md                 # プロジェクト概要と使い方
├── src/
│   ├── __init__.py           # Pythonパッケージ化
│   ├── main.py               # プログラムのエントリーポイント
│   ├── utils/
│   │   ├── __init__.py       # Pythonパッケージ化
│   │   ├── environment.py    # 設定管理
│   │   ├── logging_config.py # ログ設定
│   │   ├── git_batch.py      # Git一括操作モジュール
│   │   └── openai_git_helper.py # OpenAI API連携Git支援モジュール
│   └── modules/
│       ├── __init__.py       # Pythonパッケージ化
│       └── module1.py        # サンプルモジュール
├── tests/
│   ├── __init__.py           # テストパッケージ化
├── logs/
│   ├── .gitkeep              # 空ディレクトリをGitで追跡
├── docs/
│   ├── .gitkeep              # 空ディレクトリをGitで追跡
├── config/
│   ├── settings.ini          # 環境設定
│   └── secrets.env           # 機密情報 (例: APIキー、OpenAI APIキー)
├── data/
│   ├── .gitkeep              # 空ディレクトリをGitで追跡
├── requirements.txt          # 必要なパッケージ
├── run.bat                   # 基本実行用バッチファイル
├── run_dev.bat               # 開発環境用高機能バッチファイル
├── update_libraries.bat      # ライブラリアップデート用バッチファイル
└── run_git_ai.bat            # AI支援Git操作バッチファイル
```

## 実行スクリプトの違い

プロジェクトには複数の実行スクリプトが含まれています：

### run.bat
- 基本的な実行機能を提供
- 仮想環境のアクティブ化と指定されたスクリプトの実行
- ファイルパスとして直接スクリプトを実行（例：`src\main.py`）
- シンプルで軽量な実行環境が必要な場合に使用

### run_dev.bat
- 開発時に便利な高度な機能を提供
- Pythonモジュールとしてスクリプトを実行（`-m` オプション使用、例：`src.main`）
- 環境選択機能（development/production）
- requirements.txtの変更検知と自動パッケージインストール
- テストモードの自動設定（development環境選択時）
- 開発作業やテスト実行時に推奨

### update_libraries.bat
- ライブラリの更新に特化したスクリプト
- 仮想環境が存在しない場合は自動作成
- pip 自体を最新バージョンにアップグレード
- requirements.txt に記載されたすべてのライブラリを最新バージョンにアップデート
- インストール済みパッケージの一覧表示
- ライブラリの依存関係を最新の状態に保ちたい場合に使用

### run_git_ai.bat
- Git操作をAI支援機能で強化するスクリプト
- 複数のGitリポジトリに対する一括操作機能
- OpenAI APIを使用した高度なGit支援機能
- 対話式メニューで操作を選択可能
- 自動化されたGitワークフロー機能

## Git操作と支援機能

本プロジェクトには、以下のGit一括操作と支援機能が含まれています：

### 標準Git操作
- **status**: 全リポジトリの状態を表示
- **pull**: 全リポジトリの変更を取得
- **push**: 全リポジトリの変更をプッシュ
- **commit**: 全リポジトリの変更をコミット
- **checkout**: 全リポジトリで指定ブランチに切り替え
- **reset**: 全リポジトリの変更をリセット
- **clean**: 全リポジトリの追跡されていないファイルを削除
- **full-push**: 変更のadd, commit, pushを一回の操作で実行

### AI強化Git機能
- **ai-commit**: 変更内容からコミットメッセージを自動生成
- **ai-full-push**: 変更をステージング、AI生成メッセージでコミット、プッシュまで一括実行（ブランチ戦略のヒント付き）
- **analyze-pr**: プルリクエストを分析して要約を提供
- **analyze-code**: 指定したファイルのコード品質を分析
- **suggest-implementation**: 新機能の実装案を提案
- **check-sensitive-info**: プッシュ前に機密情報の漏洩をチェック

## 設定

### OpenAI API設定 (config/secrets.env)
```
OPENAI_API_KEY=your_api_key_here
```

### Git設定 (config/settings.ini)
```ini
[GIT]
use_openai=true
default_branch=main
auto_add=true

[OPENAI]
model=gpt-3.5-turbo
```

## 注意事項

- プロジェクト名には英数字、ハイフン、アンダースコアのみ使用可能です。
- 既存のプロジェクト名と重複する場合はエラーとなります。
- `secrets.env` には機密情報が含まれるため、`.gitignore` に追加されています。
- プロジェクトを生成するには `create_project.bat` を管理者権限で実行することを推奨します。
- `src/` および `tests/` ディレクトリには `__init__.py` ファイルが自動生成され、Pythonパッケージとして認識されます。
- AI支援機能を使用するには、OpenAI APIのキーが必要です。

## サポート情報

- 問題や提案がある場合は、担当者までご連絡ください。
