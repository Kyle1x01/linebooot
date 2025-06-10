import os
import openai
from linebot.models import TextSendMessage, FlexSendMessage, QuickReply, QuickReplyButton, MessageAction
from linebot.exceptions import LineBotApiError

def handle_price_query(line_bot_api, reply_token, user_id, product_model):
    """處理產品價格查詢"""
    try:
        # 調用GPT-4.1進行網絡搜索
        response = call_gpt_with_web_search(product_model)
        
        # 創建快速回覆按鈕，詢問是否添加到願望清單
        quick_reply = QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(label="添加到願望清單", text=f"添加到願望清單:{product_model}")
                ),
                QuickReplyButton(
                    action=MessageAction(label="不添加", text="不添加")
                )
            ]
        )
        
        # 回覆用戶
        try:
            line_bot_api.reply_message(
                reply_token,
                [
                    TextSendMessage(text=response),
                    TextSendMessage(text="是否要將此產品添加到願望清單？", quick_reply=quick_reply)
                ]
            )
        except LineBotApiError as api_error:
            print(f"LINE API Error in handle_price_query: {str(api_error)}")
    except Exception as e:
        error_message = f"查詢時發生錯誤：{str(e)}"
        try:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=error_message)
            )
        except LineBotApiError as api_error:
            print(f"LINE API Error in handle_price_query error handler: {str(api_error)}")

def call_gpt_with_web_search(product_model):
    """調用GPT-4.1進行網絡搜索並返回產品價格"""
    # 設定系統訊息
    system_message = """
    你是一個專業的3C產品價格查詢助手。請根據用戶提供的產品型號，提供該產品在台灣地區的最新價格信息。
    
    回覆要求：
    1. 只提供台灣地區的商品價格，使用新台幣（NT$）為單位
    2. 如果有多個版本或顏色，請列出各版本的價格
    3. 如果可能，提供不同通路的價格比較（如官網、電商平台等）
    4. 標明價格的來源和更新時間
    5. 如果找不到確切型號的價格，請明確說明並提供最相近型號的價格信息
    6. 盡可能的減少特殊字符 ex: ** | - 等 以換行做區隔
    7. 請盡可能的使用繁體中文回覆
    8. 不使用markdown格式輸出
    9. 128=>128GB 256=>256GB 512=>512GB 1TB=>1TB
    10. 重要：只回覆與3C產品（電腦、手機、平板、相機、耳機、智能手錶等電子產品）相關的內容
    11. 如果用戶查詢的不是3C產品，請回覆：「很抱歉，我只能提供3C電子產品的價格信息。請嘗試查詢電腦、手機、平板、相機、耳機、智能手錶等電子產品。」
    12. 在回答前，請先判斷查詢的產品是否為3C產品，如果不是，則回覆上述訊息
    
    """
    
    # 設定用戶訊息
    user_message = f"請提供{product_model}在台灣地區的最新價格信息"
    
    # 調用OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini-search-preview-2025-03-11",  # 使用支持網絡搜索的模型
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        web_search_options={},  # 啟用網絡搜索
        max_tokens=1000
    )
    
    # 提取回覆內容
    return response.choices[0].message.content