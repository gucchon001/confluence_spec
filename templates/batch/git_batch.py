#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Git一括管理ツール (Python実装)

複数のGitリポジトリに対して一括操作を行うPythonスクリプト
"""

import os
import sys
import time
import logging
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

# ロガー設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


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
            'push': GitPush,
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


def parse_args():
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(description='Git一括処理ツール')
    
    parser.add_argument('command', choices=['status', 'pull', 'push', 'commit', 'checkout', 'reset', 'clean'],
                        help='実行するGitコマンド')
    parser.add_argument('--path', default='.', help='処理対象の基底ディレクトリ')
    parser.add_argument('--branch', help='対象ブランチ（checkout, pullコマンド用）')
    parser.add_argument('--message', '-m', help='コミットメッセージ（commitコマンド用）')
    parser.add_argument('--recursive', action='store_true', help='サブディレクトリも再帰的に検索')
    parser.add_argument('--depth', type=int, default=2, help='再帰検索時の最大深度')
    
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
    
    # バッチ処理実行
    processor = GitBatchProcessor(repos, options)
    
    try:
        logger.info(f"コマンド実行開始: {args.command}")
        processor.execute_batch(args.command)
        
        # 結果サマリー表示
        summary = processor.summary()
        logger.info(f"処理完了: 合計={summary['total']}, 成功={summary['success']}, 失敗={summary['failure']}")
        
        return 0 if summary['failure'] == 0 else 1
    except Exception as e:
        logger.error(f"実行中にエラーが発生しました: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 