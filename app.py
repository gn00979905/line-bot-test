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

# --- 新增部分 START ---

# 建立 A 公司的 HR 規章知識庫
# 未來您可以將這裡的內容換成您自己公司的真實資料
# 用 """ 三個引號可以建立多行文字
HR_KNOWLEDGE_BASE = """
# A公司 HR 內部規章

## 關於請假

### 特休 (Annual Leave)
- 到職滿半年，享有3天特休。
- 到職滿一年，享有7天特休。
- 到職滿二年，享有10天特休。
- 之後每滿一年，加給1天，最多加至30天為止。

### 病假 (Sick Leave)
- 一年內未住院者，合計不得超過三十日。
- 普通傷病假一年內未超過三十日部分，工資折半發給。

## 關於服裝儀容 (Dress Code)
- 週一至週四，請穿著商務休閒服裝 (Business Casual)。
- 週五為便服日，但仍需保持整潔得體，不可穿著拖鞋、短褲。

## 關於報銷 (Reimbursement)
- 所有因公支出，請於發生後一個月內，憑發票實報實銷。
- 搭乘計程車需註明事由與起訖地點。
"""

# --- 新增部分 END ---

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
          # --- 修改部分 START ---
            
            # 建立一個包含指令、知識庫和使用者問題的完整 Prompt
            system_instruction = f"""
            你是一位專業、友善的「A公司」HR資訊助理。
            你的任務是根據下面提供的「A公司 HR 內部規章」來回答問題。
            請嚴格遵守以下規則：
            1. 只能根據提供的規章內容回答，不可以自己編造或從外部網路獲取資訊。
            2. 如果規章中沒有提到相關資訊，或問題與A公司無關，請禮貌地回答「關於您的問題，規章中沒有提到相關資訊，建議您直接洽詢HR部門。」
            3. 回答問題時要簡潔、明確。
            4. 你的角色是HR助理，請使用親切有禮的語氣。

            ---
            A公司 HR 內部規章:
            {HR_KNOWLEDGE_BASE}
            ---

            現在，請根據上面的規章內容，回答以下問題：
            使用者問題: "{user_message}"
            """
            
            # 將完整的 Prompt 送給 Gemini
            response = model.generate_content(system_instruction)
            gemini_reply = response.text
            
            # --- 修改部分 END ---
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
