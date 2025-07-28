#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高機能自動リンク巡回クローラー（マーケティングツール対応完全版）
指定したURLを起点にページ上のリンクをランダムに選択して自動巡回し、
設定ファイルに基づいてページ操作を自動実行する
"""

import requests
import time
import random
import re
import json
import os
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from typing import List, Set, Optional, Dict, Any

# Selenium関連のインポート
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Warning: selenium がインストールされていません。ページ操作機能は無効になります。")
    print("インストール: pip install selenium")

class ConfigManager:
    """設定ファイル管理クラス"""
    
    def __init__(self, config_file: str = "crawler_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        if not os.path.exists(self.config_file):
            self._create_sample_config()
            return {"actions": []}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 設定ファイル読み込みエラー: {e}")
            return {"actions": []}
    
    def _create_sample_config(self):
        """サンプル設定ファイルを作成"""
        sample_config = {
            "word_lists": {
                "names": [
                    "山田太郎", "佐藤花子", "田中一郎", "鈴木次郎", "高橋美咲",
                    "渡辺健太", "伊藤愛子", "中村隆", "小林麻衣", "加藤大輔"
                ],
                "cities": [
                    "東京", "大阪", "名古屋", "福岡", "札幌", 
                    "横浜", "神戸", "京都", "広島", "仙台"
                ],
                "companies": [
                    "株式会社サンプル", "有限会社テスト", "合同会社デモ",
                    "株式会社例示", "企業株式会社", "サンプル商事"
                ],
                "search_keywords": [
                    "Python プログラミング", "機械学習 入門", "ウェブ開発",
                    "データサイエンス", "人工知能", "JavaScript 学習"
                ],
                "emails": [
                    "test@example.com", "sample@test.co.jp", "demo@sample.org",
                    "user@demo.net", "info@example.jp"
                ],
                "phone_numbers": [
                    "03-1234-5678", "06-9876-5432", "052-1111-2222",
                    "092-3333-4444", "011-5555-6666"
                ],
                "keywords": [
                    "apple", "banana", "computer", "development", "education",
                    "football", "garden", "happiness", "internet", "journey",
                    "keyboard", "language", "mountain", "network", "ocean",
                    "picture", "quality", "research", "science", "technology",
                    "umbrella", "vacation", "website", "exercise", "yellow",
                    "zebra", "adventure", "birthday", "creativity", "design",
                    "environment", "friendship", "guitar", "healthy", "innovation",
                    "justice", "knowledge", "learning", "music", "nature",
                    "opportunity", "programming", "question", "rainbow", "solution",
                    "travel", "universe", "victory", "wisdom", "exchange"
                ]
            },
            "ignore_patterns": [
                {
                    "pattern": "logout",
                    "type": "contains",
                    "description": "ログアウトページを除外（部分一致）",
                    "enabled": true
                },
                {
                    "pattern": "admin",
                    "type": "contains", 
                    "description": "管理画面を除外（部分一致）",
                    "enabled": true
                },
                {
                    "pattern": "privacy",
                    "type": "contains",
                    "description": "プライバシーポリシーページを除外（部分一致）",
                    "enabled": true
                },
                {
                    "pattern": "terms",
                    "type": "contains",
                    "description": "利用規約ページを除外（部分一致）",
                    "enabled": true
                },
                {
                    "pattern": "contact",
                    "type": "contains",
                    "description": "お問い合わせページを除外（部分一致）",
                    "enabled": false
                },
                {
                    "pattern": "https://example.com/exact/path",
                    "type": "exact",
                    "description": "特定のURLを完全一致で除外",
                    "enabled": false
                },
                {
                    "pattern": "https://example.com/admin",
                    "type": "startswith",
                    "description": "adminで始まるURLを除外",
                    "enabled": false
                },
                {
                    "pattern": ".pdf",
                    "type": "endswith",
                    "description": "PDFファイルを除外",
                    "enabled": false
                },
                {
                    "pattern": "^https://example\\.com/admin/.*",
                    "type": "regex",
                    "description": "正規表現でadmin配下を除外",
                    "enabled": false
                },
                {
                    "pattern": "https://example.com/*.pdf",
                    "type": "wildcard",
                    "description": "ワイルドカードでPDFファイルを除外",
                    "enabled": false
                }
            ],
            "actions": [
                {
                    "name": "ログインフォーム例",
                    "url_pattern": "example.com/login",
                    "description": "ログインページでの自動入力例",
                    "inputs": [
                        {
                            "xpath": "//input[@name='username']",
                            "random_values": ["user1", "testuser", "sample_user", "demo_user"],
                            "description": "ユーザー名（ランダム選択）"
                        },
                        {
                            "xpath": "//input[@name='password']",
                            "value": "testpass",
                            "description": "パスワード（固定値）"
                        }
                    ],
                    "click_element": "//button[@type='submit']",
                    "wait_after_click": 3,
                    "enabled": False
                },
                {
                    "name": "検索フォーム例",
                    "url_pattern": "google.com",
                    "description": "Google検索の例（ランダムキーワード）",
                    "inputs": [
                        {
                            "xpath": "//input[@name='q']",
                            "value_list": "search_keywords",
                            "description": "検索キーワード（リスト参照）"
                        }
                    ],
                    "click_element": "//input[@value='Google 検索']",
                    "wait_after_click": 2,
                    "enabled": False
                },
                {
                    "name": "お問い合わせフォーム例",
                    "url_pattern": "contact",
                    "description": "お問い合わせフォームでのランダム入力例",
                    "inputs": [
                        {
                            "xpath": "//input[@name='name']",
                            "value_list": "names",
                            "description": "名前（names リストから選択）"
                        },
                        {
                            "xpath": "//input[@name='email']",
                            "value_list": "emails",
                            "description": "メールアドレス（emails リストから選択）"
                        },
                        {
                            "xpath": "//input[@name='company']",
                            "value_list": "companies",
                            "description": "会社名（companies リストから選択）"
                        },
                        {
                            "xpath": "//input[@name='city']",
                            "random_values": ["新宿区", "渋谷区", "中央区", "港区"],
                            "description": "都市（直接ランダム値指定）"
                        },
                        {
                            "xpath": "//textarea[@name='message']",
                            "random_values": [
                                "お世話になっております。サービスについてお問い合わせです。",
                                "貴社のサービスに興味があります。詳細を教えてください。",
                                "料金プランについて教えてください。",
                                "無料トライアルは可能でしょうか？"
                            ],
                            "description": "お問い合わせ内容（ランダム選択）"
                        }
                    ],
                    "click_element": "//button[contains(text(), '送信')]",
                    "wait_after_click": 5,
                    "enabled": False
                }
            ]
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, ensure_ascii=False, indent=2)
            print(f"📁 サンプル設定ファイル '{self.config_file}' を作成しました")
        except Exception as e:
            print(f"❌ 設定ファイル作成エラー: {e}")
    
    def get_actions_for_url(self, url: str) -> List[Dict[str, Any]]:
        """指定URLに対応するアクションを取得"""
        matching_actions = []
        for action in self.config.get("actions", []):
            if not action.get("enabled", True):
                continue
            
            url_pattern = action.get("url_pattern", "")
            if url_pattern and url_pattern in url:
                matching_actions.append(action)
        
        return matching_actions

class WebCrawler:
    def __init__(self, start_url: str, max_steps: int = 10, delay: float = 2.0, 
                 stay_in_domain: bool = True, max_links_per_page: int = 50,
                 config_file: str = "crawler_config.json", use_selenium: bool = True,
                 restart_enabled: bool = False, restart_range: str = "10-20",
                 fast_mode: bool = True, headless: bool = False, log_cookies: bool = True):
        """
        Webクローラーの初期化
        
        Args:
            start_url: 開始URL
            max_steps: 最大ステップ数
            delay: リクエスト間の遅延時間（秒）
            stay_in_domain: 同一ドメイン内のみ巡回するか
            max_links_per_page: 1ページあたりの最大リンク数
            config_file: 設定ファイルのパス
            use_selenium: selenium使用フラグ
            restart_enabled: ブラウザリスタート機能の有効/無効
            restart_range: リスタートステップ範囲（例：10-20）
            fast_mode: 高速モード（True）vs 安全モード（False）
            headless: ヘッドレスモード（True）vs GUI表示（False）
        """
        # ログ設定を最初に行う
        self._setup_logging()
        
        self.start_url = start_url
        self.max_steps = max_steps
        self.delay = delay
        self.stay_in_domain = stay_in_domain
        self.max_links_per_page = max_links_per_page
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.restart_enabled = restart_enabled
        self.restart_range = restart_range
        self.fast_mode = fast_mode
        self.headless = headless
        self.log_cookies = log_cookies
        
        # リスタート設定の解析
        self.restart_min, self.restart_max = self._parse_restart_range(restart_range)
        self.next_restart_step = self._get_next_restart_step() if restart_enabled else None
        self.restart_count = 0
        
        # 設定管理
        self.config_manager = ConfigManager(config_file)
        
        # 開始URLのドメインを取得
        self.base_domain = urlparse(start_url).netloc
        
        # 訪問履歴とリンク履歴
        self.visited_urls: Set[str] = set()
        self.crawl_history: List[dict] = []
        self.action_history: List[dict] = []
        self.restart_history: List[dict] = []
        
        # セッション設定
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Seleniumドライバー
        self.driver = None
        if self.use_selenium:
            self._setup_selenium()
    
    def _parse_restart_range(self, restart_range: str) -> tuple:
        """リスタート範囲を解析"""
        try:
            # 全角ハイフンやその他の文字を半角ハイフンに正規化
            normalized_range = restart_range.replace('−', '-').replace('—', '-').replace('–', '-')
            
            if '-' in normalized_range:
                min_val, max_val = normalized_range.split('-')
                return int(min_val.strip()), int(max_val.strip())
            else:
                # 単一値の場合
                val = int(normalized_range.strip())
                return val, val
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.warning(f"リスタート範囲の解析エラー: {e}. デフォルト値(10-20)を使用します")
            else:
                print(f"⚠️ リスタート範囲の解析エラー: {e}. デフォルト値(10-20)を使用します")
            return 10, 20
    
    def _get_next_restart_step(self) -> int:
        """次回リスタートステップをランダムに決定"""
        if not self.restart_enabled:
            return None
        return random.randint(self.restart_min, self.restart_max)
    
    def _setup_selenium(self):
        """Selenium WebDriverの設定"""
        try:
            chrome_options = Options()
            
            # ヘッドレスモード設定（起動時の設定に基づく）
            if self.headless:
                chrome_options.add_argument('--headless')
                print("👻 ヘッドレスモード: 有効（ブラウザ非表示）")
            else:
                print("🖥️ ヘッドレスモード: 無効（ブラウザ表示）")
            
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # マーケティングツール用の設定
            chrome_options.add_argument('--enable-javascript')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✅ Selenium WebDriver準備完了（マーケティングツール対応モード）")
        except Exception as e:
            print(f"⚠️ Selenium WebDriver設定エラー: {e}")
            print("ChromeDriverがインストールされていることを確認してください")
            self.use_selenium = False
    
    def _setup_logging(self):
        """ログ設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('crawler.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _is_valid_url(self, url: str) -> bool:
        """URLの有効性をチェック"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # 同一ドメイン制限
            if self.stay_in_domain and parsed.netloc != self.base_domain:
                return False
            
            # 除外するファイル拡張子
            excluded_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.rar', '.exe']
            if any(url.lower().endswith(ext) for ext in excluded_extensions):
                return False
            
            # 除外するキーワード
            excluded_keywords = ['mailto:', 'tel:', 'javascript:', '#']
            if any(keyword in url.lower() for keyword in excluded_keywords):
                return False
            
            # 設定ファイルの除外パターンをチェック
            if self._is_ignored_url(url):
                return False
            
            return True
        except Exception:
            return False
    
    def _is_ignored_url(self, url: str) -> bool:
        """設定ファイルの除外パターンにマッチするかチェック"""
        try:
            ignore_patterns = self.config_manager.config.get('ignore_patterns', [])
            url_lower = url.lower()
            
            for pattern_config in ignore_patterns:
                # enabledがFalseの場合はスキップ
                if not pattern_config.get('enabled', True):
                    continue
                
                pattern = pattern_config.get('pattern', '').lower()
                pattern_type = pattern_config.get('type', 'contains')  # デフォルトは部分一致
                
                if not pattern:
                    continue
                
                is_match = False
                
                # パターンタイプに応じてマッチング
                if pattern_type == 'contains':
                    # 部分一致（デフォルト）
                    is_match = pattern in url_lower
                elif pattern_type == 'exact':
                    # 完全一致
                    is_match = url_lower == pattern
                elif pattern_type == 'startswith':
                    # 前方一致
                    is_match = url_lower.startswith(pattern)
                elif pattern_type == 'endswith':
                    # 後方一致
                    is_match = url_lower.endswith(pattern)
                elif pattern_type == 'regex':
                    # 正規表現
                    try:
                        import re
                        is_match = re.search(pattern, url_lower) is not None
                    except re.error as e:
                        self.logger.warning(f"正規表現エラー: {pattern} - {e}")
                        continue
                elif pattern_type == 'wildcard':
                    # ワイルドカード（*と?をサポート）
                    try:
                        import fnmatch
                        is_match = fnmatch.fnmatch(url_lower, pattern)
                    except Exception as e:
                        self.logger.warning(f"ワイルドカードエラー: {pattern} - {e}")
                        continue
                
                if is_match:
                    description = pattern_config.get('description', '不明')
                    self.logger.info(f"🚫 除外パターンマッチ [{pattern_type}]: {pattern} ({description}) - {url}")
                    return True
            
            return False
        except Exception as e:
            self.logger.warning(f"除外パターンチェックエラー: {e}")
            return False
    
    def _fetch_page_with_js(self, url: str) -> Optional[str]:
        """SeleniumでページとJavaScriptを完全実行して取得"""
        if not self.use_selenium or not self.driver:
            # fallback to requests
            return self._fetch_page_fallback(url)
        
        try:
            self.logger.info(f"ページ取得中（JS実行）: {url}")
            self.driver.get(url)
            
            if self.fast_mode:
                # 高速モード
                time.sleep(1)
                self._wait_for_javascript_completion_fast()
                self._wait_for_marketing_tags_fast()
            else:
                # 安全モード
                time.sleep(2)
                self._wait_for_javascript_completion_safe()
                self._wait_for_marketing_tags_safe()
                time.sleep(1)
            
            return self.driver.page_source
        
        except Exception as e:
            self.logger.error(f"Seleniumページ取得エラー: {e}")
            # fallback to requests
            return self._fetch_page_fallback(url)
    
    def _wait_for_javascript_completion_fast(self):
        """JavaScript実行完了を待機（高速版）"""
        try:
            # DOM読み込み完了を待機（タイムアウト短縮）
            WebDriverWait(self.driver, 5).until(  # 10秒 → 5秒に短縮
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # jQueryが存在する場合はAjax完了を待機（タイムアウト短縮）
            try:
                WebDriverWait(self.driver, 2).until(  # 5秒 → 2秒に短縮
                    lambda driver: driver.execute_script("return typeof jQuery === 'undefined' || jQuery.active === 0")
                )
            except TimeoutException:
                pass  # jQueryがない場合は無視
            
        except TimeoutException:
            self.logger.warning("JavaScript実行完了の待機がタイムアウトしました（高速モード）")
    
    def _wait_for_marketing_tags_fast(self):
        """マーケティングタグの読み込み完了を待機（高速・並列版）"""
        try:
            # 全タグを並列チェック（タイムアウト大幅短縮）
            start_time = time.time()
            timeout = 3  # 全体で3秒以内
            
            detected_tags = []
            
            while time.time() - start_time < timeout:
                # Google Tag Manager / Analytics チェック
                try:
                    if self.driver.execute_script(
                        "return typeof gtag !== 'undefined' || typeof dataLayer !== 'undefined' || typeof ga !== 'undefined'"
                    ):
                        if 'GTM/GA' not in detected_tags:
                            detected_tags.append('GTM/GA')
                            print("    📊 Google Tag Manager/Analytics検出")
                except:
                    pass
                
                # Facebook Pixel チェック
                try:
                    if self.driver.execute_script("return typeof fbq !== 'undefined'"):
                        if 'Facebook' not in detected_tags:
                            detected_tags.append('Facebook')
                            print("    📘 Facebook Pixel検出")
                except:
                    pass
                
                # Adobe Analytics チェック
                try:
                    if self.driver.execute_script(
                        "return typeof s !== 'undefined' || typeof adobe !== 'undefined'"
                    ):
                        if 'Adobe' not in detected_tags:
                            detected_tags.append('Adobe')
                            print("    🅰️ Adobe Analytics検出")
                except:
                    pass
                
                # 短時間スリープ
                time.sleep(0.1)
            
            if not detected_tags:
                print("    ⚡ タグ検出タイムアウト（高速モード）")
                
        except Exception as e:
            self.logger.warning(f"マーケティングタグ検出エラー: {e}")
    
    def _wait_for_javascript_completion_safe(self):
        """JavaScript実行完了を待機（安全モード：元の処理）"""
        try:
            # DOM読み込み完了を待機
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # jQueryが存在する場合はAjax完了を待機
            try:
                WebDriverWait(self.driver, 5).until(
                    lambda driver: driver.execute_script("return typeof jQuery === 'undefined' || jQuery.active === 0")
                )
            except TimeoutException:
                pass  # jQueryがない場合は無視
            
        except TimeoutException:
            self.logger.warning("JavaScript実行完了の待機がタイムアウトしました（安全モード）")
    
    def _wait_for_marketing_tags_safe(self):
        """マーケティングタグの読み込み完了を待機（安全モード：元の処理）"""
        try:
            # Google Tag Manager の読み込み待機
            try:
                WebDriverWait(self.driver, 5).until(
                    lambda driver: driver.execute_script(
                        "return typeof gtag !== 'undefined' || typeof dataLayer !== 'undefined'"
                    )
                )
                print("    📊 Google Tag Manager検出")
            except TimeoutException:
                pass
            
            # Google Analytics の読み込み待機
            try:
                WebDriverWait(self.driver, 3).until(
                    lambda driver: driver.execute_script(
                        "return typeof ga !== 'undefined' || typeof gtag !== 'undefined'"
                    )
                )
                print("    📈 Google Analytics検出")
            except TimeoutException:
                pass
            
            # Facebook Pixel の読み込み待機
            try:
                WebDriverWait(self.driver, 3).until(
                    lambda driver: driver.execute_script("return typeof fbq !== 'undefined'")
                )
                print("    📘 Facebook Pixel検出")
            except TimeoutException:
                pass
            
            # Adobe Analytics の読み込み待機
            try:
                WebDriverWait(self.driver, 3).until(
                    lambda driver: driver.execute_script(
                        "return typeof s !== 'undefined' || typeof adobe !== 'undefined'"
                    )
                )
                print("    🅰️ Adobe Analytics検出")
            except TimeoutException:
                pass
                
        except Exception as e:
            self.logger.warning(f"マーケティングタグ検出エラー: {e}")
    
    def _fetch_page_fallback(self, url: str) -> Optional[str]:
        """フォールバック用：従来のrequests方式"""
        try:
            self.logger.info(f"フォールバック：requests でページ取得: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Content-Typeをチェック
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                self.logger.warning(f"HTMLではないコンテンツ: {content_type}")
                return None
            
            return response.text
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"フォールバックページ取得エラー: {e}")
            return None
    
    def _extract_links_from_selenium(self, current_url: str) -> List[str]:
        """Seleniumからリンクを抽出（JavaScript生成リンクも取得可能）"""
        try:
            links = []
            
            # JavaScript実行後のリンクを取得
            link_elements = self.driver.find_elements(By.TAG_NAME, "a")
            
            for element in link_elements:
                try:
                    href = element.get_attribute("href")
                    if href:
                        # 相対URLを絶対URLに変換
                        absolute_url = urljoin(current_url, href.strip())
                        
                        # URLの有効性をチェック
                        if self._is_valid_url(absolute_url) and absolute_url not in self.visited_urls:
                            links.append(absolute_url)
                except Exception:
                    continue  # 個別のリンク取得エラーは無視
            
            # 重複を除去し、制限数まで削る
            unique_links = list(set(links))
            if len(unique_links) > self.max_links_per_page:
                unique_links = random.sample(unique_links, self.max_links_per_page)
            
            return unique_links
        
        except Exception as e:
            self.logger.error(f"Seleniumリンク抽出エラー: {e}")
            return []
    
    def _extract_links(self, html: str, current_url: str) -> List[str]:
        """HTMLからリンクを抽出（フォールバック用）"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            # aタグのhref属性を取得
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href'].strip()
                
                # 相対URLを絶対URLに変換
                absolute_url = urljoin(current_url, href)
                
                # URLの有効性をチェック
                if self._is_valid_url(absolute_url) and absolute_url not in self.visited_urls:
                    links.append(absolute_url)
            
            # 重複を除去し、制限数まで削る
            unique_links = list(set(links))
            if len(unique_links) > self.max_links_per_page:
                unique_links = random.sample(unique_links, self.max_links_per_page)
            
            return unique_links
        
        except Exception as e:
            self.logger.error(f"HTMLリンク抽出エラー: {e}")
            return []
    
    def _get_input_value(self, input_config: Dict[str, Any]) -> Optional[str]:
        """入力値を取得（固定値、ランダム値、リスト参照をサポート）"""
        # 1. 固定値が指定されている場合
        if 'value' in input_config and input_config['value'] is not None:
            return str(input_config['value'])
        
        # 2. 直接ランダム値配列が指定されている場合
        if 'random_values' in input_config:
            random_values = input_config['random_values']
            if isinstance(random_values, list) and random_values:
                selected_value = random.choice(random_values)
                print(f"    🎲 ランダム選択: {selected_value} (選択肢数: {len(random_values)})")
                return str(selected_value)
        
        # 3. word_listsからの参照が指定されている場合
        if 'value_list' in input_config:
            list_name = input_config['value_list']
            word_lists = self.config_manager.config.get('word_lists', {})
            if list_name in word_lists:
                word_list = word_lists[list_name]
                if isinstance(word_list, list) and word_list:
                    selected_value = random.choice(word_list)
                    print(f"    🎲 リスト'{list_name}'から選択: {selected_value} (選択肢数: {len(word_list)})")
                    return str(selected_value)
                else:
                    print(f"    ⚠️ リスト'{list_name}'が空または無効です")
            else:
                print(f"    ⚠️ リスト'{list_name}'が見つかりません")
        
        return None
    
    def _perform_page_actions(self, url: str) -> bool:
        """ページ操作を実行"""
        if not self.use_selenium or not self.driver:
            return False
        
        actions = self.config_manager.get_actions_for_url(url)
        if not actions:
            return False
        
        try:
            # ページをSeleniumで読み込み
            self.driver.get(url)
            time.sleep(2)  # ページ読み込み待機
            
            for action in actions:
                print(f"🎯 アクション実行: {action.get('name', '不明')}")
                print(f"📝 説明: {action.get('description', '')}")
                
                action_success = True
                inputs_processed = 0
                inputs_successful = 0
                
                # INPUT要素に値を設定
                inputs = action.get('inputs', [])
                for input_config in inputs:
                    xpath = input_config.get('xpath')
                    description = input_config.get('description', '')
                    
                    if not xpath:
                        continue
                    
                    inputs_processed += 1
                    
                    # 入力値を取得（固定値、ランダム値、リスト参照をサポート）
                    value = self._get_input_value(input_config)
                    
                    if value is None:
                        print(f"  ⚠️ 入力値が取得できません: {description}")
                        continue
                    
                    try:
                        element = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                        element.clear()
                        element.send_keys(value)
                        inputs_successful += 1
                        print(f"  ✅ 入力完了: {description} = {value}")
                    except TimeoutException:
                        print(f"  ❌ 要素が見つからない: {xpath} ({description})")
                        action_success = False
                    except Exception as e:
                        print(f"  ❌ 入力エラー: {e}")
                        action_success = False
                
                # 要素をクリック
                click_xpath = action.get('click_element')
                click_successful = False
                if click_xpath:
                    try:
                        element = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, click_xpath))
                        )
                        element.click()
                        click_successful = True
                        print(f"  ✅ クリック完了: {click_xpath}")
                        
                        # クリック後の待機時間
                        wait_time = action.get('wait_after_click', 3)
                        time.sleep(wait_time)
                        
                    except TimeoutException:
                        print(f"  ❌ クリック要素が見つからない: {click_xpath}")
                        action_success = False
                    except Exception as e:
                        print(f"  ❌ クリックエラー: {e}")
                        action_success = False
                
                # 最終的な成功判定
                overall_success = action_success and (inputs_successful == inputs_processed or inputs_processed == 0) and (click_successful or not click_xpath)
                
                # アクション履歴に記録
                self.action_history.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'url': url,
                    'action_name': action.get('name', '不明'),
                    'success': overall_success,
                    'inputs_total': inputs_processed,
                    'inputs_successful': inputs_successful,
                    'click_attempted': bool(click_xpath),
                    'click_successful': click_successful,
                    'description': action.get('description', '')
                })
                
                # 結果表示
                if overall_success:
                    print(f"  🎉 アクション '{action.get('name')}' 完了")
                    print(f"      📊 入力成功: {inputs_successful}/{inputs_processed}, クリック: {'✅' if click_successful or not click_xpath else '❌'}")
                else:
                    print(f"  ⚠️ アクション '{action.get('name')}' で一部エラー発生")
                    print(f"      📊 入力成功: {inputs_successful}/{inputs_processed}, クリック: {'✅' if click_successful or not click_xpath else '❌'}")
            
            return True
            
        except Exception as e:
            print(f"❌ ページ操作エラー: {e}")
            return False
    
    def _perform_browser_restart(self, current_step: int) -> bool:
        """ブラウザリスタートを実行"""
        try:
            print(f"\n🔄 ブラウザリスタート実行中 (ステップ {current_step})")
            
            # リスタート履歴に記録
            restart_entry = {
                'step': current_step,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'restart_count': self.restart_count + 1,
                'visited_urls_before': len(self.visited_urls)
            }
            
            if self.driver:
                # Cookie削除
                self.driver.delete_all_cookies()
                print("  🍪 Cookieを削除しました")
                
                # ローカルストレージ削除
                try:
                    self.driver.execute_script("window.localStorage.clear();")
                    print("  💾 ローカルストレージをクリアしました")
                except Exception as e:
                    print(f"  ⚠️ ローカルストレージクリア警告: {e}")
                
                # セッションストレージ削除
                try:
                    self.driver.execute_script("window.sessionStorage.clear();")
                    print("  💾 セッションストレージをクリアしました")
                except Exception as e:
                    print(f"  ⚠️ セッションストレージクリア警告: {e}")
                
                # キャッシュクリア（可能な範囲で）
                try:
                    self.driver.execute_script("window.location.reload(true);")
                    print("  🔄 ハードリロードを実行しました")
                except Exception as e:
                    print(f"  ⚠️ リロード警告: {e}")
            
            # 訪問済みURLリストをクリア
            self.visited_urls.clear()
            print("  🗂️ 訪問済みURLリストをクリアしました")
            
            # Requestsセッションも更新
            self.session.cookies.clear()
            print("  🍪 Requestsセッションのクッキーもクリアしました")
            
            # リスタート回数をインクリメント
            self.restart_count += 1
            
            # 次回リスタートステップを決定
            remaining_steps = self.max_steps - current_step
            if remaining_steps > self.restart_max:
                self.next_restart_step = current_step + self._get_next_restart_step()
            else:
                self.next_restart_step = None  # 残りステップが少ない場合は無効化
            
            restart_entry['success'] = True
            restart_entry['next_restart_step'] = self.next_restart_step
            self.restart_history.append(restart_entry)
            
            print(f"  ✅ リスタート完了 (#{self.restart_count})")
            if self.next_restart_step:
                print(f"  📅 次回リスタート予定: ステップ {self.next_restart_step}")
            else:
                print(f"  📅 次回リスタート: なし（残りステップ数が少ないため）")
            
            return True
            
        except Exception as e:
            print(f"  ❌ リスタートエラー: {e}")
            restart_entry['success'] = False
            restart_entry['error'] = str(e)
            self.restart_history.append(restart_entry)
            return False
    
    def _add_to_history(self, step: int, url: str, links_found: int, selected_link: str = None, action_performed: bool = False, restart_occurred: bool = False):
        """履歴に追加"""
        # Cookie情報を取得
        cookie_count = 0
        cookie_details = []
        if self.use_selenium and self.driver and self.log_cookies:
            try:
                cookies = self.driver.get_cookies()
                cookie_count = len(cookies)
                cookie_details = cookies  # 詳細情報も保存
            except:
                pass
        
        history_entry = {
            'step': step,
            'url': url,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'links_found': links_found,
            'selected_link': selected_link,
            'domain': urlparse(url).netloc,
            'action_performed': action_performed,
            'restart_occurred': restart_occurred,
            'cookie_count': cookie_count,
            'cookie_details': cookie_details
        }
        self.crawl_history.append(history_entry)
    
    def _log_cookie_info(self, step: int, url: str):
        """Cookie情報をログに出力"""
        if not self.use_selenium or not self.driver:
            return
        
        try:
            cookies = self.driver.get_cookies()
            if cookies:
                # 画面には表形式のみ表示
                print(f"\n🍪 ステップ {step} - Cookie情報 ({len(cookies)}個)")
                print(f"📍 URL: {url}")
                
                # 表形式でヘッダーを表示
                print("┌" + "─" * 20 + "┬" + "─" * 30 + "┬" + "─" * 20 + "┬" + "─" * 10 + "┐")
                print("│ {:<18} │ {:<28} │ {:<18} │ {:<8} │".format("Cookie名", "値", "ドメイン", "セキュア"))
                print("├" + "─" * 20 + "┼" + "─" * 30 + "┼" + "─" * 20 + "┼" + "─" * 10 + "┤")
                
                for cookie in cookies:
                    name = cookie.get('name', 'N/A')
                    value = cookie.get('value', 'N/A')
                    domain = cookie.get('domain', 'N/A')
                    secure = cookie.get('secure', False)
                    
                    # 値が長い場合は短縮表示
                    display_value = value[:25] + "..." if len(value) > 25 else value
                    
                    # セキュアフラグの表示
                    secure_flag = "✓" if secure else "✗"
                    
                    print("│ {:<18} │ {:<28} │ {:<18} │ {:<8} │".format(
                        name[:18], display_value[:28], domain[:18], secure_flag
                    ))
                
                print("└" + "─" * 20 + "┴" + "─" * 30 + "┴" + "─" * 20 + "┴" + "─" * 10 + "┘")
                
                # ログファイルに詳細情報を記録（画面には表示しない）
                self._log_cookie_details_to_file(step, cookies)
                
            else:
                print(f"\n🍪 ステップ {step} - Cookie情報: なし")
                self.logger.info(f"ステップ {step} - Cookie情報: Cookieなし")
                
        except Exception as e:
            print(f"\n🍪 ステップ {step} - Cookie情報取得エラー: {e}")
            self.logger.warning(f"Cookie情報取得エラー: {e}")
    
    def _log_cookie_details_to_file(self, step: int, cookies: list):
        """Cookie詳細情報をログファイルに記録（画面には表示しない）"""
        try:
            self.logger.info(f"ステップ {step} - Cookie情報: {len(cookies)}個のCookieを検出")
            for i, cookie in enumerate(cookies, 1):
                name = cookie.get('name', 'N/A')
                value = cookie.get('value', 'N/A')
                domain = cookie.get('domain', 'N/A')
                path = cookie.get('path', 'N/A')
                expiry = cookie.get('expiry', 'N/A')
                secure = cookie.get('secure', False)
                http_only = cookie.get('httpOnly', False)
                
                # 有効期限の変換
                expiry_str = 'N/A'
                if expiry != 'N/A':
                    try:
                        expiry_str = datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        expiry_str = str(expiry)
                
                self.logger.info(f"  Cookie {i}: {name}")
                self.logger.info(f"    値: {value}")
                self.logger.info(f"    ドメイン: {domain}")
                self.logger.info(f"    パス: {path}")
                self.logger.info(f"    有効期限: {expiry_str}")
                self.logger.info(f"    セキュア: {secure}")
                self.logger.info(f"    HttpOnly: {http_only}")
        except Exception as e:
            self.logger.warning(f"Cookie詳細ログ記録エラー: {e}")
    
    def crawl(self):
        """クローリング実行"""
        print("=" * 60)
        print(f"🚀 高機能Webクローリング開始")
        print(f"📍 開始URL: {self.start_url}")
        print(f"📊 最大ステップ数: {self.max_steps}")
        print(f"⏱️ 遅延時間: {self.delay}秒")
        print(f"🌐 ドメイン制限: {'有効' if self.stay_in_domain else '無効'}")
        print(f"🤖 ページ操作: {'有効' if self.use_selenium else '無効'}")
        
        # 除外パターンの表示
        ignore_patterns = self.config_manager.config.get('ignore_patterns', [])
        enabled_patterns = [p for p in ignore_patterns if p.get('enabled', True)]
        if enabled_patterns:
            print(f"🚫 除外パターン: {len(enabled_patterns)}個有効")
            for pattern in enabled_patterns:
                pattern_type = pattern.get('type', 'contains')
                print(f"    • [{pattern_type}] {pattern['pattern']}: {pattern['description']}")
        else:
            print(f"🚫 除外パターン: なし")
        
        if self.restart_enabled:
            print(f"🔄 ブラウザリスタート: 有効 ({self.restart_range}ステップ間隔)")
            print(f"📅 初回リスタート予定: ステップ {self.next_restart_step}")
        else:
            print(f"🔄 ブラウザリスタート: 無効")
        
        if self.fast_mode:
            print(f"⚡ 処理速度: 高速モード")
        else:
            print(f"🐌 処理速度: 安全モード")
            
        if self.headless:
            print(f"👻 表示モード: ヘッドレス")
        else:
            print(f"🖥️ 表示モード: ブラウザ表示")
        
        if self.log_cookies:
            print(f"🍪 Cookie情報出力: 有効")
        else:
            print(f"🍪 Cookie情報出力: 無効")
            
        print("=" * 60)
        
        current_url = self.start_url
        
        for step in range(1, self.max_steps + 1):
            print(f"\n📝 ステップ {step}/{self.max_steps}")
            
            # リスタートチェック
            if (self.restart_enabled and 
                self.next_restart_step is not None and 
                step == self.next_restart_step):
                
                restart_success = self._perform_browser_restart(step)
                if restart_success:
                    current_url = self.start_url  # スタートURLに戻る
                    print(f"🏠 スタートURLに戻ります: {current_url}")
                else:
                    print("⚠️ リスタートに失敗しましたが、処理を継続します")
            
            print(f"🔗 現在のURL: {current_url}")
            
            # Cookie情報をログに出力
            if self.log_cookies:
                self._log_cookie_info(step, current_url)
            
            # ページアクションをチェック・実行
            action_performed = self._perform_page_actions(current_url)
            
            # 全ページでSelenium使用（マーケティングツール対応）
            if self.use_selenium and self.driver:
                # Seleniumでページを取得（JavaScript完全実行）
                if not action_performed:
                    # アクションが実行されていない場合、新しくページを読み込み
                    html_content = self._fetch_page_with_js(current_url)
                else:
                    # アクションが実行済みの場合、現在のページソースを使用
                    html_content = self.driver.page_source
                    # 現在のURLを更新（リダイレクトされた可能性）
                    current_url = self.driver.current_url
                    print(f"🔄 現在のURL（操作後）: {current_url}")
                
                # Seleniumから直接リンクを抽出（JavaScript生成リンクも取得）
                if html_content:
                    links = self._extract_links_from_selenium(current_url)
                else:
                    links = []
            else:
                # Seleniumが無効な場合のフォールバック
                html_content = self._fetch_page_fallback(current_url)
                if html_content:
                    links = self._extract_links(html_content, current_url)
                else:
                    links = []
            
            if not html_content:
                print("❌ ページの取得に失敗しました")
                break
            
            # 訪問済みに追加
            self.visited_urls.add(current_url)
            
            print(f"🔍 {len(links)}個のリンクを発見")
            
            if not links:
                print("⚠️ 有効なリンクが見つかりませんでした")
                # リンクが見つからない場合でもリスタートがあれば継続
                if (self.restart_enabled and 
                    self.next_restart_step is not None and 
                    step < self.next_restart_step and 
                    step < self.max_steps):
                    print("🔄 リスタート待ちのため処理を継続します")
                    current_url = self.start_url
                    self._add_to_history(step, current_url, 0, action_performed=action_performed, restart_occurred=(step == self.next_restart_step))
                    continue
                else:
                    self._add_to_history(step, current_url, 0, action_performed=action_performed, restart_occurred=(step == self.next_restart_step))
                    break
            
            # ランダムにリンクを選択
            selected_link = random.choice(links)
            print(f"🎯 選択されたリンク: {selected_link}")
            
            # 履歴に追加
            restart_occurred = (self.restart_enabled and 
                              self.next_restart_step is not None and 
                              step == self.next_restart_step)
            self._add_to_history(step, current_url, len(links), selected_link, action_performed, restart_occurred)
            
            # 最後のステップでない場合、次のURLに移動
            if step < self.max_steps:
                current_url = selected_link
                print(f"⏳ {self.delay}秒待機中...")
                time.sleep(self.delay)
            else:
                # 最後のステップでは選択したリンクの情報も記録
                if self.use_selenium and self.driver:
                    final_html = self._fetch_page_with_js(selected_link)
                    if final_html:
                        final_links = self._extract_links_from_selenium(selected_link)
                        self._add_to_history(step + 1, selected_link, len(final_links))
                        self.visited_urls.add(selected_link)
                else:
                    final_html = self._fetch_page_fallback(selected_link)
                    if final_html:
                        final_links = self._extract_links(final_html, selected_link)
                        self._add_to_history(step + 1, selected_link, len(final_links))
                        self.visited_urls.add(selected_link)
        
        self._print_summary()
    
    def _print_summary(self):
        """結果サマリーを表示"""
        print("\n" + "=" * 60)
        print("📊 クローリング結果サマリー")
        print("=" * 60)
        
        print(f"🔢 総ステップ数: {len(self.crawl_history)}")
        print(f"🌐 訪問ページ数: {len(self.visited_urls)}")
        print(f"🤖 実行されたアクション数: {len(self.action_history)}")
        if self.restart_enabled:
            print(f"🔄 ブラウザリスタート回数: {self.restart_count}")
        
        # ドメイン別統計
        domain_count = {}
        for entry in self.crawl_history:
            domain = entry['domain']
            domain_count[domain] = domain_count.get(domain, 0) + 1
        
        print(f"\n📈 ドメイン別訪問数:")
        for domain, count in sorted(domain_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {domain}: {count}回")
        
        # リスタート履歴
        if self.restart_history:
            print(f"\n🔄 ブラウザリスタート履歴:")
            for restart in self.restart_history:
                status = "✅ 成功" if restart['success'] else "❌ 失敗"
                print(f"  • [{restart['timestamp']}] #{restart['restart_count']}: {status} (ステップ {restart['step']})")
                if restart.get('next_restart_step'):
                    print(f"    次回予定: ステップ {restart['next_restart_step']}")
                if not restart['success'] and restart.get('error'):
                    print(f"    エラー: {restart['error']}")
        
        # アクション実行結果
        if self.action_history:
            print(f"\n🤖 アクション実行結果:")
            successful_actions = sum(1 for action in self.action_history if action['success'])
            total_inputs = sum(action.get('inputs_total', 0) for action in self.action_history)
            successful_inputs = sum(action.get('inputs_successful', 0) for action in self.action_history)
            
            print(f"  • 成功したアクション: {successful_actions}/{len(self.action_history)}")
            print(f"  • 入力成功率: {successful_inputs}/{total_inputs} ({(successful_inputs/total_inputs*100):.1f}% )" if total_inputs > 0 else "  • 入力: なし")
            
            for action in self.action_history:
                status = "✅ 成功" if action['success'] else "❌ 失敗" 
                inputs_info = f"入力{action.get('inputs_successful', 0)}/{action.get('inputs_total', 0)}"
                click_info = "クリック✅" if action.get('click_successful') else "クリック❌" if action.get('click_attempted') else "クリックなし"
                print(f"  • [{action['timestamp']}] {action['action_name']}: {status} ({inputs_info}, {click_info})")
        
        print(f"\n📋 詳細履歴:")
        for entry in self.crawl_history:
            timestamp = entry['timestamp']
            step = entry['step']
            url = entry['url']
            links_found = entry['links_found']
            selected = entry.get('selected_link', 'なし')
            action_mark = "🤖" if entry.get('action_performed') else ""
            restart_mark = "🔄" if entry.get('restart_occurred') else ""
            
            print(f"  [{timestamp}] ステップ{step} {action_mark}{restart_mark}: {url}")
            print(f"    🔗 {links_found}個のリンクを発見")
            if selected != 'なし':
                print(f"    ➡️ 次の選択: {selected}")
            print()
    
    def save_history(self, filename: str = 'crawl_history.txt'):
        """履歴をファイルに保存"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== 高機能Webクローリング履歴 ===\n\n")
                f.write(f"開始URL: {self.start_url}\n")
                f.write(f"最大ステップ数: {self.max_steps}\n")
                f.write(f"総訪問ページ数: {len(self.visited_urls)}\n")
                f.write(f"実行されたアクション数: {len(self.action_history)}\n")
                
                # 除外パターン情報
                ignore_patterns = self.config_manager.config.get('ignore_patterns', [])
                enabled_patterns = [p for p in ignore_patterns if p.get('enabled', True)]
                if enabled_patterns:
                    f.write(f"除外パターン数: {len(enabled_patterns)}\n")
                    for pattern in enabled_patterns:
                        pattern_type = pattern.get('type', 'contains')
                        f.write(f"  • [{pattern_type}] {pattern['pattern']}: {pattern['description']}\n")
                else:
                    f.write("除外パターン: なし\n")
                
                if self.restart_enabled:
                    f.write(f"ブラウザリスタート回数: {self.restart_count}\n")
                    f.write(f"リスタート設定: {self.restart_range}\n")
                f.write("\n")
                
                # リスタート履歴
                if self.restart_history:
                    f.write("=== ブラウザリスタート履歴 ===\n")
                    for restart in self.restart_history:
                        f.write(f"[{restart['timestamp']}] リスタート #{restart['restart_count']}\n")
                        f.write(f"  ステップ: {restart['step']}\n")
                        f.write(f"  成功: {restart['success']}\n")
                        f.write(f"  リスタート前訪問URL数: {restart['visited_urls_before']}\n")
                        if restart.get('next_restart_step'):
                            f.write(f"  次回予定ステップ: {restart['next_restart_step']}\n")
                        if not restart['success'] and restart.get('error'):
                            f.write(f"  エラー: {restart['error']}\n")
                        f.write("-" * 30 + "\n")
                    f.write("\n")
                
                f.write("=== アクション実行履歴 ===\n")
                for action in self.action_history:
                    f.write(f"[{action['timestamp']}] {action['action_name']}\n")
                    f.write(f"  URL: {action['url']}\n")
                    f.write(f"  説明: {action.get('description', 'なし')}\n")
                    f.write(f"  全体成功: {action['success']}\n")
                    f.write(f"  入力総数: {action.get('inputs_total', 0)}\n")
                    f.write(f"  入力成功数: {action.get('inputs_successful', 0)}\n")
                    f.write(f"  クリック試行: {action.get('click_attempted', False)}\n")
                    f.write(f"  クリック成功: {action.get('click_successful', False)}\n")
                    f.write("-" * 30 + "\n")
                
                f.write("\n=== 巡回履歴 ===\n")
                for entry in self.crawl_history:
                    f.write(f"[{entry['timestamp']}] ステップ {entry['step']}\n")
                    f.write(f"URL: {entry['url']}\n")
                    f.write(f"発見リンク数: {entry['links_found']}\n")
                    f.write(f"アクション実行: {entry.get('action_performed', False)}\n")
                    f.write(f"リスタート発生: {entry.get('restart_occurred', False)}\n")
                    
                    # 詳細なCookie情報を出力
                    if self.log_cookies and entry.get('cookie_details'):
                        f.write(f"Cookie数: {entry.get('cookie_count', 0)}\n")
                        f.write("Cookie詳細:\n")
                        for i, cookie in enumerate(entry['cookie_details'], 1):
                            name = cookie.get('name', 'N/A')
                            value = cookie.get('value', 'N/A')
                            domain = cookie.get('domain', 'N/A')
                            path = cookie.get('path', 'N/A')
                            expiry = cookie.get('expiry', 'N/A')
                            secure = cookie.get('secure', False)
                            http_only = cookie.get('httpOnly', False)
                            
                            # 有効期限の変換
                            expiry_str = 'N/A'
                            if expiry != 'N/A':
                                try:
                                    expiry_str = datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S')
                                except:
                                    expiry_str = str(expiry)
                            
                            f.write(f"  {i}. {name}\n")
                            f.write(f"     値: {value}\n")
                            f.write(f"     ドメイン: {domain}\n")
                            f.write(f"     パス: {path}\n")
                            f.write(f"     有効期限: {expiry_str}\n")
                            f.write(f"     セキュア: {secure}\n")
                            f.write(f"     HttpOnly: {http_only}\n")
                    elif self.log_cookies:
                        f.write(f"Cookie数: {entry.get('cookie_count', 0)}\n")
                    
                    if entry.get('selected_link'):
                        f.write(f"選択リンク: {entry['selected_link']}\n")
                    f.write("-" * 50 + "\n")
            
            print(f"📁 履歴を {filename} に保存しました")
        except Exception as e:
            print(f"❌ ファイル保存エラー: {e}")
    
    def __del__(self):
        """デストラクタ"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except:
                pass

def main():
    """メイン関数"""
    print("🕷️ 高機能自動リンク巡回クローラー（マーケティングツール対応版）")
    print("=" * 60)
    
    # 依存関係チェック
    if not SELENIUM_AVAILABLE:
        print("❌ seleniumが必須です。以下のコマンドでインストールしてください:")
        print("pip install selenium")
        print("また、ChromeDriverも必要です。")
        print("マーケティングツール動作確認のため、Selenium必須です。")
        return
    
    print("🎯 マーケティングツール動作確認対応:")
    print("  • Google Tag Manager")
    print("  • Google Analytics") 
    print("  • Facebook Pixel")
    print("  • Adobe Analytics")
    print("  • その他JavaScriptタグ")
    print()
    
    # ユーザー入力
    start_url = input("開始URL: ").strip()
    if not start_url:
        start_url = "https://example.com"
        print(f"デフォルトURL使用: {start_url}")
    
    try:
        max_steps = int(input("最大ステップ数 (デフォルト: 5): ") or 5)
        delay = float(input("遅延時間(秒) (デフォルト: 3.0): ") or 3.0)
    except ValueError:
        max_steps = 5
        delay = 3.0
        print("デフォルト値を使用します")
    
    # 同一ドメイン制限の設定
    while True:
        stay_in_domain_input = input("同一ドメイン内のみ巡回? (Y/n): ").strip().lower()
        if stay_in_domain_input in ['y', 'yes', '']:
            stay_in_domain = True
            break
        elif stay_in_domain_input in ['n', 'no']:
            stay_in_domain = False
            break
        else:
            print("⚠️ 無効な入力です。'y'、'n'、またはEnterキーを押してください。")
    
    config_file = input("設定ファイル名 (デフォルト: crawler_config.json): ").strip()
    if not config_file:
        config_file = "crawler_config.json"
    
    # Seleniumは必須なので、設定のみ確認
    print("\n--- ブラウザ設定 ---")
    print("💡 マーケティングツール動作確認のため、Seleniumは常に有効です")
    
    # ヘッドレスモード設定
    while True:
        headless_input = input("ヘッドレスモード（ブラウザ非表示）を使用? (Y/n): ").strip().lower()
        if headless_input in ['y', 'yes', '']:
            headless = True
            break
        elif headless_input in ['n', 'no']:
            headless = False
            break
        else:
            print("⚠️ 無効な入力です。'y'、'n'、またはEnterキーを押してください。")
    
    if headless:
        print("✅ ヘッドレスモード: 有効（高速・省リソース）")
    else:
        print("✅ GUIモード: 有効（ブラウザ表示・デバッグ向け）")
    
    use_selenium = True
    
    # ブラウザリスタート設定
    print("\n--- ブラウザリスタート設定 ---")
    while True:
        restart_input = input("ブラウザリスタート機能を使用? (Y/n): ").strip().lower()
        if restart_input in ['y', 'yes', '']:
            restart_enabled = True
            break
        elif restart_input in ['n', 'no']:
            restart_enabled = False
            break
        else:
            print("⚠️ 無効な入力です。'y'、'n'、またはEnterキーを押してください。")
    
    restart_range = "10-20"  # デフォルト値
    if restart_enabled:
        print("リスタート間隔を設定してください:")
        print("例: 10-20 (10〜20ステップ間でランダム)")
        print("例: 15 (15ステップ毎に必ず実行)")
        range_input = input("リスタート間隔 (デフォルト: 10-20): ").strip()
        if range_input:
            # 全角ハイフンを半角ハイフンに変換
            restart_range = range_input.replace('−', '-').replace('—', '-').replace('–', '-')
        print(f"✅ リスタート設定: {restart_range}ステップ間隔")
    else:
        print("❌ リスタート機能: 無効")
    
    # 高速化設定
    print("\n--- 処理速度設定 ---")
    print("⚡ 高速モード: タグ検出時間を最小化（推奨）")
    print("🐌 安全モード: 確実にタグ検出（遅い）")
    while True:
        fast_mode_input = input("高速モードを使用? (Y/n): ").strip().lower()
        if fast_mode_input in ['y', 'yes', '']:
            fast_mode = True
            break
        elif fast_mode_input in ['n', 'no']:
            fast_mode = False
            break
        else:
            print("⚠️ 無効な入力です。'y'、'n'、またはEnterキーを押してください。")
    
    if fast_mode:
        print("✅ 高速モード: 有効（約3-5秒/ページ）")
    else:
        print("🐌 安全モード: 有効（約8-12秒/ページ）")
    
    # Cookie情報出力設定
    print("\n--- Cookie情報出力設定 ---")
    while True:
        cookie_log_input = input("Cookie情報をログに出力しますか? (Y/n): ").strip().lower()
        if cookie_log_input in ['y', 'yes', '']:
            log_cookies = True
            break
        elif cookie_log_input in ['n', 'no']:
            log_cookies = False
            break
        else:
            print("⚠️ 無効な入力です。'y'、'n'、またはEnterキーを押してください。")
    
    if log_cookies:
        print("✅ Cookie情報出力: 有効")
    else:
        print("❌ Cookie情報出力: 無効")
    
    print("\n" + "=" * 60)
    print("🚀 設定完了！マーケティングツール対応クローリングを開始します...")
    print("📊 JavaScript・タグマネージャー完全実行モード")
    if fast_mode:
        print("⚡ 高速モード有効")
    if headless:
        print("👻 ヘッドレスモード有効")
    else:
        print("🖥️ ブラウザ表示モード有効")
    print("=" * 60)
    
    # クローラー実行
    crawler = WebCrawler(
        start_url=start_url,
        max_steps=max_steps,
        delay=delay,
        stay_in_domain=stay_in_domain,
        config_file=config_file,
        use_selenium=use_selenium,
        restart_enabled=restart_enabled,
        restart_range=restart_range,
        fast_mode=fast_mode,
        headless=headless,
        log_cookies=log_cookies
    )
    
    try:
        crawler.crawl()
        
        # 履歴保存の確認
        while True:
            save_input = input("\n履歴をファイルに保存しますか? (Y/n): ").strip().lower()
            if save_input in ['y', 'yes', '']:
                crawler.save_history()
                break
            elif save_input in ['n', 'no']:
                break
            else:
                print("⚠️ 無効な入力です。'y'、'n'、またはEnterキーを押してください。")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによって中断されました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")


if __name__ == "__main__":
    main()