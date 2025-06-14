import os
import openai
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

def handle_product_review(line_bot_api, reply_token, product_model):
    """處理產品評價"""
    try:
        # 調用GPT-4.1進行網絡搜索
        response = call_gpt_with_web_search(product_model)
        
        # 回覆用戶
        try:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=response)
            )
        except LineBotApiError as api_error:
            print(f"LINE API Error in handle_product_review: {str(api_error)}")
    except Exception as e:
        error_message = f"查詢評價時發生錯誤：{str(e)}"
        try:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=error_message)
            )
        except LineBotApiError as api_error:
            print(f"LINE API Error in handle_product_review error handler: {str(api_error)}")

def call_gpt_with_web_search(product_model):
    """調用GPT-4.1進行網絡搜索並返回產品評價"""
    # 設定系統訊息
    system_message = """
    你是一個專業的3C產品評價助手。請根據用戶提供的產品型號，提供該產品的專業評價摘要。
    
    回覆要求：
    1. 回覆必須控制在500字以內且使用繁體中文回覆
    2. 確保評價針對的是台灣發行版本的產品
    3. 評價應包括產品的優點和缺點
    4. 評價應基於專業測評和用戶反饋
    5. 在回覆的最後，提供兩個專業評測的網頁鏈結
    6. 如果找不到確切型號的評價，請明確說明並提供最相近型號的評價
    7. 盡可能的減少特殊字符 ex: ** | - 等 以換行做區隔
    9. 重要：只回覆與3C產品（電腦、手機、平板、相機、耳機、智能手錶等電子產品）相關的內容
    10. 如果用戶查詢的不是3C產品，請回覆：「很抱歉，我只能提供3C電子產品的評價信息。請嘗試查詢電腦、手機、平板、相機、耳機、智能手錶等電子產品。」
    11. 在回答前，請先判斷查詢的產品是否為3C產品，如果不是，則回覆上述訊息
    """
    
    # 設定用戶訊息
    user_message = f"請提供{product_model}的專業評價摘要和兩個專業評測的網頁鏈結"
    
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