from ._anvil_designer import SettingsFormTemplate
from anvil import *
import anvil.server
import anvil.users

class SettingsForm(SettingsFormTemplate):
  def __init__(self, **properties):
    # 初期化
    self.init_components(**properties)

    # 起動時に保存されているデータを読み込む
    self.load_settings()

  def load_settings(self):
    """データベースから現在の設定を読み出して画面に反映する"""
    user = anvil.users.get_user()
    if user:
      # クッキー情報の反映
      self.cookie_input.text = user['cookie_text'] if user['cookie_text'] else ""
      # 自動クリア設定の反映
      if user['auto_clear'] is not None:
        self.auto_clear_check.checked = user['auto_clear']
      else:
        self.auto_clear_check.checked = False

  @handle("back_btn", "click")
  def back_btn_click(self, **event_args):
    """「保存して戻る」ボタン：保存を実行してから戻る"""
    if self.execute_save():
      open_form('Form1')

  @handle("cancel_btn", "click")
  def cancel_btn_click(self, **event_args):
    """「保存せずに戻る」ボタン：何もせずメイン画面へ"""
    open_form('Form1')

  def execute_save(self):
    """【共通保存処理】クッキーと自動クリア設定をデータベースへ書き込む"""
    user = anvil.users.get_user()
    if not user:
      alert("ログインが必要です")
      return False

    # サーバー側の保存関数を呼び出し
    success = anvil.server.call('save_user_settings', 
                                self.cookie_input.text, 
                                self.auto_clear_check.checked)
    if not success:
      alert("保存に失敗しました。")
    return success