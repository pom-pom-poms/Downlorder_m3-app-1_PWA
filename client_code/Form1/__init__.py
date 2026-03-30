from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.js
import anvil.users

class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.current_url = None
    # 初期状態にリセット
    self.reset_download_button()
    self.check_login_status()

  def check_login_status(self):
    user = anvil.users.get_user()
    if user:
      # ボタンは「ログアウト」のみ
      self.login_btn.text = "ログアウト"
      self.settings_btn.visible = True
      # アカウント名は別ラベルに表示
      self.account_label.text = user['email']
      self.account_label.visible = True
    else:
      self.login_btn.text = "ログイン / 登録"
      self.settings_btn.visible = False
      self.account_label.text = ""
      self.account_label.visible = False

  @handle("login_btn", "click")
  def login_btn_click(self, **event_args):
    if anvil.users.get_user():
      if confirm("ログアウトしますか？"):
        anvil.users.logout()
    else:
      anvil.users.login_with_form(allow_cancel=True)
    self.check_login_status()

  def settings_btn_click(self, **event_args):
    open_form('SettingsForm')

  def url_input_change(self, **event_args):
    if not self.url_input.text:
      self.reset_download_button()

  @handle("clear_btn", "click")
  def clear_btn_click(self, **event_args):
    self.url_input.text = ""
    self.reset_download_button()

  def reset_download_button(self):
    """ボタンを『解析開始』の状態（青）に戻す"""
    self.download_btn.text = "解析開始"
    self.download_btn.icon = "fa:search"
    self.download_btn.background = "#2196F3"
    self.download_btn.foreground = "#ffffff"
    self.download_btn.enabled = True
    self.current_url = None
    self.format_dropdown.items = []
    self.title_label.text = ""

  def btn_test(self, **event_args):
    url = self.url_input.text
    # すでに解析済みで、保存ボタンとして押された場合
    if self.current_url == url and self.format_dropdown.selected_value:
      video_url = self.format_dropdown.selected_value
      anvil.js.window.open(video_url)
      user = anvil.users.get_user()
      if user and user['auto_clear']:
        self.url_input.text = ""
        self.reset_download_button()
      return
    # 解析を開始
    self.start_analysis(url)

  def start_analysis(self, url):
    if not url:
      alert("URLを入力してください")
      return

    # 解析中（濃い青）
    self.download_btn.text = "解析中..."
    self.download_btn.icon = "fa:spinner"
    self.download_btn.background = "#1976D2"
    self.download_btn.enabled = False

    user = anvil.users.get_user()
    cookie_data = user['cookie_text'] if user and user['cookie_text'] else ""

    try:
      result = anvil.server.call('get_video_info', url, cookie_data)
      if 'error' in result:
        alert(f"解析エラー: {result['error']}")
        self.reset_download_button()
      else:
        # 解析成功（緑）
        self.title_label.text = "動画タイトル: " + result['title']
        self.format_dropdown.items = result['formats']
        self.current_url = url
        self.download_btn.text = "ダウンロード" # 表記を短縮
        self.download_btn.icon = "fa:download"
        self.download_btn.background = "#4CAF50"
    except Exception as e:
      alert(f"システムエラー: {str(e)}")
      self.reset_download_button()

    self.download_btn.enabled = True