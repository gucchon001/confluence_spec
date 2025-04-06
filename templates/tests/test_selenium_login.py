#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Seleniumを使用したログインテスト

ダミーのログインページにアクセスし、ログイン機能をテストします。
このテストはHTTPBinやテスト用のログインページを使用します。
"""

import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.utils.environment import env
from src.utils.logging_config import get_logger
from src.modules.selenium.selector import SelectorManager

logger = get_logger(__name__)

class TestSeleniumLogin:
    """Seleniumを使用したログインテスト"""
    
    @pytest.fixture(scope="class")
    def browser_config(self):
        """ブラウザの設定を読み込むフィクスチャ"""
        env.load_env()
        
        # [BROWSER]セクションから設定を読み込む
        config = {
            'headless': env.get_config_value("BROWSER", "headless", "false").lower() == "true",
            'auto_screenshot': env.get_config_value("BROWSER", "auto_screenshot", "true").lower() == "true",
            'screenshot_dir': env.get_config_value("BROWSER", "screenshot_dir", "logs/screenshots"),
            'screenshot_format': env.get_config_value("BROWSER", "screenshot_format", "png"),
            'screenshot_quality': int(env.get_config_value("BROWSER", "screenshot_quality", "100")),
            'screenshot_on_error': env.get_config_value("BROWSER", "screenshot_on_error", "true").lower() == "true"
        }
        
        # スクリーンショットディレクトリの絶対パスを作成
        if not os.path.isabs(config['screenshot_dir']):
            config['screenshot_dir'] = os.path.join(
                str(env.get_project_root()), config['screenshot_dir']
            )
        
        # スクリーンショットディレクトリが存在しない場合は作成
        os.makedirs(config['screenshot_dir'], exist_ok=True)
        
        return config
    
    @pytest.fixture(scope="class")
    def driver(self, browser_config):
        """WebDriverのセットアップと終了処理を行うフィクスチャ"""
        # Chromeオプションの設定
        chrome_options = Options()
        
        # ヘッドレスモードの設定
        if browser_config['headless']:
            chrome_options.add_argument("--headless")
            logger.info("ヘッドレスモードでChromeを起動します")
        
        # その他の共通設定
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # WebDriverの初期化
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 暗黙的な待機を設定
        driver.implicitly_wait(10)
        logger.info("Chromeドライバーを初期化しました")
        
        # ドライバーを返却
        yield driver
        
        # テスト終了後にドライバーをクローズ
        driver.quit()
        logger.info("Chromeドライバーを終了しました")
    
    @pytest.fixture
    def selector_manager(self):
        """セレクタマネージャのフィクスチャ"""
        # プロジェクトルートからセレクタCSVファイルのパスを取得
        project_root = env.get_project_root()
        selectors_path = os.path.join(project_root, "config", "selectors.csv")
        
        # セレクタマネージャの初期化
        selector_mgr = SelectorManager(selectors_path)
        logger.info(f"セレクタマネージャを初期化しました: {selectors_path}")
        return selector_mgr
    
    def take_screenshot(self, driver, browser_config, name):
        """設定に基づいてスクリーンショットを撮影する"""
        if not browser_config['auto_screenshot']:
            return None
            
        filename = f"{name}_{int(time.time())}.{browser_config['screenshot_format']}"
        screenshot_path = os.path.join(browser_config['screenshot_dir'], filename)
        
        try:
            driver.save_screenshot(screenshot_path)
            logger.info(f"スクリーンショットを保存しました: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"スクリーンショットの撮影に失敗しました: {str(e)}")
            return None
    
    def test_selector_manager_initialization(self, selector_manager):
        """セレクタマネージャが正しく初期化されるかテスト"""
        # ログイングループのセレクタが読み込まれているか確認
        login_selectors = selector_manager.get_selectors_by_group("login")
        
        # 読み込まれたセレクタをログに出力
        logger.info(f"ログイングループのセレクタ数: {len(login_selectors)}")
        for name, selector in login_selectors.items():
            logger.info(f"セレクタ: {name}, タイプ: {selector['selector_type']}, 値: {selector['selector_value']}, 説明: {selector.get('description', '')}")
        
        assert len(login_selectors) > 0, "ログイングループのセレクタが読み込まれていません"
        assert "username" in login_selectors, "usernameセレクタが見つかりません"
        assert "password" in login_selectors, "passwordセレクタが見つかりません"
        assert "login_button" in login_selectors, "login_buttonセレクタが見つかりません"
    
    def test_httpbin_form_submission(self, driver, browser_config):
        """HTTPBinのフォーム送信テスト
        
        実際のログインページの代わりに、HTTPBinのフォームページを使用して
        フォーム送信のテストを行います。
        """
        try:
            # HTTPBinのフォームページにアクセス
            driver.get("https://httpbin.org/forms/post")
            logger.info("HTTPBinのフォームページにアクセスしました")
            
            # ページ読み込み後のスクリーンショット
            self.take_screenshot(driver, browser_config, "httpbin_form")
            
            # 各フォーム要素に値を入力
            customer_name = driver.find_element(By.NAME, "custname")
            customer_name.clear()
            customer_name.send_keys("テストユーザー")
            
            # ラジオボタンを選択
            driver.find_element(By.CSS_SELECTOR, "input[value='medium']").click()
            
            # チェックボックスを選択
            driver.find_element(By.NAME, "topping").click()
            
            # 日付を入力
            date_field = driver.find_element(By.NAME, "delivery")
            date_field.clear()
            date_field.send_keys("2023-12-31")
            
            # 入力後のスクリーンショット
            self.take_screenshot(driver, browser_config, "httpbin_form_filled")
            
            # 送信ボタンをクリック
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # 結果ページの検証
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.json"))
            )
            
            # 送信後のスクリーンショット
            self.take_screenshot(driver, browser_config, "httpbin_result")
            
            # 送信結果の確認
            result_json = driver.find_element(By.CSS_SELECTOR, "div.json").text
            logger.info(f"送信結果: {result_json}")
            
            # 結果に期待する値が含まれているか確認
            assert "テストユーザー" in result_json, "送信したユーザー名が結果に含まれていません"
            assert "medium" in result_json, "選択したラジオボタンの値が結果に含まれていません"
            
            logger.info("HTTPBinフォームテストが成功しました")
            
        except Exception as e:
            # エラー時のスクリーンショット
            if browser_config['screenshot_on_error']:
                self.take_screenshot(driver, browser_config, "error_httpbin")
            logger.error(f"テスト中にエラーが発生しました: {str(e)}")
            raise
    
    def test_dummy_login_page(self, driver, selector_manager, browser_config):
        """セレクタを使用したダミーログインページのテスト
        
        ここでは、実際のセレクタを使用しようとしますが、
        テスト対象のページが実際に存在しないため、代わりにJSAlertの操作を
        例示します。
        """
        # テスト対象のURLが設定されているか確認
        login_url = env.get_config_value("TESTS", "DUMMY_LOGIN_URL", "")
        
        # URLが設定されていない場合は、代わりにJavaScriptアラートを使用したデモを実行
        if not login_url:
            logger.info("ダミーログインURLが設定されていないため、JSアラートを使用したデモを実行します")
            
            # JavaScriptでダミーのログインページを作成
            driver.get("about:blank")
            driver.execute_script("""
            document.body.innerHTML = `
                <h1>ダミーログインページ</h1>
                <form id="login-form">
                    <div>
                        <label for="account_key">アカウントキー:</label>
                        <input type="text" id="account_key" name="account_key">
                    </div>
                    <div>
                        <label for="username">ユーザー名:</label>
                        <input type="text" id="username" name="username">
                    </div>
                    <div>
                        <label for="password">パスワード:</label>
                        <input type="password" id="password" name="password">
                    </div>
                    <div>
                        <button type="button" class="loginbtn" onclick="showAlert()">ログイン</button>
                    </div>
                </form>
                <script>
                    function showAlert() {
                        const accountKey = document.getElementById('account_key').value;
                        const username = document.getElementById('username').value;
                        const password = document.getElementById('password').value;
                        
                        if (!accountKey || !username || !password) {
                            alert('すべてのフィールドを入力してください');
                            return;
                        }
                        
                        alert(`ログイン情報\\nアカウントキー: ${accountKey}\\nユーザー名: ${username}\\nパスワード: ${password}`);
                    }
                </script>
            `;
            document.title = "ダミーログインページ";
            """)
            
            logger.info("JSでダミーログインページを作成しました")
            
            # 初期ページのスクリーンショット
            self.take_screenshot(driver, browser_config, "dummy_login")
            
            try:
                # セレクタを使用して要素を検索
                login_group = "login"
                
                # ログインフォームに使用する値を secrets.env から取得（存在すれば）
                account_key = env.get_env_var("TEST_ACCOUNT_KEY", "DEMO123")
                username = env.get_env_var("TEST_USERNAME", "testuser@example.com")
                password = env.get_env_var("TEST_PASSWORD", "password123")
                
                # アカウントキー入力
                account_key_selector = selector_manager.get_selector(login_group, "account_key")
                account_key_locator = (By.ID if account_key_selector["selector_type"] == "id" else By.CSS_SELECTOR, 
                                      account_key_selector["selector_value"])
                account_key_elem = driver.find_element(*account_key_locator)
                account_key_elem.send_keys(account_key)
                
                # ユーザー名入力
                username_selector = selector_manager.get_selector(login_group, "username")
                username_locator = (By.ID if username_selector["selector_type"] == "id" else By.CSS_SELECTOR, 
                                  username_selector["selector_value"])
                username_elem = driver.find_element(*username_locator)
                username_elem.send_keys(username)
                
                # パスワード入力
                password_selector = selector_manager.get_selector(login_group, "password")
                password_locator = (By.ID if password_selector["selector_type"] == "id" else By.CSS_SELECTOR, 
                                  password_selector["selector_value"])
                password_elem = driver.find_element(*password_locator)
                password_elem.send_keys(password)
                
                # 入力後のスクリーンショット
                self.take_screenshot(driver, browser_config, "dummy_login_filled")
                
                # ログインボタンクリック
                login_button_selector = selector_manager.get_selector(login_group, "login_button")
                login_button_locator = (By.CSS_SELECTOR if login_button_selector["selector_type"] == "css" 
                                       else By.XPATH if login_button_selector["selector_type"] == "xpath" 
                                       else By.ID, 
                                       login_button_selector["selector_value"])
                login_button = driver.find_element(*login_button_locator)
                login_button.click()
                
                # アラートの処理
                alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
                alert_text = alert.text
                logger.info(f"アラートメッセージ: {alert_text}")
                assert f"アカウントキー: {account_key}" in alert_text, "アラートに期待するテキストが含まれていません"
                assert f"ユーザー名: {username}" in alert_text, "アラートに期待するテキストが含まれていません"
                alert.accept()
                
                logger.info("ダミーログインテストが成功しました")
                
            except Exception as e:
                # エラー時のスクリーンショット
                if browser_config['screenshot_on_error']:
                    self.take_screenshot(driver, browser_config, "error_dummy_login")
                logger.error(f"テスト中にエラーが発生しました: {str(e)}")
                raise
                
        else:
            # 実際のログインURLが設定されている場合の処理
            logger.info(f"ログインURLが設定されています: {login_url}")
            logger.info("実際のログインテストは実装されていないため、このサンプルではスキップします")
            pytest.skip("設定されたログインURLへのテストはこのサンプルではスキップします") 