# 🕷️ 高機能自動リンク巡回クローラー

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.0+-green.svg)](https://selenium-python.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> マーケティングツール（Google Tag Manager、Google Analytics、Facebook Pixel等）の動作確認を目的とした、JavaScript完全実行対応の自動リンク巡回システム

## 📋 プロジェクト概要

### 目的
マーケティングツール（Google Tag Manager、Google Analytics、Facebook Pixel等）の動作確認を目的とした、JavaScript完全実行対応の自動リンク巡回システム

## 📑 目次

- [🚀 インストール方法](#-インストール方法)
- [📋 プロジェクト概要](#-プロジェクト概要)
- [🏗️ アーキテクチャ](#️-アーキテクチャ)
- [⚙️ 設定ファイル仕様](#️-設定ファイル仕様)
- [🔧 主要クラス・メソッド詳細](#-主要クラスメソッド詳細)
- [🚀 実行フロー](#-実行フロー)
- [📊 マーケティングツール対応詳細](#-マーケティングツール対応詳細)
- [🔄 ブラウザリスタート機能](#-ブラウザリスタート機能)
- [📝 データ構造](#-データ構造)
- [🛠️ 開発・拡張ガイド](#️-開発拡張ガイド)
- [⚠️ 制約・注意事項](#️-制約注意事項)
- [🔧 設定項目詳細](#-設定項目詳細)
- [📁 ファイル構成](#-ファイル構成)
- [🐛 トラブルシューティング](#-トラブルシューティング)
- [📈 拡張可能性](#-拡張可能性)
- [🔒 セキュリティ考慮事項](#-セキュリティ考慮事項)
- [📞 開発支援情報](#-開発支援情報)
- [📋 設定ファイル例](#-設定ファイル例)

### 主要機能
- **自動リンク巡回**: 指定URLを起点にランダムリンク選択で自動巡回
- **マーケティングツール対応**: JavaScript・タグマネージャー完全実行
- **設定ファイルベース操作**: JSON設定によるフォーム入力・クリック自動化
- **ランダム値機能**: 固定値・ランダム配列・共通リスト参照対応
- **ブラウザリスタート**: Cookie削除・ストレージクリア機能
- **柔軟な動作モード**: ヘッドレス/GUI、高速/安全モード切り替え

## 🏗️ アーキテクチャ

### 技術スタック
- **Python 3.9+**
- **Selenium**: ブラウザ自動操作・JavaScript実行
- **BeautifulSoup**: HTMLパース（フォールバック用）
- **Requests**: HTTP通信（フォールバック用）
- **Chrome/ChromeDriver**: 実際のブラウザエンジン

### クラス構造
```
WebCrawler (メインクラス)
├── ConfigManager (設定ファイル管理)
├── _setup_selenium() (ブラウザ初期化)
├── _fetch_page_with_js() (JavaScript実行ページ取得)
├── _perform_page_actions() (自動操作実行)
├── _perform_browser_restart() (ブラウザリスタート)
└── crawl() (メイン巡回処理)
```

## ⚙️ 設定ファイル仕様 (crawler_config.json)

### 基本構造
```json
{
  "word_lists": {
    "リスト名": ["値1", "値2", ...]
  },
  "ignore_patterns": [
    {
      "pattern": "除外パターン",
      "type": "パターンタイプ",
      "description": "説明",
      "enabled": true/false
    }
  ],
  "actions": [
    {
      "name": "アクション名",
      "url_pattern": "対象URLパターン",
      "description": "説明",
      "inputs": [...],
      "click_element": "クリック対象XPATH",
      "wait_after_click": 待機秒数,
      "enabled": true/false
    }
  ]
}
```

### inputs配列の仕様
```json
{
  "xpath": "//input[@name='example']",
  "value": "固定値",                    // 固定値の場合
  "random_values": ["値1", "値2"],       // 直接ランダム値の場合
  "value_list": "word_listのキー名",     // 共通リスト参照の場合
  "description": "説明"
}
```

### ignore_patterns配列の仕様
```json
{
  "pattern": "除外パターン文字列",
  "type": "contains|exact|startswith|endswith|regex|wildcard",
  "description": "除外理由の説明",
  "enabled": true/false
}
```

### 標準word_lists
- `names`: 日本人名前 (10個)
- `cities`: 日本の都市名 (10個)
- `companies`: 会社名 (6個)
- `search_keywords`: 検索キーワード (6個)
- `emails`: メールアドレス (5個)
- `phone_numbers`: 電話番号 (5個)
- `keywords`: 英単語 (50個)

### 除外パターンタイプ (ignore_patterns)
| タイプ | 説明 | 例 | マッチ例 |
|--------|------|-----|----------|
| `contains` | 部分一致（デフォルト） | `"logout"` | `example.com/logout`, `example.com/user/logout` |
| `exact` | 完全一致 | `"https://example.com/admin"` | `https://example.com/admin` のみ |
| `startswith` | 前方一致 | `"https://example.com/admin"` | `https://example.com/admin`, `https://example.com/admin/users` |
| `endswith` | 後方一致 | `".pdf"` | `example.com/file.pdf`, `example.com/documents/report.pdf` |
| `regex` | 正規表現 | `"^https://example\\.com/admin/.*"` | `https://example.com/admin/`, `https://example.com/admin/users` |
| `wildcard` | ワイルドカード | `"https://example.com/*.pdf"` | `https://example.com/file.pdf`, `https://example.com/documents/report.pdf` |

## 🔧 主要クラス・メソッド詳細

### WebCrawler クラス

#### コンストラクタパラメータ
```python
def __init__(self, 
             start_url: str,                    # 開始URL
             max_steps: int = 10,              # 最大ステップ数
             delay: float = 2.0,               # 遅延時間(秒)
             stay_in_domain: bool = True,      # 同一ドメイン制限
             max_links_per_page: int = 50,     # 1ページあたり最大リンク数
             config_file: str = "crawler_config.json",  # 設定ファイル
             use_selenium: bool = True,        # Selenium使用フラグ
             restart_enabled: bool = False,    # リスタート機能
             restart_range: str = "10-20",     # リスタート間隔
             fast_mode: bool = True,           # 高速モード
             headless: bool = False):          # ヘッドレスモード
```

#### 重要メソッド

##### `_fetch_page_with_js(url: str) -> Optional[str]`
- **目的**: JavaScript完全実行でページ取得
- **動作**: Seleniumでページ読み込み → JS実行待機 → マーケティングタグ検出
- **モード分岐**: fast_mode により待機時間・検出方法を変更

##### `_perform_page_actions(url: str) -> bool`
- **目的**: 設定ファイルベースの自動操作実行
- **処理フロー**:
  1. URL条件マッチング
  2. 各input要素への値設定（_get_input_value使用）
  3. 指定要素のクリック
  4. 実行結果の記録

##### `_get_input_value(input_config: Dict) -> Optional[str]`
- **目的**: 入力値の取得（3パターン対応）
- **優先順位**:
  1. `value` (固定値)
  2. `random_values` (直接ランダム配列)
  3. `value_list` (word_lists参照)

##### `_is_ignored_url(url: str) -> bool`
- **目的**: 除外パターンにマッチするかチェック
- **対応パターン**: contains, exact, startswith, endswith, regex, wildcard
- **処理**: 設定ファイルのignore_patternsを順次チェック

##### `_perform_browser_restart(current_step: int) -> bool`
- **目的**: ブラウザ状態の完全リセット
- **処理内容**:
  - Cookie削除
  - localStorage/sessionStorage削除
  - 訪問履歴クリア
  - 開始URLへの復帰

### ConfigManager クラス

#### 主要メソッド
- `get_actions_for_url(url: str)`: URL条件に合致するアクション取得
- `_create_sample_config()`: サンプル設定ファイル自動生成

## 🚀 実行フロー

### 1. 初期化フェーズ
```
設定入力 → WebCrawler初期化 → Selenium起動 → 設定ファイル読み込み
```

### 2. 巡回フェーズ (各ステップ)
```
リスタートチェック → ページアクション実行 → JavaScript完全実行 → 
リンク抽出 → 除外パターンチェック → ランダム選択 → 次URLへ移動
```

### 3. 終了フェーズ
```
結果サマリー表示 → 履歴保存 → ブラウザ終了
```

## 📊 マーケティングツール対応詳細

### 検出対象タグ
- **Google Tag Manager**: `gtag`, `dataLayer`
- **Google Analytics**: `ga`, `gtag`
- **Facebook Pixel**: `fbq`
- **Adobe Analytics**: `s`, `adobe`

### 高速モード vs 安全モード
| 項目 | 高速モード | 安全モード |
|------|------------|------------|
| 基本待機 | 1秒 | 2秒 |
| JS完了待機 | 最大5秒 | 最大10秒 |
| jQuery待機 | 最大2秒 | 最大5秒 |
| タグ検出方式 | 並列・同時 (3秒) | 順次・個別 (20秒) |
| 総処理時間 | 約3-5秒/ページ | 約8-12秒/ページ |

## 🔄 ブラウザリスタート機能

### 実行タイミング
- ランダム間隔（例：10-20ステップ間）
- 設定可能な範囲指定

### リセット内容
1. **ブラウザ状態**: Cookie、localStorage、sessionStorage
2. **アプリ状態**: 訪問済みURLリスト、セッション情報
3. **位置リセット**: 開始URLに自動復帰

## 📝 データ構造

### 巡回履歴 (crawl_history)
```python
{
    'step': int,                    # ステップ番号
    'url': str,                     # 訪問URL
    'timestamp': str,               # タイムスタンプ
    'links_found': int,             # 発見リンク数
    'selected_link': str,           # 選択したリンク
    'domain': str,                  # ドメイン
    'action_performed': bool,       # アクション実行フラグ
    'restart_occurred': bool        # リスタート発生フラグ
}
```

### アクション履歴 (action_history)
```python
{
    'timestamp': str,               # 実行時刻
    'url': str,                     # 対象URL
    'action_name': str,             # アクション名
    'success': bool,                # 全体成功フラグ
    'inputs_total': int,            # 入力試行数
    'inputs_successful': int,       # 入力成功数
    'click_attempted': bool,        # クリック試行フラグ
    'click_successful': bool,       # クリック成功フラグ
    'description': str              # 説明
}
```

## 🛠️ 開発・拡張ガイド

### 新しいマーケティングツール追加
1. `_wait_for_marketing_tags_fast/safe()` にJavaScript検出ロジック追加
2. 検出成功時のログ出力を追加

### 新しいアクションタイプ追加
1. `_perform_page_actions()` に新しい操作タイプ追加
2. 設定ファイルスキーマの拡張

### パフォーマンス改善点
- **並列リンク取得**: 複数ページの同時処理
- **インテリジェント待機**: ページ特性に応じた待機時間調整
- **キャッシュ機能**: 訪問済みページの結果キャッシュ

## ⚠️ 制約・注意事項

### セキュリティ制約
- CORS制約により、一部サイトでiframe内容取得不可
- 同一オリジンポリシーの影響
- ブラウザセキュリティ設定の影響

### パフォーマンス制約
- JavaScript実行により処理時間増加
- メモリ使用量の増大（特にGUIモード）
- ネットワーク依存の不安定性

### 技術的制約
- ChromeDriver のバージョン依存
- Python Selenium バージョン互換性
- OS依存のブラウザ設定

## 🔧 設定項目詳細

### 起動時設定項目
1. **開始URL**: 巡回開始地点
2. **最大ステップ数**: 巡回回数上限
3. **遅延時間**: リクエスト間隔（サーバー負荷軽減）
4. **同一ドメイン制限**: 外部ドメインへの移動制限
5. **設定ファイル名**: アクション定義ファイル
6. **ヘッドレスモード**: ブラウザ表示/非表示
7. **ブラウザリスタート**: Cookie等リセット機能
8. **処理速度**: 高速モード/安全モード
9. **除外パターン**: 設定ファイルで定義された除外条件

### 実行時動的制御
- リスタートタイミングのランダム化
- URL条件によるアクション分岐
- 除外パターンによるリンクフィルタリング
- エラー時のフォールバック処理

## 📁 ファイル構成

```
project/
├── web_crawler.py              # メインプログラム
├── crawler_config.json         # 設定ファイル（自動生成）
├── crawler.log                # 実行ログ
├── crawl_history.txt          # 巡回履歴（任意保存）
└── README.md                  # この仕様書
```

## 🚀 インストール方法

### 🚀 クイックスタート（5分でセットアップ）

```bash
# 1. リポジトリをクローンまたはダウンロード
git clone https://github.com/your-username/web-crawler.git
cd web-crawler

# 2. 依存関係をインストール
pip install -r requirements.txt

# 3. ChromeDriver をインストール（macOS）
brew install chromedriver

# 4. アプリケーションを実行
python3 web_crawler.py
```

### 1. 必要な環境
- **Python 3.9以上**
- **Chrome ブラウザ**
- **ChromeDriver**

### 2. 依存関係のインストール

```bash
# 必要なPythonパッケージをインストール
pip install requests beautifulsoup4 selenium

# または requirements.txt を使用する場合
pip install -r requirements.txt
```

### 3. ChromeDriver のインストール

#### macOS の場合
```bash
# Homebrew を使用
brew install chromedriver

# または手動インストール
# 1. https://chromedriver.chromium.org/ からダウンロード
# 2. 解凍して /usr/local/bin/ に配置
# 3. 実行権限を付与
chmod +x /usr/local/bin/chromedriver
```

#### Windows の場合
```bash
# 1. https://chromedriver.chromium.org/ からダウンロード
# 2. 解凍して PATH が通っているディレクトリに配置
# 3. または環境変数 PATH に追加
```

#### Linux の場合
```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# CentOS/RHEL
sudo yum install chromedriver

# または手動インストール（macOS と同様）
```

### 4. インストール確認

```bash
# Python バージョン確認
python3 --version

# 依存関係確認
python3 -c "import requests, beautifulsoup4, selenium; print('✅ 依存関係OK')"

# ChromeDriver 確認
chromedriver --version
```

### 5. アプリケーションの実行

```bash
# 基本実行
python3 web_crawler.py

# ヘルプ表示（オプション）
python3 web_crawler.py --help
```

## 🚀 実行コマンド例

```bash
# 基本実行
python3 web_crawler.py

# 依存関係インストール
pip install requests beautifulsoup4 selenium

# ChromeDriver の確認
chromedriver --version
```

## 🐛 トラブルシューティング

### よくあるエラー
1. **ChromeDriver not found**: PATH設定またはバージョン不一致
2. **Selenium import error**: `pip install selenium` 実行
3. **fast_mode not defined**: 旧バージョンのコード実行
4. **正規表現エラー**: ignore_patternsのregexタイプで無効なパターン
5. **ワイルドカードエラー**: ignore_patternsのwildcardタイプで無効なパターン

### インストール関連のトラブルシューティング

#### ChromeDriver が見つからない場合
```bash
# PATH を確認
echo $PATH

# ChromeDriver の場所を確認
which chromedriver

# 手動で PATH に追加（macOS/Linux）
export PATH=$PATH:/path/to/chromedriver

# Windows の場合
# システム環境変数に ChromeDriver のパスを追加
```

#### Python パッケージのインストールエラー
```bash
# pip をアップグレード
pip install --upgrade pip

# 仮想環境を使用（推奨）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 依存関係を再インストール
pip install -r requirements.txt
```

#### Chrome ブラウザのバージョン確認
```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version

# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --version

# Linux
google-chrome --version
```

### デバッグ方法
- ヘッドレスモード無効化でブラウザ動作確認
- ログファイル（crawler.log）の詳細確認
- 設定ファイルの構文チェック

## 📈 拡張可能性

### 短期拡張案
- **レポート機能**: HTML/CSV形式の詳細レポート出力
- **スケジューリング**: 定期実行機能
- **並列処理**: 複数ブラウザでの同時巡回
- **除外パターン拡張**: より高度なフィルタリング条件

### 中長期拡張案
- **Web UI**: ブラウザベースの設定・監視画面
- **API化**: REST API での外部連携
- **ML連携**: 行動パターン学習・最適化

## 🔒 セキュリティ考慮事項

### 対象サイトへの配慮
- 適切な遅延時間設定（サーバー負荷軽減）
- robots.txt の尊重
- レート制限の遵守
- 除外パターンによる不要ページの回避

### データ保護
- 取得データの適切な管理
- 個人情報の非取得・非保存
- ログファイルのセキュア管理

## 🔒 セキュリティ

### セキュリティポリシー

このプロジェクトでは、セキュリティの問題を真剣に受け止めています。

#### 脆弱性の報告

セキュリティの脆弱性を発見した場合は、以下の方法で報告してください：

1. **プライベート報告**: セキュリティ関連のIssueを作成し、`security` ラベルを付けてください
2. **詳細な情報**: 脆弱性の詳細、再現手順、影響範囲を含めてください
3. **責任ある開示**: 公開前に開発チームに報告してください

#### セキュリティのベストプラクティス

- 設定ファイルに機密情報（APIキー、パスワード等）を含めないでください
- ログファイルに個人情報が含まれないよう注意してください
- 対象サイトの利用規約を遵守してください

### データ保護
- 取得データの適切な管理
- 個人情報の非取得・非保存
- ログファイルのセキュア管理

---

## 📞 開発支援情報

### 主要変数・定数
- `SELENIUM_AVAILABLE`: Selenium利用可能フラグ
- `self.visited_urls`: 訪問済みURL管理（重複防止）
- `self.next_restart_step`: 次回リスタート予定ステップ

### 重要なステートマシン
巡回処理は以下の状態を持つ：
1. **初期化**: ブラウザ起動・設定読み込み
2. **巡回中**: URL取得→アクション実行→リンク選択
3. **リスタート**: 状態リセット→開始URLに復帰
4. **終了**: リソース解放・結果出力

## 📋 設定ファイル例

### 基本的な設定例
```json
{
  "word_lists": {
    "names": ["山田太郎", "佐藤花子"],
    "emails": ["test@example.com"]
  },
  "ignore_patterns": [
    {
      "pattern": "logout",
      "type": "contains",
      "description": "ログアウトページを除外",
      "enabled": true
    },
    {
      "pattern": "^https://example\\.com/admin/.*",
      "type": "regex",
      "description": "管理画面を正規表現で除外",
      "enabled": true
    }
  ],
  "actions": [
    {
      "name": "ログインフォーム",
      "url_pattern": "login",
      "inputs": [
        {
          "xpath": "//input[@name='username']",
          "value_list": "names"
        }
      ],
      "enabled": true
    }
  ]
}
```

### 除外パターンの詳細例
```json
{
  "ignore_patterns": [
    {
      "pattern": "logout",
      "type": "contains",
      "description": "ログアウトページを除外（部分一致）",
      "enabled": true
    },
    {
      "pattern": "https://example.com/admin",
      "type": "exact",
      "description": "特定の管理画面URLを完全一致で除外",
      "enabled": true
    },
    {
      "pattern": "https://example.com/admin",
      "type": "startswith",
      "description": "adminで始まるURLを除外",
      "enabled": true
    },
    {
      "pattern": ".pdf",
      "type": "endswith",
      "description": "PDFファイルを除外",
      "enabled": true
    },
    {
      "pattern": "^https://example\\.com/admin/.*",
      "type": "regex",
      "description": "正規表現でadmin配下を除外",
      "enabled": true
    },
    {
      "pattern": "https://example.com/*.pdf",
      "type": "wildcard",
      "description": "ワイルドカードでPDFファイルを除外",
      "enabled": true
    }
  ]
}
```

---

この仕様書を参考に、効率的な開発・拡張を行ってください。

---

## 📄 ライセンス

このプロジェクトは [MIT License](LICENSE) の下で公開されています。

## 🤝 コントリビューション

このプロジェクトへの貢献を歓迎します！詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## ⭐ スター

このプロジェクトが役に立った場合は、⭐ を付けてください！

---

**注意**: このツールは教育・研究目的で提供されています。対象サイトの利用規約を遵守してご利用ください。