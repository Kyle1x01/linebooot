import os
import openai
from linebot.models import TextSendMessage

def handle_product_query(line_bot_api, reply_token, product_model):
    """處理產品規格查詢"""
    try:
        # 調用GPT-4.1進行網絡搜索
        response = call_gpt_with_web_search(product_model)
        
        # 回覆用戶
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=response)
        )
    except Exception as e:
        error_message = f"查詢時發生錯誤：{str(e)}"
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=error_message)
        )

def call_gpt_with_web_search(product_model):
    """調用GPT-4.1進行網絡搜索並返回產品規格"""
    # 設定系統訊息
    system_message = """
    你是一個專業的3C產品規格查詢助手。請根據用戶提供的產品型號，提供該產品的詳細規格信息。
    
    回覆要求：
    1. 回覆必須控制在500字以內
    2. 只提供裝置規格信息，不要包含價格、評價或其他非規格信息
    3. 確保提供的是台灣發行版本的規格
    4. 格式應清晰易讀，可使用項目符號或表格形式
    5. 如果找不到確切型號，請明確說明並提供最相近型號的信息
    """
    
    # 設定用戶訊息
    user_message = f"請提供{product_model}的詳細規格信息"
    
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