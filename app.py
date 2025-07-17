import os
from flask import Flask, request, abort

# 載入 LINE Bot & Gemini 相關套件
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import google.generativeai as genai

# 初始化 Flask 應用
app = Flask(__name__)

# --- 程式碼修改處 START ---

# 從「環境變數」讀取金鑰，而不是 Colab Secrets
# Render 會在它的平台上讓我們設定這些變數
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# --- 程式碼修改處 END ---

# 初始化 LINE Bot SDK
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
messaging_api = MessagingApi(ApiClient(configuration))

# 初始化 Gemini API
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    # 如果初始化失敗，在日誌中記錄錯誤
    app.logger.error(f"Gemini API 初始化失敗：{e}")
    model = None

# Webhook 路由，這部分和 Colab 版本完全相同
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 訊息處理邏輯，這部分也和 Colab 版本完全相同
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    user_message = event.message.text
    if model:
        try:
            response = model.generate_content(user_message)
            gemini_reply = response.text
        except Exception as e:
            app.logger.error(f"呼叫 Gemini API 時發生錯誤: {e}")
            gemini_reply = "抱歉，我現在有點忙，請稍後再試。"
    else:
        gemini_reply = "抱歉，後端 AI 服務未啟動，請聯繫管理員。"

    messaging_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=gemini_reply)]
        )
    )

# --- 程式碼修改處 START ---
# 這段是為了讓 Render 能正確啟動 Flask 應用，不再需要 ngrok
if __name__ == "__main__":
    # Render 會自動處理 port，我們監聽 0.0.0.0 即可
    # debug=True 在正式環境應設為 False，但為了方便初期除錯可先開著
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
# --- 程式碼修改處 END ---
