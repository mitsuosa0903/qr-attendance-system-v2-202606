# 05. データベース設計 (Database Design)

## 📊 ER図 (ER Diagram)
本システムでは、生の読み取りログと、業務上の意味を持つ勤怠データを分離して管理しています。

```mermaid
erDiagram
    Users {
        string user_id PK "社員番号など"
        string user_name "氏名"
        string created_at "作成日時"
    }
    
    Attendances {
        integer attendance_id PK "自動採番"
        string user_id FK "Usersテーブル参照"
        date work_date "勤務日(YYYY-MM-DD)"
        datetime check_in_time "出勤時刻"
        datetime check_out_time "退勤時刻(Null許容)"
        string status "ステータス(WORKING/FINISHED)"
    }

    ScanLogs {
        integer log_id PK
        string user_id FK
        datetime scan_time "読み取り時刻"
        string scan_type "IN / OUT"
    }

    Users ||--o{ Attendances : "1:N"
    Users ||--o{ ScanLogs : "1:N"
```

## 🗄️ テーブル定義

### 1. Users (ユーザー情報)
社員や利用者の基本情報を管理します。

### 2. Attendances (勤怠情報)
1日単位の出勤・退勤ペアを管理します。`check_out_time` が NULL の場合は現在勤務中として扱われます。

### 3. ScanLogs (打刻生ログ)
カメラがQRコードを検知した「瞬間」をすべて記録します。監査ログとしての役割や、二重打刻防止の判定基準として利用されます。

## 💡 設計の工夫
* **ステータス管理**: `status` カラムを持つことで、「今誰が出勤中か」を即座にクエリ可能にしています。
* **履歴の永続性**: 直近の打刻ログだけでなく、すべてのスキャン履歴を残すことで、後からの遡及修正やトラブル時の調査を可能にしています。
