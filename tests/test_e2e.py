import pytest
from playwright.sync_api import Page, expect

def test_user_registration_e2e(page: Page, live_server_in_app):
    """
    [E2Eテスト（Playwright）]
    実際のブラウザ(Chromium等)を立ち上げ、ユーザーと同じように入力・クリックを行います。
    live_server_in_app というFixtureにより、裏でテスト用Flaskサーバーが自動で動きます。
    """
    # 1. バックグラウンドで起動したアプリの社員登録ページへアクセス
    page.goto(f"{live_server_in_app}/add_user")
    
    # 2. テキストボックスに入力 (name属性で対象を指定)
    page.fill("input[name='user_id']", "E2E_001")
    page.fill("input[name='user_name']", "E2E・自動操作テスト君")
    
    # 3. 登録ボタンをクリック
    page.click("button[type='submit']")
    
    # 4. 画面上に指定のメッセージが表示されているか検証
    # （DOMに現れるまでPlaywrightが自動で待機してくれます）
    expect(page.locator(".status.success")).to_contain_text("登録完了")
    expect(page.locator(".status.success")).to_contain_text("E2E・自動操作テスト君")
