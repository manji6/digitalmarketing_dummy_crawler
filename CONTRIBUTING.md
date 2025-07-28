# 🤝 コントリビューションガイド

このプロジェクトへの貢献をありがとうございます！以下のガイドラインに従ってください。

## 🚀 開発環境のセットアップ

1. リポジトリをフォーク
2. ローカルにクローン
```bash
git clone https://github.com/your-username/web-crawler.git
cd web-crawler
```

3. 仮想環境を作成
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
```

4. 依存関係をインストール
```bash
pip install -r requirements.txt
```

## 📝 プルリクエストの作成

1. 新しいブランチを作成
```bash
git checkout -b feature/your-feature-name
```

2. 変更をコミット
```bash
git add .
git commit -m "feat: add new feature description"
```

3. プルリクエストを作成

## 🧪 テスト

新しい機能を追加する際は、テストも含めてください。

```bash
# 基本的な動作確認
python3 web_crawler.py --help
```

## 📋 コミットメッセージの規約

- `feat:` - 新機能
- `fix:` - バグ修正
- `docs:` - ドキュメント更新
- `style:` - コードスタイル修正
- `refactor:` - リファクタリング
- `test:` - テスト追加・修正
- `chore:` - その他の変更

## 🔍 コードレビュー

プルリクエストは以下の点でレビューされます：

- コードの品質
- 機能の実装
- ドキュメントの更新
- テストの追加

## 📞 サポート

質問や提案がある場合は、[Issues](https://github.com/your-username/web-crawler/issues) を作成してください。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。 