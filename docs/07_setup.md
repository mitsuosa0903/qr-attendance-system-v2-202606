# 07. セットアップガイド (Setup Guide)

## 🛠 動作環境
* **OS**: Windows / macOS / Linux
* **Python**: 3.10 以上
* **ハードウェア**: Webカメラ（内蔵または外付け）

## 🚀 導入手順

### 1. リポジトリの準備
```bash
git clone https://github.com/あなたのユーザー名/qr-attendance-system-v2.git
cd qr-attendance-system-v2
```

### 2. ライブラリのインストール
```bash
pip install -r requirements.txt
```

### 3. データベースの初期化
初回実行時のみ、以下のコマンドで空のデータベースを作成します。
```bash
python db/init_db.py
```

### 4. 実行手順
本システムは3つの機能を同時に起動して利用します。

**一括起動する場合（推奨）**:
```bash
python start_all.py
```

**個別に起動する場合**:
ターミナルを3つ開き、それぞれ実行してください。

1. **出勤用アプリ**: `python in_app.py`  (ブラウザで `http://127.0.0.1:5001` を開く)
2. **退勤用アプリ**: `python out_app.py` (ブラウザで `http://127.0.0.1:5002` を開く)
3. **管理者アプリ**: `python admin_app.py` (ブラウザで `http://127.0.0.1:5003` を開く)

## 💡 運用テストの手順
1. 管理者アプリまたは出勤アプリの `/add_user` から適当なIDでユーザーを登録。
2. 表示されたQRコードをスマホ等で撮影（または保存）。
3. 保存したQRコードをカメラにかざすと、打刻が反映されます。
