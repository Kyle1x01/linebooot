import os
import json
import re
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
import openai
from dotenv import load_dotenv
from modules.product_query import handle_product_query
from modules.price_query import handle_price_query
from modules.product_compare import handle_product_compare
from modules.product_recommend import handle_product_recommend
from modules.popular_ranking import handle_popular_ranking
from modules.product_review import handle_product_review
from modules.wishlist import add_to_wishlist, view_wishlist, remove_from_wishlist, clear_wishlist
from modules.user_state import UserState

# 載入環境變數
load_dotenv()

app = Flask(__name__)

# 設定Line Bot API
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

# 設定OpenAI API
openai.api_key = os.environ.get('OPENAI_API_KEY')

# 用戶狀態管理
user_states = {}

@app.route("/callback", methods=['POST'])
def callback():
    # 獲取 X-Line-Signature 頭部值
    signature = request.headers['X-Line-Signature']

    # 獲取請求體內容
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 處理 webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text
    
    # 初始化用戶狀態（如果不存在）
    if user_id not in user_states:
        user_states[user_id] = UserState()
    
    user_state = user_states[user_id]
    
    # 處理「離開」指令 - 重置用戶狀態
    if text == "離開":
        user_state.reset()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="已退出當前功能。輸入「說明」查看可用指令。")
        )
        return
    
    # 處理「說明」指令
    if text == "說明":
        help_message = get_help_message()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=help_message)
        )
        return
    
    # 處理願望清單相關指令
    if text == "查看我的車車":
        view_wishlist(line_bot_api, event.reply_token, user_id)
        return
    
    if text.startswith("移除"):
        product_name = text[2:].strip()
        remove_from_wishlist(line_bot_api, event.reply_token, user_id, product_name)
        return
    
    if text == "清空購物車":
        clear_wishlist(line_bot_api, event.reply_token, user_id)
        return
    
    # 根據用戶當前狀態處理輸入
    if user_state.waiting_for_input:
        handle_user_input(event, user_state, text)
        return
    
    # 處理功能選擇
    if text == "查詢裝置":
        user_state.set_state("product_query", waiting_for_input=True)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入您想查詢的裝置型號：")
        )
    elif text == "我想查詢價格":
        user_state.set_state("price_query", waiting_for_input=True)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入您想查詢價格的裝置型號：")
        )
    elif text == "大車拼":
        user_state.set_state("product_compare", waiting_for_input=True)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入您想比較的兩種裝置型號，以逗號分隔：")
        )
    elif text == "求推薦":
        user_state.set_state("product_recommend_type", waiting_for_input=True)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入您想推薦的裝置類型（例如：手機、筆電、耳機等）：")
        )
    elif text == "金榜題名":
        user_state.set_state("popular_ranking", waiting_for_input=True)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入您想查詢的產品類型（例如：手機）：")
        )
    elif text == "評價大師":
        user_state.set_state("product_review", waiting_for_input=True)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請輸入您想查詢評價的裝置型號：")
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我不明白您的指令。請輸入「說明」查看可用功能。")
        )

def handle_user_input(event, user_state, text):
    """根據用戶當前狀態處理輸入"""
    if user_state.current_state == "product_query":
        handle_product_query(line_bot_api, event.reply_token, text)
    elif user_state.current_state == "price_query":
        handle_price_query(line_bot_api, event.reply_token, event.source.user_id, text)
    elif user_state.current_state == "product_compare":
        handle_product_compare(line_bot_api, event.reply_token, text)
    elif user_state.current_state == "product_recommend_type":
        # 保存裝置類型到上下文
        user_state.set_context("device_type", text)
        # 更新狀態為等待需求和預算
        user_state.set_state("product_recommend", waiting_for_input=True)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"請輸入您對{text}的需求和預算：")
        )
    elif user_state.current_state == "product_recommend":
        handle_product_recommend(line_bot_api, event.reply_token, text, event.source.user_id)
    elif user_state.current_state == "popular_ranking":
        handle_popular_ranking(line_bot_api, event.reply_token, text)
    elif user_state.current_state == "product_review":
        handle_product_review(line_bot_api, event.reply_token, text)
    
    # 重置用戶狀態
    user_state.reset()

def get_help_message():
    """返回幫助訊息"""
    return """🤖 3C小助手功能說明：

1. 產品規格查詢: 輸入「查詢裝置」
2. 產品價格查詢: 輸入「我想查詢價格」
3. 產品比較: 輸入「大車拼」
4. 推薦產品: 輸入「求推薦」
5. 熱門排行: 輸入「金榜題名」
6. 產品評價: 輸入「評價大師」

🛒 願望清單功能：
- 查看: 輸入「查看我的車車」
- 移除: 輸入「移除+產品名稱」
- 清空: 輸入「清空購物車」

❓ 其他指令：
- 「說明」- 顯示此說明
- 「離開」- 終止目前程序"""

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)