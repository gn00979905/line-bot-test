# 檔名: app.py
# 版本：從檔案讀取知識庫

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

# --- 修改部分 START ---

def load_knowledge_base(file_path='knowledge.md'):
    """從指定的檔案路徑讀取知識庫內容。"""
    try:
        # 使用 with open 確保檔案會被妥善關閉
        # encoding='utf-8' 對於讀取中文內容至關重要
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"錯誤：找不到知識庫檔案 {file_path}。請確保檔案存在於正確的路徑。")
        return "錯誤：找不到知識庫檔案。"
    except Exception as e:
        print(f"讀取知識庫檔案時發生錯誤：{e}")
        return f"錯誤：讀取知識庫時發生問題 - {e}"

# 在應用程式啟動時，從檔案載入知識庫內容
HR_KNOWLEDGE_BASE = load_knowledge_base()

# --- 修改部分 END ---


# 初始化 Flask 應用
app = Flask(__name__)

# 從「環境變數」讀取金鑰
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# 初始化 LINE Bot SDK
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
messaging_api = MessagingApi(ApiClient(configuration))

# 初始化 Gemini API
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    app.logger.error(f"Gemini API 初始化失敗：{e}")
    model = None

# Webhook 路由，這部分不變
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

# 訊息處理邏輯，除了知識庫來源改變外，其餘不變
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    user_message = event.message.text
    
    if model:
        try:
            # 建立一個包含指令、知識庫和使用者問題的完整 Prompt
            # 這裡的 HR_KNOWLEDGE_BASE 現在是從檔案讀取的內容
            system_instruction = f"""
            你是一位專業、友善的工作職掌交接的資訊助理，在工程師黃啟嘉不在的時候回答同事與主管工作相關問題。
            你的任務是根據下面提供的「黃啟嘉工作職掌與交接」來回答問題。
            請嚴格遵守以下規則：
            1. 只能根據提供的規章內容回答，不可以自己編造或從外部網路獲取資訊。
            2. 如果規章中沒有提到相關資訊，或問題與工作職掌無關，請禮貌地回答「關於您的問題，規章中沒有提到相關資訊，若有其他問題建議您直接洽詢黃啟嘉本人。」
            3. 回答問題時要簡潔、明確。
            4. 你的角色是黃啟嘉工作職掌與交接助理，請使用親切有禮的語氣。
            5. 不要一股腦的把所有的知識庫資料全部吐給使用者，只回答使用者問題的部分。譬如使用者問TTD就只回答TTD的部份，若使用者問黃啟嘉負責的專案，就只回答負責的專案名稱，而不要吐細節。

            ---
            黃啟嘉工作職掌交接:
            {HR_KNOWLEDGE_BASE}
            ---

            現在，請根據上面的工作職掌，回答以下問題：
            使用者問題: "{user_message}"
            """
            
            response = model.generate_content(system_instruction)
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

# 伺服器啟動部分，不變
# 這段是為了讓 Render 能正確啟動 Flask 應用，不再需要 ngrok
if __name__ == "__main__":
    # Render 會自動處理 port，我們監聽 0.0.0.0 即可
    # debug=True 在正式環境應設為 False，但為了方便初期除錯可先開著
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)

