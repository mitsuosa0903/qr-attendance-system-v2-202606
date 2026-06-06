# 04. システムアーキテクチャ (System Architecture)

## 🏗️ 全体構成
本システムは、実運用での打刻ミスを物理的に防ぐため、役割ごとに独立した3つのポート（端末）が共通のデータベースを参照する構成を採用しています。

```mermaid
graph TD
    subgraph Office_Entrance [事業所入口 / 出口]
        Terminal_IN[入室用端末<br/>in_app.py / 5001]
        Terminal_OUT[退室用端末<br/>out_app.py / 5002]
    end

    subgraph Back_Office [バックオフィス]
        Admin_PC[管理用端末<br/>admin_app.py / 5003]
    end

    subgraph Data_Layer [データ層]
        DB[(SQLite Database<br/>attendance.db)]
    end

    %% Interactions
    Terminal_IN -- "出勤QRを読取" --> DB
    Terminal_OUT -- "退勤QRを読取" --> DB
    Admin_PC -- "データ照会・管理" --> DB
```

## 🔄 処理フロー（状態遷移）
QRコード読み取り時のシステム挙動は、以下のフローチャートに基づいて判定されます。

```mermaid
flowchart TD
    Start((待機)) --> Detect[QRコード検出<br/>OpenCV]
    Detect --> CheckUser{ユーザー存在確認}
    CheckUser -- "未登録" --> Error[エラー通知]
    CheckUser -- "登録済" --> Judge{当日の打刻状況}
    
    Judge -- "打刻なし" --> In[出勤記録を追加]
    Judge -- "出勤中" --> Out[退勤時間を更新]
    Judge -- "退勤済" --> Ignore[二重打刻防止]
    
    In --> Complete((完了・画面表示))
    Out --> Complete
    Error --> Complete
    Ignore --> Complete
    Complete --> Start
```

## 🔌 端末ごとの役割
1. **入室用端末 (5001)**: 社員が最初に出社した際にQRをかざす専用端末。
2. **退室用端末 (5002)**: 社員が退勤する際にQRをかざす専用端末。
3. **管理者アプリ (5003)**: 社員登録、QR発行、勤怠状況の監視を担当するバックオフィス用。
