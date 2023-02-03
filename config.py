'''
  OpenAi ChatGPT session, You can find the session token manually from your browser:

  1. Go to https://chat.openai.com/api/auth/session
  2. Press F12 to open console
  3. Go to Application > Cookies
  4. Copy the session token value in __Secure-next-auth.session-token
'''
GPT_SESSION = ''

'''
  DingTalk bot app_secret
'''
APP_SECRET = ''

__all__ = [
  GPT_SESSION,
  APP_SECRET,
]
