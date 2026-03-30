import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import yt_dlp
import tempfile
import os

@anvil.server.callable
def get_video_info(url, cookie_text=None):
  ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'format': 'all', 
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  }

  tmp_cookie = None
  if cookie_text and len(cookie_text) > 10:
    tmp_cookie = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt', encoding='utf-8')
    tmp_cookie.write(cookie_text)
    tmp_cookie.close()
    ydl_opts['cookiefile'] = tmp_cookie.name

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=False)
      formats = info.get('formats', [])

      max_height = max([f.get('height') or 0 for f in formats]) if formats else 0

      formats_data = []
      for f in formats:
        f_url = f.get('url')
        if not f_url: continue

        height = f.get('height') or 0
        res_label = f.get('resolution') or f'{height}p' if height else "Unknown"
        ext = f.get('ext', 'unknown')
        has_v = f.get('vcodec') != 'none'
        has_a = f.get('acodec') != 'none'

        if has_v and has_a and height == max_height and height > 0:
          score = 10000 
          label = f"⭐ 最高品質: {res_label} ({ext})"
        elif has_a and not has_v:
          score = 8000
          label = f"🎵 音声のみ ({ext})"
        elif has_v and has_a:
          score = 5000 - height
          label = f"🎬 動画: {res_label} ({ext})"
        elif has_v:
          score = 1000 - height
          label = f"🎬 映像のみ: {res_label} ({ext})" # 「無音」から「映像のみ」に変更
        else:
          continue

        formats_data.append({'label': label, 'url': f_url, 'score': score})

      if not formats_data:
        return {'error': '保存可能な形式が見つかりませんでした。'}

      sorted_formats = sorted(formats_data, key=lambda x: x['score'], reverse=True)
      unique_formats = []
      seen_labels = set()
      for f in sorted_formats:
        if f['label'] not in seen_labels:
          unique_formats.append((f['label'], f['url']))
          seen_labels.add(f['label'])

      return {'title': info.get('title', 'video'), 'formats': unique_formats}
  except Exception as e:
    return {'error': str(e)}
  finally:
    if tmp_cookie and os.path.exists(tmp_cookie.name):
      try: os.remove(tmp_cookie.name)
      except: pass

@anvil.server.callable
def save_user_settings(cookie_text, auto_clear):
  user = anvil.users.get_user()
  if user:
    user['cookie_text'] = cookie_text
    user['auto_clear'] = auto_clear
    return True
  return False