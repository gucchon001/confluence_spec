#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git一括管理ツール (Python実装)

複数のGitリポジトリに対して一括操作を行うPythonモジュール
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

# 設定管理とロギングのインポート
try:
    from src.utils.environment import env
    from src.utils.logging_config import get_logger
except ImportError:
    # 直接実行時のフォールバック
    import logging
    env = None
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# ロガー設定
logger = get_logger(__name__)


class GitCommand:
    """Git操作の基本クラス"""
    
    def __init__(self, repo_path: str, options: Dict[str, Any] = None):
        """
        コンストラクタ
        
        Args:
            repo_path: Gitリポジトリのパス
            options: コマンドオプション
        """
        self.repo_path = Path(repo_path)
        self.options = options or {}
        
        # リポジトリの存在確認
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"有効なGitリポジトリではありません: {repo_path}")
    
    def _run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """
        Gitコマンドを実行
        
        Args:
            command: 実行するコマンドとその引数のリスト
        
        Returns:
            実行結果
        """
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                check=True,
                text=True,
                capture_output=True
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"コマンド実行エラー: {e.stderr.strip()}")
            raise
    
    def execute(self) -> Dict[str, Any]:
        """
        コマンドを実行する抽象メソッド
        
        Returns:
            実行結果の辞書
        """
        raise NotImplementedError("サブクラスで実装する必要があります")


class GitStatus(GitCommand):
    """リポジトリのステータスを表示"""
    
    def execute(self) -> Dict[str, Any]:
        """
        git statusを実行
        
        Returns:
            実行結果
        """
        command = ['git', 'status', '--short']
        result = self._run_command(command)
        return {
            'success': result.returncode == 0,
            'output': result.stdout.strip(),
            'command': ' '.join(command)
        }


class GitPull(GitCommand):
    """リモートリポジトリからプルする"""
    
    def execute(self) -> Dict[str, Any]:
        """
        git pullを実行
        
        Returns:
            実行結果
        """
        branch = self.options.get('branch', '')
        command = ['git', 'pull']
        if branch:
            command.extend(['origin', branch])
        
        result = self._run_command(command)
        return {
            'success': result.returncode == 0,
            'output': result.stdout.strip(),
            'command': ' '.join(command)
        }


class GitForcePull(GitCommand):
    """リモートリポジトリから強制的にプルする"""
    
    def execute(self) -> Dict[str, Any]:
        """
        git fetch と git reset --hard origin/<branch> を実行して強制的にリモートの状態に合わせる
        
        Returns:
            実行結果
        """
        branch = self.options.get('branch', '')
        if not branch:
            # カレントブランチを取得
            try:
                branch_result = self._run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
                branch = branch_result.stdout.strip()
            except Exception as e:
                return {
                    'success': False,
                    'error': f"カレントブランチの取得に失敗しました: {str(e)}",
                    'command': 'git rev-parse --abbrev-ref HEAD'
                }
        
        # まずはfetchを実行
        try:
            fetch_result = self._run_command(['git', 'fetch', 'origin'])
        except Exception as e:
            return {
                'success': False,
                'error': f"fetchに失敗しました: {str(e)}",
                'command': 'git fetch origin'
            }
        
        # ローカルの変更を保存するかどうか
        try_stash = self.options.get('try_stash', True)
        
        if try_stash:
            # ローカルの変更を一時保存
            try:
                stash_result = self._run_command(['git', 'stash', 'save', f"自動保存 {time.strftime('%Y-%m-%d %H:%M:%S')}"])
                stashed = "No local changes to save" not in stash_result.stdout
            except Exception:
                stashed = False
        
        # 強制的にリモートの状態にリセット
        try:
            reset_result = self._run_command(['git', 'reset', '--hard', f"origin/{branch}"])
            
            result = {
                'success': reset_result.returncode == 0,
                'output': f"強制的にリセットしました: {reset_result.stdout.strip()}",
                'command': f"git reset --hard origin/{branch}"
            }
            
            # stashした場合は、変更を戻す試み
            if try_stash and stashed:
                try:
                    self._run_command(['git', 'stash', 'pop'])
                    result['output'] += "\n保存した変更を復元しました。"
                except Exception as e:
                    result['output'] += f"\n保存した変更の復元に失敗しました: {str(e)}"
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f"リセットに失敗しました: {str(e)}",
                'command': f"git reset --hard origin/{branch}"
            }


