#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
エラーケースとエッジケースでのページ解析テスト

難しいシナリオでのブラウザ動作をテストします:
- 存在しないページや無効なURLへのアクセス
- タイムアウトや読み込みエラー
- 複雑なDOM構造や動的コンテンツ
- エラーページやリダイレクト
"""

import pytest
import time
import logging
import requests
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from src.utils.environment import env
from src.utils.logging_config import get_logger
from src.modules.selenium.browser import Browser

# ロガーの設定
logger = get_logger(__name__)

class TestErrorHandling:
    """エラーケースとエッジケースのテスト"""
    
    @pytest.fixture(scope="function")
    def browser(self):
        """
        Browserインスタンスのフィクスチャ
        各テストごとに新しいブラウザインスタンスを作成
        """
        # 環境変数と設定の読み込み
        env.load_env()
        
        # Browserインスタンスの作成（短いタイムアウトでエラーケースをテスト）
        browser = Browser(
            logger=logger,
            headless=env.get_config_value("BROWSER", "headless", "true").lower() == "true",
            timeout=int(env.get_config_value("BROWSER", "error_test_timeout", "5"))
        )
        
        # ブラウザの初期化
        if not browser.setup():
            pytest.fail("ブラウザの初期化に失敗しました")
        
        yield browser
        
        # テスト終了後にブラウザを閉じる
        browser.quit()
    
    def test_nonexistent_page(self, browser):
        """存在しないページへのアクセス時の挙動テスト"""
        # 存在しないURLに移動
        url = "https://thisdomaindoesnotexist.example.com"
        
        # DNSルックアップが失敗するURLなので、エラーが発生することを期待
        result = browser.navigate_to(url)
        
        # navigate_toはエラー時にFalseを返すはず
        assert result is False, "存在しないドメインへのアクセスが成功してしまいました"
        
        # スクリーンショットが保存されていることを確認（間接的に）
        logger.info("存在しないページへのアクセステスト完了")
    
    def test_invalid_protocol(self, browser):
        """無効なプロトコルの挙動テスト"""
        # 無効なプロトコルでのURLに移動を試みる
        url = "invalid://example.com"
        
        # エラーが発生することを期待
        result = browser.navigate_to(url)
        
        # navigate_toはエラー時にFalseを返すはず
        assert result is False, "無効なプロトコルでのアクセスが成功してしまいました"
        
        logger.info("無効なプロトコルテスト完了")
    
    def test_page_with_errors(self, browser):
        """JavaScriptエラーのあるページの挙動テスト"""
        # JavaScriptエラーを含むURLに移動
        url = "https://the-internet.herokuapp.com/javascript_error"
        
        # ページ自体は読み込まれるはず
        result = browser.navigate_to(url)
        assert result is True, "エラーページへのアクセスに失敗しました"
        
        # ページ解析を実行
        page_analysis = browser.analyze_page_content()
        
        # タイトルが取得できることを確認
        assert page_analysis['page_title'], "ページタイトルが取得できませんでした"
        
        # ページの状態を確認
        assert page_analysis['page_status']['ready_state'] == "complete", "ページの読み込みが完了していません"
        
        logger.info(f"JavaScriptエラーページの状態: {page_analysis['page_status']}")
        logger.info("JavaScriptエラーページテスト完了")
    
    def test_redirect_handling(self, browser):
        """リダイレクトの挙動テスト"""
        # リダイレクトするURLに移動
        url = "https://httpbin.org/redirect-to?url=https://example.com"
        
        # ページに移動
        result = browser.navigate_to(url)
        assert result is True, "リダイレクトページへのアクセスに失敗しました"
        
        # 最終的なURLがリダイレクト先であることを確認
        final_url = browser.driver.current_url
        assert "example.com" in final_url, f"リダイレクトが適切に処理されていません: {final_url}"
        
        logger.info(f"リダイレクト後のURL: {final_url}")
        logger.info("リダイレクトテスト完了")
    
    def test_slow_loading_page(self, browser):
        """読み込みの遅いページの挙動テスト"""
        # 読み込みが遅いページに移動
        url = "https://httpbin.org/delay/3"  # 3秒の遅延
        
        # タイムアウト時間を短く設定した場合、エラーになる可能性がある
        if int(env.get_config_value("BROWSER", "error_test_timeout", "5")) < 4:
            try:
                browser.navigate_to(url)
                # ページの読み込み完了を待機
                load_success = browser.wait_for_page_load(timeout=3)
                assert load_success is False, "タイムアウトが発生するはずでしたが、ページが読み込まれました"
            except TimeoutException:
                logger.info("期待通りのタイムアウトが発生しました")
        else:
            # タイムアウト時間が十分であれば、最終的には読み込みが完了するはず
            start_time = time.time()
            result = browser.navigate_to(url)
            load_time = time.time() - start_time
            
            assert result is True, "遅いページへのアクセスに失敗しました"
            assert load_time >= 3, f"予期せず早く読み込まれました: {load_time:.2f}秒"
            
            logger.info(f"遅いページの読み込み時間: {load_time:.2f}秒")
        
        logger.info("遅いページの読み込みテスト完了")
    
    def test_complex_dom_structure(self, browser):
        """複雑なDOM構造を持つページの解析テスト"""
        # 複雑なDOM構造を持つページに移動（例: GitHub）
        url = "https://github.com"
        
        # ページに移動
        result = browser.navigate_to(url)
        assert result is True, "複雑なDOM構造を持つページへのアクセスに失敗しました"
        
        # インタラクティブ要素の検出
        interactive = browser.find_interactive_elements()
        
        # 多数の要素が検出されているはず
        assert len(interactive['clickable']) > 20, "期待される数のクリック可能要素が検出されませんでした"
        
        # ページ解析のパフォーマンスを測定
        start_time = time.time()
        page_analysis = browser.analyze_page_content()
        analysis_time = time.time() - start_time
        
        logger.info(f"複雑なDOMの解析時間: {analysis_time:.2f}秒")
        logger.info(f"検出された要素数: ボタン={len(page_analysis['buttons'])}, リンク={len(page_analysis['links'])}, 入力={len(page_analysis['inputs'])}")
        
        # 解析がタイムアウトなどで失敗していないことを確認
        assert page_analysis['page_title'], "ページ解析に失敗しました"
        
        logger.info("複雑なDOM構造のテスト完了")
    
    def test_status_code_pages(self, browser):
        """HTTPステータスコードページの解析テスト"""
        # テスト対象のステータスコード
        status_codes = [404, 500]
        
        for code in status_codes:
            url = f"https://httpbin.org/status/{code}"
            
            # 事前にリクエストを送信して、HTTPステータスを確認
            try:
                response = requests.head(url, timeout=5)
                assert response.status_code == code, f"期待されるステータスコード {code} ではなく {response.status_code} が返されました"
            except requests.RequestException as e:
                logger.warning(f"HTTP事前チェック中にエラーが発生しました: {str(e)}")
            
            # ブラウザでアクセス
            try:
                browser.navigate_to(url)
                
                # ページ解析を実行
                page_analysis = browser.analyze_page_content()
                
                # エラーページの特徴を探す
                error_text = browser.find_element_by_text(str(code), case_sensitive=False)
                error_found = len(error_text) > 0
                
                logger.info(f"ステータスコード {code} ページ: エラーテキスト検出 = {error_found}")
                
            except WebDriverException as e:
                logger.info(f"ステータスコード {code} ページアクセス中にブラウザエラーが発生しました: {str(e)}")
        
        logger.info("HTTPステータスコードページテスト完了")
    
    def test_alert_and_confirm_dialogs(self, browser):
        """アラートとダイアログの処理テスト"""
        # アラートが含まれるページに移動
        url = "https://the-internet.herokuapp.com/javascript_alerts"
        
        # ページに移動
        result = browser.navigate_to(url)
        assert result is True, "アラートページへのアクセスに失敗しました"
        
        # アラート表示ボタンを探す
        alert_buttons = browser.find_element_by_text("Click for JS Alert", case_sensitive=False)
        
        if alert_buttons:
            # アラートボタンをクリック
            alert_buttons[0]['element'].click()
            
            # アラート情報を取得
            alert_info = browser._check_alerts()
            
            # アラートの存在を確認
            assert alert_info['present'], "アラートが検出されませんでした"
            logger.info(f"アラートテキスト: {alert_info['text']}")
            
            # アラートを処理
            try:
                alert = browser.driver.switch_to.alert
                alert.accept()
                logger.info("アラートを承認しました")
            except Exception as e:
                logger.error(f"アラート処理中にエラーが発生しました: {str(e)}")
        
        # 確認ダイアログを探す
        confirm_buttons = browser.find_element_by_text("Click for JS Confirm", case_sensitive=False)
        
        if confirm_buttons:
            # 確認ボタンをクリック
            confirm_buttons[0]['element'].click()
            
            # ダイアログ情報を取得
            dialog_info = browser._check_alerts()
            
            # ダイアログの存在を確認
            assert dialog_info['present'], "確認ダイアログが検出されませんでした"
            assert dialog_info['type'] == 'confirm', f"ダイアログタイプが正しくありません: {dialog_info['type']}"
            
            logger.info(f"確認ダイアログタイプ: {dialog_info['type']}")
            
            # ダイアログを処理（拒否）
            try:
                alert = browser.driver.switch_to.alert
                alert.dismiss()
                logger.info("確認ダイアログを拒否しました")
            except Exception as e:
                logger.error(f"ダイアログ処理中にエラーが発生しました: {str(e)}")
        
        logger.info("アラートとダイアログのテスト完了")
    
    def test_dynamic_content_page(self, browser):
        """動的コンテンツを持つページの解析テスト"""
        # 動的に変化するコンテンツを持つページに移動
        url = "https://the-internet.herokuapp.com/dynamic_content"
        
        # ページに移動
        result = browser.navigate_to(url)
        assert result is True, "動的コンテンツページへのアクセスに失敗しました"
        
        # 初期状態のコンテンツを取得
        initial_content = browser.get_page_source()
        
        # ページをリロードして動的コンテンツを変更
        browser.driver.refresh()
        browser.wait_for_page_load()
        
        # 新しい状態のコンテンツを取得
        new_content = browser.get_page_source()
        
        # コンテンツが変化していることを確認
        assert initial_content != new_content, "ページのリロード後も動的コンテンツが変化していません"
        
        # 変化を検出できることを確認
        page_changed = browser.detect_page_changes(wait_seconds=1)
        logger.info(f"ページ変化検出: {page_changed}")
        
        logger.info("動的コンテンツページのテスト完了")
    
    def test_iframe_content(self, browser):
        """iframeを含むページの解析テスト"""
        # iframeを含むページに移動
        url = "https://the-internet.herokuapp.com/iframe"
        
        # ページに移動
        result = browser.navigate_to(url)
        assert result is True, "iframeページへのアクセスに失敗しました"
        
        # ページ解析を実行
        page_analysis = browser.analyze_page_content()
        
        # iframeの検出を確認
        iframe_elements = browser.driver.find_elements(By.TAG_NAME, "iframe")
        assert len(iframe_elements) > 0, "iframeが検出されませんでした"
        
        try:
            # 最初のiframeに切り替え
            browser.driver.switch_to.frame(iframe_elements[0])
            
            # iframe内の要素を検索
            editor_element = browser.driver.find_element(By.ID, "tinymce")
            assert editor_element, "iframe内のエディタ要素が見つかりませんでした"
            
            # iframe内のテキストを取得
            editor_text = editor_element.text
            logger.info(f"iframe内のエディタテキスト: {editor_text}")
            
            # 元のフレームに戻る
            browser.driver.switch_to.default_content()
            
            logger.info("iframeコンテンツにアクセスできました")
        except Exception as e:
            browser.driver.switch_to.default_content()  # 元のフレームに戻る
            logger.error(f"iframe処理中にエラーが発生しました: {str(e)}")
            pytest.fail(f"iframe処理中にエラーが発生しました: {str(e)}")
        
        logger.info("iframeテスト完了")
    
    def test_secure_connection(self, browser):
        """セキュアな接続とプライバシーエラーのテスト"""
        # HTTPSとHTTPサイトへのアクセス
        secure_url = "https://example.com"
        insecure_url = "http://example.com"  # 多くのブラウザで警告が表示される
        
        # セキュアなサイトにアクセス
        browser.navigate_to(secure_url)
        secure_protocol = urlparse(browser.driver.current_url).scheme
        
        # HTTPSにリダイレクトされているはず
        assert secure_protocol == "https", f"セキュアなプロトコルにリダイレクトされていません: {secure_protocol}"
        logger.info(f"セキュアな接続: {browser.driver.current_url}")
        
        # 非セキュアなサイトにアクセス（自動リダイレクトされる可能性あり）
        browser.navigate_to(insecure_url)
        current_protocol = urlparse(browser.driver.current_url).scheme
        
        # 多くのサイトは自動的にHTTPSにリダイレクトされる
        logger.info(f"非セキュアURLへのアクセス後のプロトコル: {current_protocol}")
        
        logger.info("セキュア接続テスト完了") 