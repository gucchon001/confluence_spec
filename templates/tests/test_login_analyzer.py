#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ログインページの解析と自動検証テスト

ログインフォームの自動検出、エラーメッセージの検証、セキュリティ要素の確認などを行います。
"""

import pytest
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.utils.environment import env
from src.utils.logging_config import get_logger
from src.modules.selenium.browser import Browser
from src.modules.selenium.login_page import LoginPage

# ロガーの設定
logger = get_logger(__name__)

class TestLoginAnalyzer:
    """ログインページの解析と自動検証テスト"""
    
    @pytest.fixture(scope="class")
    def browser(self):
        """Browserインスタンスのフィクスチャ"""
        # 環境変数と設定の読み込み
        env.load_env()
        
        # Browserインスタンスの作成
        browser = Browser(
            logger=logger,
            headless=env.get_config_value("BROWSER", "headless", "false").lower() == "true",
            timeout=int(env.get_config_value("BROWSER", "timeout", "10"))
        )
        
        # ブラウザの初期化
        if not browser.setup():
            pytest.fail("ブラウザの初期化に失敗しました")
        
        yield browser
        
        # テスト終了後にブラウザを閉じる
        browser.quit()
    
    @pytest.fixture
    def login_page(self, browser):
        """LoginPageインスタンスのフィクスチャ"""
        # LoginPageインスタンスの作成
        login_page = LoginPage(
            browser=browser,
            logger=logger
        )
        return login_page
    
    @pytest.fixture
    def demo_login_url(self):
        """テスト用ログインページのURL"""
        # デモサイトのログインページURLを返す
        return "https://practicetestautomation.com/practice-test-login/"
    
    def test_login_form_detection(self, browser, demo_login_url):
        """ログインフォームの自動検出テスト"""
        # テスト用ログインページに移動
        browser.navigate_to(demo_login_url)
        
        # ページ解析を実行
        page_analysis = browser.analyze_page_content(element_filter={'forms': True, 'inputs': True, 'buttons': True})
        
        # フォームの存在を確認
        assert len(page_analysis['forms']) > 0, "ログインフォームが検出されませんでした"
        
        # ユーザー名/メールアドレス入力欄の検出
        username_inputs = [
            inp for inp in page_analysis['inputs'] 
            if any(keyword in inp['name'].lower() or keyword in inp.get('id', '').lower() 
                  for keyword in ['user', 'email', 'login', 'name'])
        ]
        
        # パスワード入力欄の検出
        password_inputs = [
            inp for inp in page_analysis['inputs'] 
            if 'password' in inp['name'].lower() or 'password' in inp.get('id', '').lower() or inp['type'] == 'password'
        ]
        
        # ログインボタンの検出
        login_buttons = [
            btn for btn in page_analysis['buttons'] 
            if any(keyword in btn['text'].lower() or keyword in btn.get('id', '').lower() 
                  for keyword in ['login', 'signin', 'submit', 'ログイン'])
        ]
        
        # 各要素が検出されていることを確認
        assert len(username_inputs) > 0, "ユーザー名/メールアドレス入力欄が検出されませんでした"
        assert len(password_inputs) > 0, "パスワード入力欄が検出されませんでした"
        assert len(login_buttons) > 0, "ログインボタンが検出されませんでした"
        
        # 検出された要素の情報をログに出力
        logger.info(f"検出されたユーザー名入力欄: {username_inputs[0]['name']} (タイプ: {username_inputs[0]['type']})")
        logger.info(f"検出されたパスワード入力欄: {password_inputs[0]['name']} (タイプ: {password_inputs[0]['type']})")
        logger.info(f"検出されたログインボタン: {login_buttons[0]['text']}")
    
    def test_login_failure_detection(self, browser, demo_login_url):
        """ログイン失敗時のエラーメッセージ検出テスト"""
        # テスト用ログインページに移動
        browser.navigate_to(demo_login_url)
        
        # ページ解析を実行
        page_analysis = browser.analyze_page_content(element_filter={'forms': True, 'inputs': True, 'buttons': True})
        
        # ユーザー名/メールアドレス入力欄の取得
        username_inputs = [
            inp for inp in page_analysis['inputs'] 
            if any(keyword in inp['name'].lower() or keyword in inp.get('id', '').lower() 
                  for keyword in ['user', 'email', 'login', 'name'])
        ]
        
        # パスワード入力欄の取得
        password_inputs = [
            inp for inp in page_analysis['inputs'] 
            if 'password' in inp['name'].lower() or 'password' in inp.get('id', '').lower() or inp['type'] == 'password'
        ]
        
        # ログインボタンの取得
        login_buttons = [
            btn for btn in page_analysis['buttons'] 
            if any(keyword in btn['text'].lower() or keyword in btn.get('id', '').lower() 
                  for keyword in ['login', 'signin', 'submit', 'ログイン'])
        ]
        
        if username_inputs and password_inputs and login_buttons:
            # 無効なログイン情報を入力
            username_inputs[0]['element'].clear()
            username_inputs[0]['element'].send_keys("invalid_user")
            
            password_inputs[0]['element'].clear()
            password_inputs[0]['element'].send_keys("invalid_password")
            
            # ログインボタンをクリック
            login_buttons[0]['element'].click()
            
            # ページの読み込みを待機
            browser.wait_for_page_load()
            
            # エラーメッセージの検出（ページ解析を再実行）
            updated_analysis = browser.analyze_page_content(element_filter={'errors': True})
            
            # エラーメッセージが表示されているか確認
            # エラーメッセージがない場合は、テキスト検索でエラー関連の文言を探す
            if not updated_analysis['error_messages']:
                error_elements = browser.find_element_by_text("invalid", case_sensitive=False) or \
                                browser.find_element_by_text("incorrect", case_sensitive=False) or \
                                browser.find_element_by_text("error", case_sensitive=False) or \
                                browser.find_element_by_text("failed", case_sensitive=False)
                
                assert len(error_elements) > 0, "ログイン失敗時のエラーメッセージが検出されませんでした"
                logger.info(f"検出されたエラーメッセージ: {error_elements[0]['text']}")
            else:
                # エラーメッセージが検出された場合
                logger.info(f"検出されたエラーメッセージ: {updated_analysis['error_messages'][0]['text']}")
                assert len(updated_analysis['error_messages']) > 0, "ログイン失敗時のエラーメッセージが検出されませんでした"
        else:
            pytest.skip("ログインフォームの要素が検出できなかったため、テストをスキップします")
    
    def test_login_security_features(self, browser, demo_login_url):
        """ログインページのセキュリティ機能検出テスト"""
        # テスト用ログインページに移動
        browser.navigate_to(demo_login_url)
        
        # HTMLソースを取得してセキュリティ関連の機能を検査
        page_source = browser.get_page_source()
        
        # セキュリティ機能の検出結果
        security_features = {
            'csrf_token': False,  # CSRF対策トークン
            'https': browser.driver.current_url.startswith('https'),  # HTTPS接続
            'autocomplete_off': False,  # パスワードの自動補完防止
            'remember_me': False,  # ログイン情報の記憶機能
            'captcha': False,  # CAPTCHA
            'two_factor': False,  # 二要素認証
            'password_requirements': False  # パスワード要件
        }
        
        # ページ解析を実行
        page_analysis = browser.analyze_page_content()
        
        # CSRF対策トークンの検出
        if 'csrf' in page_source.lower() or '_token' in page_source.lower():
            security_features['csrf_token'] = True
        
        # パスワード入力欄でautocomplete="off"の検出
        password_inputs = [
            inp for inp in page_analysis['inputs'] 
            if inp['type'] == 'password' or 'password' in inp['name'].lower()
        ]
        
        if password_inputs and 'autocomplete="off"' in page_source:
            security_features['autocomplete_off'] = True
        
        # Remember Meチェックボックスの検出
        remember_elements = browser.find_element_by_text("remember", case_sensitive=False)
        if remember_elements:
            security_features['remember_me'] = True
        
        # CAPTCHA機能の検出
        if 'captcha' in page_source.lower() or 'recaptcha' in page_source.lower():
            security_features['captcha'] = True
        
        # 二要素認証に関する表示の検出
        two_factor_elements = browser.find_element_by_text("two-factor", case_sensitive=False) or \
                             browser.find_element_by_text("2fa", case_sensitive=False)
        if two_factor_elements:
            security_features['two_factor'] = True
        
        # パスワード要件の検出
        password_req_elements = browser.find_element_by_text("password requirement", case_sensitive=False) or \
                               browser.find_element_by_text("at least", case_sensitive=False)
        if password_req_elements:
            security_features['password_requirements'] = True
        
        # セキュリティ機能の検出結果をログに出力
        logger.info("検出されたセキュリティ機能:")
        for feature, detected in security_features.items():
            logger.info(f"- {feature}: {'あり' if detected else 'なし'}")
        
        # HTTPS接続の確認（必須とする）
        assert security_features['https'], "ログインページがHTTPS接続ではありません"
    
    def test_login_page_performance(self, browser, demo_login_url):
        """ログインページのパフォーマンス測定テスト"""
        # テスト用ログインページに移動
        start_time = time.time()
        browser.navigate_to(demo_login_url)
        
        # ページのロード完了を待機
        browser.wait_for_page_load()
        
        # ロード完了までの時間を計測
        load_time = time.time() - start_time
        
        # ページ状態を取得して読み込み時間を確認
        page_status = browser._get_page_status()
        performance_time_ms = page_status['load_time_ms']
        
        # パフォーマンス情報をログに出力
        logger.info(f"ページロード時間: {load_time:.2f}秒")
        logger.info(f"Performance API 計測値: {performance_time_ms}ms")
        
        # ページの読み込み時間が基準値を超えていないことを確認
        # (通常は5秒以内が望ましい)
        assert load_time < 10, f"ページの読み込みに時間がかかりすぎています: {load_time:.2f}秒"
    
    def test_login_success_workflow(self, browser, demo_login_url):
        """ログイン成功時のワークフロー検証テスト"""
        # テスト用ログインページに移動
        browser.navigate_to(demo_login_url)
        
        # ページ解析を実行
        page_analysis = browser.analyze_page_content(element_filter={'forms': True, 'inputs': True, 'buttons': True})
        
        # ログインフォームの要素を取得
        username_inputs = [
            inp for inp in page_analysis['inputs'] 
            if any(keyword in inp['name'].lower() or keyword in inp.get('id', '').lower() 
                  for keyword in ['user', 'email', 'login', 'name'])
        ]
        
        password_inputs = [
            inp for inp in page_analysis['inputs'] 
            if 'password' in inp['name'].lower() or 'password' in inp.get('id', '').lower() or inp['type'] == 'password'
        ]
        
        login_buttons = [
            btn for btn in page_analysis['buttons'] 
            if any(keyword in btn['text'].lower() or keyword in btn.get('id', '').lower() 
                  for keyword in ['login', 'signin', 'submit', 'ログイン'])
        ]
        
        if username_inputs and password_inputs and login_buttons:
            # テスト用サイトの正しい認証情報を入力
            # (このサイトの場合: "student" / "Password123")
            username_inputs[0]['element'].clear()
            username_inputs[0]['element'].send_keys("student")
            
            password_inputs[0]['element'].clear()
            password_inputs[0]['element'].send_keys("Password123")
            
            # ログインボタンをクリック
            login_buttons[0]['element'].click()
            
            # ページの読み込みを待機
            browser.wait_for_page_load()
            
            # ログイン成功の確認 (以下のいずれかの方法で)
            # 1. URLの変化
            current_url = browser.driver.current_url
            assert demo_login_url != current_url, "ログイン後にURLが変化していません"
            
            # 2. 歓迎メッセージの検出
            welcome_elements = browser.find_element_by_text("welcome", case_sensitive=False) or \
                              browser.find_element_by_text("successful", case_sensitive=False) or \
                              browser.find_element_by_text("logged in", case_sensitive=False)
            
            assert len(welcome_elements) > 0, "ログイン成功後の歓迎メッセージが検出されませんでした"
            logger.info(f"検出された成功メッセージ: {welcome_elements[0]['text']}")
            
            # 3. ログアウトボタンの存在を確認
            logout_elements = browser.find_element_by_text("logout", case_sensitive=False) or \
                             browser.find_element_by_text("sign out", case_sensitive=False) or \
                             browser.find_element_by_text("ログアウト", case_sensitive=False)
            
            assert len(logout_elements) > 0, "ログアウトボタンが検出されませんでした"
            logger.info(f"検出されたログアウトボタン: {logout_elements[0]['text']}")
        else:
            pytest.skip("ログインフォームの要素が検出できなかったため、テストをスキップします") 