class GitPush(GitCommand):
    """リモートリポジトリにプッシュする"""
    
    def execute(self) -> Dict[str, Any]:
        """
        git pushを実行
        
        Returns:
            実行結果
        """
        branch = self.options.get('branch', '')
        command = ['git', 'push']
        if branch:
            command.extend(['origin', branch])
        
        result = self._run_command(command)
        return {
            'success': result.returncode == 0,
            'output': result.stdout.strip(),
            'command': ' '.join(command)
        }


class GitFullPush(GitCommand):
    """変更をadd, commit, pushまで一気に実行する"""
    
    def execute(self) -> Dict[str, Any]:
        """
        git add, git commit, git pushを連続して実行
        
        Returns:
            実行結果
        """
        # 変更があるか確認
        status_result = self._run_command(['git', 'status', '--porcelain'])
        if not status_result.stdout.strip():
            return {
                'success': True,
                'output': "変更はありません。プッシュするものがありません。",
                'command': 'git status'
            }
        
        # 変更をステージングエリアに追加
        try:
            add_result = self._run_command(['git', 'add', '--all'])
        except Exception as e:
            return {
                'success': False,
                'error': f"変更の追加に失敗しました: {str(e)}",
                'command': 'git add --all'
            }
        
        # コミット実行
        commit_message = self.options.get('message', f"自動コミット {time.strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            commit_result = self._run_command(['git', 'commit', '-m', commit_message])
        except Exception as e:
            return {
                'success': False,
                'error': f"コミットに失敗しました: {str(e)}",
                'command': f"git commit -m '{commit_message}'"
            }
        
        # プッシュ実行
        branch = self.options.get('branch', '')
        push_command = ['git', 'push']
        if branch:
            push_command.extend(['origin', branch])
        
        try:
            push_result = self._run_command(push_command)
            
            return {
                'success': True,
                'output': f"変更を追加、コミット、プッシュしました。\nコミットメッセージ: {commit_message}\n{push_result.stdout.strip()}",
                'command': ' '.join(push_command)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"プッシュに失敗しました: {str(e)}",
                'command': ' '.join(push_command)
            }


class GitCommit(GitCommand):
    """変更をコミットする"""
    
    def execute(self) -> Dict[str, Any]:
        """
        git addとgit commitを実行
        
        Returns:
            実行結果
        """
        message = self.options.get('message', 'Auto commit by batch tool')
        
        # 変更を全て追加
        add_result = self._run_command(['git', 'add', '--all'])
        
        # 変更があるか確認
        status_result = self._run_command(['git', 'status', '--porcelain'])
        if not status_result.stdout.strip():
            return {
                'success': True,
                'output': 'コミットする変更はありません',
                'command': 'git status'
            }
        
        commit_result = self._run_command(['git', 'commit', '-m', message])
        return {
            'success': commit_result.returncode == 0,
            'output': commit_result.stdout.strip(),
            'command': f'git commit -m "{message}"'
        }


class GitCheckout(GitCommand):
    """指定されたブランチにチェックアウトする"""
    
    def execute(self) -> Dict[str, Any]:
        """
        git checkoutを実行
        
        Returns:
            実行結果
        """
        branch = self.options.get('branch', '')
        if not branch:
            raise ValueError("ブランチ名が指定されていません")
        
        command = ['git', 'checkout', branch]
        result = self._run_command(command)
        return {
            'success': result.returncode == 0,
            'output': result.stdout.strip(),
            'command': ' '.join(command)
        }


class GitReset(GitCommand):
    """変更をリセットする"""
    
    def execute(self) -> Dict[str, Any]:
        """
        git reset --hardを実行
        
        Returns:
            実行結果
        """
        command = ['git', 'reset', '--hard', 'HEAD']
        result = self._run_command(command)
        return {
            'success': result.returncode == 0,
            'output': result.stdout.strip(),
            'command': ' '.join(command)
        }


class GitClean(GitCommand):
    """追跡されていないファイルを削除する"""
    
    def execute(self) -> Dict[str, Any]:
        """
        git cleanを実行
        
        Returns:
            実行結果
        """
        command = ['git', 'clean', '-fd']
        result = self._run_command(command)
        return {
            'success': result.returncode == 0,
            'output': result.stdout.strip(),
            'command': ' '.join(command)
        }


class GitBatchProcessor:
    """複数リポジトリに対するGitバッチ処理"""
    
    def __init__(self, repos: List[str], options: Dict[str, Any] = None):
        """
        コンストラクタ
        
        Args:
            repos: 処理対象のリポジトリパスのリスト
            options: 全リポジトリ共通のオプション
        """
        self.repos = repos
        self.options = options or {}
        self.results = {}
        
        # コマンドクラスのマッピング
        self.command_classes = {
            'status': GitStatus,
            'pull': GitPull,
            'force-pull': GitForcePull,
            'push': GitPush,
            'full-push': GitFullPush,
            'commit': GitCommit,
            'checkout': GitCheckout,
            'reset': GitReset,
            'clean': GitClean
        }
    
    def execute_batch(self, command_name: str) -> Dict[str, Any]:
        """
        全リポジトリに対して指定されたコマンドを実行
        
        Args:
            command_name: 実行するコマンド名
        
        Returns:
            リポジトリごとの実行結果
        """
        if command_name not in self.command_classes:
            raise ValueError(f"不明なコマンド: {command_name}")
        
        command_class = self.command_classes[command_name]
        results = {}
        
        for repo in self.repos:
            repo_name = Path(repo).name
            logger.info(f"リポジトリ処理開始: {repo_name}")
            
            try:
                command = command_class(repo, self.options)
                result = command.execute()
                results[repo_name] = result
                logger.info(f"結果: {result['output']}")
            except Exception as e:
                logger.error(f"エラー発生: {str(e)}")
                results[repo_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        self.results.update(results)
        return results
    
    def summary(self) -> Dict[str, int]:
        """
        実行結果のサマリーを取得
        
        Returns:
            成功/失敗数のサマリー
        """
        success_count = sum(1 for result in self.results.values() if result.get('success', False))
        return {
            'total': len(self.results),
            'success': success_count,
            'failure': len(self.results) - success_count
        }


def find_git_repos(base_dir: str, max_depth: int = 2, recursive: bool = False) -> List[str]:
    """
    指定ディレクトリ以下のGitリポジトリを探索
    
    Args:
        base_dir: 探索開始ディレクトリ
        max_depth: 最大探索深度
        recursive: 再帰的に探索するかどうか
    
    Returns:
        見つかったGitリポジトリのパスのリスト
    """
    base_path = Path(base_dir)
    repos = []
    
    # カレントディレクトリがGitリポジトリかチェック
    if (base_path / ".git").exists():
        repos.append(str(base_path))
        return repos if not recursive else repos + _find_git_repos_recursive(base_path, 1, max_depth)
    elif recursive:
        return _find_git_repos_recursive(base_path, 0, max_depth)
    
    return repos


def _find_git_repos_recursive(path: Path, current_depth: int, max_depth: int) -> List[str]:
    """
    再帰的にGitリポジトリを探索する補助関数
    
    Args:
        path: 探索パス
        current_depth: 現在の深度
        max_depth: 最大深度
    
    Returns:
        見つかったGitリポジトリのパスのリスト
    """
    if current_depth > max_depth:
        return []
    
    repos = []
    for item in path.iterdir():
        if not item.is_dir():
            continue
        
        if (item / ".git").exists():
            repos.append(str(item))
        else:
            repos.extend(_find_git_repos_recursive(item, current_depth + 1, max_depth))
    
    return repos


def execute_git_command(command: str, **kwargs) -> Dict[str, Any]:
    """
    Git操作を実行する便利関数
    
    Args:
        command: 実行するコマンド (status, pull, push, commit, checkout, reset, clean)
        **kwargs: コマンドのオプション
            - path: 処理対象のディレクトリパス (デフォルト: カレントディレクトリ)
            - branch: ブランチ名 (checkout, pullコマンド用)
            - message: コミットメッセージ (commitコマンド用)
            - recursive: サブディレクトリも再帰的に検索するかどうか (デフォルト: False)
            - depth: 再帰検索時の最大深度 (デフォルト: 2)
    
    Returns:
        実行結果の辞書
    """
    # 設定値の取得
    path = kwargs.get('path', '.')
    branch = kwargs.get('branch', None)
    message = kwargs.get('message', None)
    recursive = kwargs.get('recursive', False)
    depth = kwargs.get('depth', 2)
    
    # Git設定の取得（設定ファイルからの読み込み）
    if env:
        # デフォルト値を設定ファイルから取得
        if not branch:
            branch = env.get_config_value("GIT", "default_branch", None)
        auto_add = env.get_config_value("GIT", "auto_add", "true").lower() == "true"
    else:
        auto_add = True
    
    # オプションの設定
    options = {}
    if branch:
        options['branch'] = branch
    if message:
        options['message'] = message
    if auto_add:
        options['auto_add'] = auto_add
    
    # 対象リポジトリを探索
    logger.info(f"リポジトリ探索開始: {path}")
    repos = find_git_repos(path, depth, recursive)
    
    if not repos:
        logger.error("Gitリポジトリが見つかりませんでした。")
        return {
            'success': False,
            'error': 'リポジトリが見つかりませんでした'
        }
    
    logger.info(f"{len(repos)}個のリポジトリが見つかりました:")
    for repo in repos:
        logger.info(f"- {repo}")
    
    # バッチ処理実行
    processor = GitBatchProcessor(repos, options)
    
    try:
        logger.info(f"コマンド実行開始: {command}")
        results = processor.execute_batch(command)
        
        # 結果サマリー
        summary = processor.summary()
        logger.info(f"処理完了: 合計={summary['total']}, 成功={summary['success']}, 失敗={summary['failure']}")
        
        return {
            'success': summary['failure'] == 0,
            'summary': summary,
            'results': results
        }
    except Exception as e:
        logger.error(f"実行中にエラーが発生しました: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def parse_args():
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(description='Git一括処理ツール')
    
    parser.add_argument('command', choices=['status', 'pull', 'force-pull', 'push', 'full-push', 'commit', 'checkout', 'reset', 'clean'],
                        help='実行するGitコマンド')
    parser.add_argument('--path', default='.', help='処理対象の基底ディレクトリ')
    parser.add_argument('--branch', help='対象ブランチ（checkout, pullコマンド用）')
    parser.add_argument('--message', '-m', help='コミットメッセージ（commitコマンド用）')
    parser.add_argument('--recursive', action='store_true', help='サブディレクトリも再帰的に検索')
    parser.add_argument('--depth', type=int, default=2, help='再帰検索時の最大深度')
    parser.add_argument('--no-stash', action='store_true', help='force-pull時にstashを試みない')
    
    return parser.parse_args()


def main():
    """メイン関数"""
    args = parse_args()
    
    # 対象リポジトリを探索
    logger.info(f"リポジトリ探索開始: {args.path}")
    repos = find_git_repos(args.path, args.depth, args.recursive)
    
    if not repos:
        logger.error("Gitリポジトリが見つかりませんでした。")
        return 1
    
    logger.info(f"{len(repos)}個のリポジトリが見つかりました:")
    for repo in repos:
        logger.info(f"- {repo}")
    
    # オプションの設定
    options = {}
    if args.branch:
        options['branch'] = args.branch
    if args.message:
        options['message'] = args.message
    if args.no_stash:
        options['try_stash'] = False
    
    # バッチ処理実行
    result = execute_git_command(
        args.command,
        path=args.path,
        branch=args.branch,
        message=args.message,
        recursive=args.recursive,
        depth=args.depth
    )
    
    if result['success']:
        sys.exit(0)
    else:
        sys.exit(1)


# スクリプトとして直接実行された場合のエントリーポイント
if __name__ == "__main__":
    main() 