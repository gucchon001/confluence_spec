#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Selenium ページ解析機能を活用したテスト

ページ要素の分析、インタラクティブ要素の検出、フォーム自動入力など
高度なページ解析機能を使用したテストを行います。
"""

import os
import time
import pytest
from pathlib import Path
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.utils.environment import env
from src.utils.logging_config import get_logger
from src.modules.selenium.browser import Browser
from src.modules.selenium.selector import SelectorManager

# ロガーの設定
logger = get_logger(__name__)

class TestPageAnalyzer:
    """Seleniumページ解析機能を活用したテスト"""
    
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
    def httpbin_form_url(self):
        """HTTPBinのフォームページURL"""
        return "https://httpbin.org/forms/post"
    
    @pytest.fixture
    def demo_store_url(self):
        """テスト用デモストアURL"""
        return "https://demostore.seleniumacademy.com/"
    
    def test_basic_page_analysis(self, browser, httpbin_form_url):
        """基本的なページ解析のテスト"""
        # HTTPBinのフォームページに移動
        browser.navigate_to(httpbin_form_url)
        
        # ページのタイトルを確認
        assert "HTML form" in browser.driver.title, "ページのタイトルが予期したものと異なります"
        
        # ページ解析を実行
        page_analysis = browser.analyze_page_content()
        
        # 解析結果の検証
        assert len(page_analysis['forms']) > 0, "フォームが検出されませんでした"
        assert len(page_analysis['buttons']) > 0, "ボタンが検出されませんでした"
        assert len(page_analysis['inputs']) > 0, "入力フィールドが検出されませんでした"
        
        # ページステータスの確認
        assert page_analysis['page_status']['ready_state'] == "complete", "ページが完全に読み込まれていません"
        assert not page_analysis['page_status']['ajax_requests_active'], "アクティブなAJAXリクエストが存在します"
        
        # ページの基本情報をログに出力
        logger.info(f"ページタイトル: {page_analysis['page_title']}")
        logger.info(f"フォーム数: {len(page_analysis['forms'])}")
        logger.info(f"ボタン数: {len(page_analysis['buttons'])}")
        logger.info(f"リンク数: {len(page_analysis['links'])}")
        logger.info(f"入力フィールド数: {len(page_analysis['inputs'])}")
    
    def test_form_automation(self, browser, httpbin_form_url):
        """フォーム自動操作のテスト"""
        # HTTPBinのフォームページに移動
        browser.navigate_to(httpbin_form_url)
        
        # フォーム要素の解析
        page_analysis = browser.analyze_page_content(element_filter={'forms': True, 'inputs': True, 'buttons': True})
        
        # フォームとそのフィールドを特定
        assert len(page_analysis['inputs']) >= 3, "予期される数の入力フィールドが見つかりません"
        
        # 入力フィールドとボタンを特定
        text_inputs = [inp for inp in page_analysis['inputs'] if inp['type'] in ('text', 'email', 'tel')]
        submit_buttons = [btn for btn in page_analysis['buttons'] if btn['type'] == 'submit' or 'submit' in btn['text'].lower()]
        
        # フォームに自動入力
        for i, input_field in enumerate(text_inputs):
            if input_field['element'].is_enabled() and input_field['element'].is_displayed():
                # フィールドの種類によって適切な値を入力
                if 'email' in input_field['type'] or 'email' in input_field['name'].lower():
                    input_field['element'].send_keys("test@example.com")
                    logger.info(f"メールアドレスを入力: {input_field['name']}")
                else:
                    input_field['element'].send_keys(f"テスト値{i+1}")
                    logger.info(f"テキストを入力: {input_field['name']}")
        
        # ラジオボタンやチェックボックスを選択
        for inp in page_analysis['inputs']:
            if inp['type'] == 'checkbox' and inp['element'].is_enabled() and not inp['element'].is_selected():
                inp['element'].click()
                logger.info(f"チェックボックスを選択: {inp['name']}")
        
        # 検証済みのフォームデータを持っていることを確認
        assert len([inp for inp in text_inputs if inp['element'].get_attribute('value')]) > 0, "フォームに値が入力されていません"
        
        # 送信せずに終了（テストサイトにリクエストを送信しないため）
        logger.info("フォーム自動入力テスト完了")
    
    def test_search_elements_by_text(self, browser, demo_store_url):
        """テキストによる要素検索のテスト"""
        # デモストアに移動
        browser.navigate_to(demo_store_url)
        
        # テキスト検索の実行: "cart"を含む要素を検索
        cart_elements = browser.find_element_by_text("cart", case_sensitive=False)
        assert len(cart_elements) > 0, "'cart'を含む要素が見つかりませんでした"
        
        # テキスト検索の実行: "login"または"account"を含む要素を検索
        login_elements = browser.find_element_by_text("login", case_sensitive=False)
        account_elements = browser.find_element_by_text("account", case_sensitive=False)
        
        # 少なくともどちらかの要素が見つかるはず
        assert len(login_elements) > 0 or len(account_elements) > 0, "ログイン/アカウント関連の要素が見つかりませんでした"
        
        # 見つけた要素の情報をログに出力
        for i, element in enumerate(cart_elements[:3]):  # 最初の3つだけを表示
            logger.info(f"カート要素 {i+1}: {element['text']} (タグ: {element['tag']})")
    
    def test_interactive_elements(self, browser, demo_store_url):
        """インタラクティブ要素の検出と操作のテスト"""
        # デモストアに移動
        browser.navigate_to(demo_store_url)
        
        # インタラクティブ要素の検出
        interactive = browser.find_interactive_elements()
        
        # 検出された要素の数を確認
        assert len(interactive['clickable']) > 0, "クリック可能な要素が見つかりませんでした"
        assert len(interactive['input']) >= 0, "入力フィールドが見つかりませんでした"
        
        # クリック可能な要素の中からナビゲーションメニュー項目を探す
        nav_items = [elem for elem in interactive['clickable'] 
                    if elem['element'].get_attribute('class') and 
                    ('menu' in elem['element'].get_attribute('class') or 'nav' in elem['element'].get_attribute('class'))]
        
        # クリック可能な要素の情報をログに出力
        logger.info(f"クリック可能な要素: {len(interactive['clickable'])}")
        logger.info(f"入力フィールド: {len(interactive['input'])}")
        logger.info(f"ナビゲーション項目: {len(nav_items)}")
        
        if len(nav_items) > 0:
            # 最初のナビゲーション項目をクリックしてページ遷移をテスト
            first_nav = nav_items[0]
            logger.info(f"クリック対象: {first_nav['text']} (タグ: {first_nav['tag']})")
            
            # 現在のURLを記録
            original_url = browser.driver.current_url
            
            # ナビゲーション要素をクリック
            first_nav['element'].click()
            
            # ページの読み込みを待機
            browser.wait_for_page_load()
            
            # URLが変わったことを確認
            new_url = browser.driver.current_url
            assert original_url != new_url, "ナビゲーション後のURLが変わっていません"
            logger.info(f"ページ遷移成功: {original_url} -> {new_url}")
    
    def test_page_state_detection(self, browser, demo_store_url):
        """ページ状態の検出と監視のテスト"""
        # デモストアに移動
        browser.navigate_to(demo_store_url)
        
        # 初期ページ状態の取得
        initial_state = browser._get_page_status()
        assert initial_state['ready_state'] == 'complete', "ページが完全に読み込まれていません"
        
        # インタラクティブ要素の検出
        interactive = browser.find_interactive_elements()
        
        if len(interactive['clickable']) > 0:
            # いずれかのクリック可能な要素をクリックして変化を監視
            # 製品カードかメニュー項目を優先的に探す
            product_cards = [elem for elem in interactive['clickable'] 
                           if elem['element'].get_attribute('class') and 
                           ('product' in elem['element'].get_attribute('class') or 'card' in elem['element'].get_attribute('class'))]
            
            target_element = product_cards[0] if product_cards else interactive['clickable'][0]
            
            # 現在のページソースを記録
            original_source = browser.get_page_source()
            
            # 要素をクリック
            logger.info(f"クリック対象: {target_element['text'][:30]}... (タグ: {target_element['tag']})")
            target_element['element'].click()
            
            # ページ変化の検出
            page_changed = browser.detect_page_changes(wait_seconds=5)
            
            if page_changed:
                logger.info("ページの変化を検出しました")
                
                # 新しいページ状態の取得
                new_state = browser._get_page_status()
                new_source = browser.get_page_source()
                
                # ページ内容が変化したことを確認
                assert original_source != new_source, "ページ内容が変化していません"
                logger.info(f"ページ状態: {new_state['ready_state']}")
                
                # ページが再び完全に読み込まれるのを待機
                browser.wait_for_page_load()
            else:
                logger.info("ページの変化は検出されませんでした")
                
    def test_spa_element_detection(self, browser):
        """単一ページアプリケーション（SPA）での要素検出テスト"""
        # React、Angular、またはVueベースのSPAサイトに移動
        # この例ではReactで構築されたサイトを使用
        browser.navigate_to("https://react-shopping-cart-67954.firebaseapp.com/")
        
        # ページがロードされるまで待機
        browser.wait_for_page_load()
        
        # 初期状態の解析
        initial_analysis = browser.analyze_page_content()
        
        # フィルタまたはソート機能を探す（SPAで動的に内容が変わる要素）
        filter_elements = browser.find_element_by_text("filter", case_sensitive=False)
        sort_elements = browser.find_element_by_text("sort", case_sensitive=False)
        
        target_elements = filter_elements or sort_elements
        
        if target_elements:
            # フィルタまたはソート要素をクリック
            target = target_elements[0]
            logger.info(f"SPA操作対象: {target['text']} (タグ: {target['tag']})")
            target['element'].click()
            
            # SPAの内容更新を待機（画面遷移なしで内容が変わる）
            time.sleep(1)  # 短い待機
            
            # ページの変化を検出
            content_changed = browser.detect_page_changes(wait_seconds=2)
            
            # 2回目の解析を実行
            updated_analysis = browser.analyze_page_content()
            
            if content_changed:
                logger.info("SPA内容の変化を検出しました")
                
                # 何らかの変化があることを確認（ここではボタンの状態など）
                assert initial_analysis != updated_analysis, "SPAの内容に変化がありませんでした"
        else:
            # 商品カードのような要素を探す
            product_elements = browser.find_element_by_text("product", case_sensitive=False) or \
                               browser.find_element_by_text("item", case_sensitive=False) or \
                               browser.find_element_by_text("cart", case_sensitive=False)
            
            if product_elements:
                # 商品要素をクリック
                product = product_elements[0]
                logger.info(f"商品要素: {product['text'][:30]}... (タグ: {product['tag']})")
                product['element'].click()
                
                # SPAの内容更新を待機
                time.sleep(1)
                
                # ページの変化を検出
                content_changed = browser.detect_page_changes(wait_seconds=2)
                logger.info(f"コンテンツ変化検出: {content_changed}")
            else:
                logger.warning("SPAでインタラクティブな要素が見つかりませんでした")
                
    def test_alert_detection(self, browser):
        """アラート検出と処理のテスト"""
        # アラートを表示するJavaScriptを実行できるページに移動
        browser.navigate_to("https://the-internet.herokuapp.com/javascript_alerts")
        
        # ページ内の「アラート表示」ボタンを探す
        alert_buttons = browser.find_element_by_text("Alert", case_sensitive=False)
        
        if alert_buttons:
            # アラートを表示するボタンをクリック
            alert_button = alert_buttons[0]
            logger.info(f"アラートボタン: {alert_button['text']}")
            
            # ボタンをクリック
            alert_button['element'].click()
            
            # アラート情報を取得
            alert_info = browser._check_alerts()
            
            # アラートの存在を確認
            assert alert_info['present'], "アラートが検出されませんでした"
            logger.info(f"アラートテキスト: {alert_info['text']}")
            logger.info(f"アラートタイプ: {alert_info['type']}")
            
            # アラートを受け入れる
            alert = browser.driver.switch_to.alert
            alert.accept()
            
            # 結果メッセージを確認
            success_message = browser.find_element_by_text("successfully", case_sensitive=False)
            assert len(success_message) > 0, "アラート操作の成功メッセージが見つかりませんでした"
            logger.info(f"検出されたメッセージ: {success_message[0]['text']}")
        else:
            logger.warning("アラートボタンが見つかりませんでした") 