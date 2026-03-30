from ._anvil_designer import Form0Template
from anvil import *
import anvil.server
import anvil.js
import anvil.users

class Form0(Form0Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.current_url = None
    self.check_login_status()

  def check_login_status(self):
    """ログイン状態に応じて表示を切り替える"""
    user = anvil.users.get_user()
    if user:
      self.login_btn.text = f"ログアウト ({user['email']})"
      self.settings_btn.visible = True
    else:
      self.login_btn.text = "ログイン / 登録"
      self.settings_btn.visible = False

  @handle("login_btn", "click")
  def login_btn_click(self, **event_args):
    """ログインボタン処理"""
    if anvil.users.get_user():
      if confirm("ログアウトしますか？"):
        anvil.users.logout()
    else:
      anvil.users.login_with_form(allow_cancel=True)
    self.check_login_status()

  def settings_btn_click(self, **event_args):
    """設定画面へ切り替え"""
    open_form('SettingsForm')

  def url_input_change(self, **event_args):
    """手動でURLが消されたら初期状態に戻す"""
    if not self.url_input.text:
      self.reset_download_button()

  @handle("clear_btn", "click")
  def clear_btn_click(self, **event_args):
    """クリアボタン：すべてをリセット"""
    self.url_input.text = ""
    self.reset_download_button()

  def reset_download_button(self):
    """表示を完全に初期状態に戻す"""
    self.download_btn.text = "解析開始"
    self.download_btn.enabled = True
    self.current_url = None
    self.format_dropdown.items = []
    self.title_label.text = ""

  def btn_test(self, **event_args):
    """解析・ダウンロード実行"""
    url = self.url_input.text

    # 【ここを修正】既に解析済みURLと一致し、保存を実行する場合
    if self.current_url == url and self.format_dropdown.selected_value:
      video_url = self.format_dropdown.selected_value
      # ダウンロード実行
      anvil.js.window.open(video_url)

      # 保存が成功した「後」に、自動クリア設定を確認してリセット
      user = anvil.users.get_user()
      if user and user['auto_clear']:
        self.url_input.text = ""
        self.reset_download_button()

      return

    # 未解析なら解析を開始
    self.start_analysis(url)

  def start_analysis(self, url):
    """動画解析処理"""
    if not url:
      alert("URLを入力してください")
      return

    self.download_btn.text = "解析中..."
    self.download_btn.enabled = False

    user = anvil.users.get_user()
    cookie_data = user['cookie_text'] if user and user['cookie_text'] else ""

    try:
      result = anvil.server.call('get_video_info', url, cookie_data)

      if 'error' in result:
        alert(f"解析エラー: {result['error']}")
        self.reset_download_button()
      else:
        # 解析成功時は、URLもタイトルも「表示したまま」にする（保存ボタンで照合するため）
        self.title_label.text = "動画タイトル: " + result['title']
        self.format_dropdown.items = result['formats']
        self.current_url = url
        self.download_btn.text = "ダウンロード（保存）"

    except Exception as e:
      alert(f"システムエラー: {str(e)}")
      self.reset_download_button()

    self.download_btn.enabled = True