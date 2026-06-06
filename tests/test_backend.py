import pytest

def test_in_app_index(in_client):
    """
    [バックエンド・ユニットテスト]
    出勤アプリのトップページ (/) が正常に表示されるか (ステータスコード 200 OK) を確認します。
    """
    response = in_client.get('/')
    assert response.status_code == 200


def test_add_user_form(in_client):
    """
    [バックエンド・統合テスト]
    ユーザー登録APIにPOSTした際、正しくデータが処理されるかを確認します。
    ブラウザを介さず、Pythonのコードレベルで直接検証します。（超高速）
    """
    # 仮の社員データで登録リクエストを送信
    response = in_client.post('/add_user', data={
        "user_id": "BACKEND_001",
        "user_name": "バックエンド・テスト太郎"
    })
    
    # ページの中に「登録完了」の文字が出力されているか確認
    response_text = response.data.decode('utf-8')
    assert "登録完了" in response_text
    assert "バックエンド・テスト太郎" in response_text

def test_add_user_duplicate_error(in_client):
    """
    [バックエンド・異常系テスト]
    同じIDで登録しようとしたとき、エラーメッセージが返るかをテストします。
    """
    # 1回目：正常登録
    in_client.post('/add_user', data={"user_id": "BACKEND_002", "user_name": "太郎"})
    
    # 2回目：同じIDで登録！
    response = in_client.post('/add_user', data={"user_id": "BACKEND_002", "user_name": "次郎"})
    response_text = response.data.decode('utf-8')
    
    # データベースの予約エラー(すでに登録されています)が出るはず
    assert "すでに登録されています" in response_text
