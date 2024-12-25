# weekly-dish

1週間分の夕食の主菜を提案するためのWebアプリケーション

## 環境構築

uvを使ってpython環境を作成しています。uvのインストールについては公式ドキュメントを参照してください。

```bash
git clone [このリポジトリ]
cd [このリポジトリ]
uv sync
```

## 開発方法
- mainブランチへのPRリクエストを作成すると、CIが実行される
    - mypyによる型チェック
    - pytestによるテスト
- mainブランチにマージされると、リリースされる
    - Google CloudのArtifact Registryにコンテナが格納される
    - Cloud Runサービスとしてデプロイされる

## ローカル環境での検証

ローカル環境でstreamlitアプリを起動する
```
cd app
uv run streamlit run app.py
```