import os
import openai
from linebot.models import TextSendMessage

def handle_popular_ranking(line_bot_api, reply_token, product_type):
    """處理熱門排行"""
    try:
        # 調用GPT-4.1進行網絡搜索
        response = call_gpt_with_web_search(product_type)
        
        # 回覆用戶
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=response)
        )
    except Exception as e:
        error_message = f"查詢排行時發生錯誤：{str(e)}"
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=error_message)
        )

def call_gpt_with_web_search(product_type):
    """調用GPT-4.1進行網絡搜索並返回熱門排行"""
    # 設定系統訊息
    system_message = """
    你是一個專業的3C產品排行榜助手。請根據用戶提供的產品類型，提供台灣地區最熱門的前五名產品排行。
    
    回覆要求：
    1. 只提供台灣地區的商品排行
    2. 價格必須使用新台幣（NT$）為單位
    3. 每個產品應包含簡短的規格亮點和價格區間
    4. 排行應基於最新的市場數據
    5. 只列出前五名產品
    6. 如果可能，標明排行的來源和更新時間
    """
    
    # 設定用戶訊息
    user_message = f"請提供台灣地區最熱門的前五名{product_type}排行榜"
    
    # 調用OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4o-search-preview",  # 使用支持網絡搜索的模型
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        web_search_options={},  # 啟用網絡搜索
        max_tokens=1000
    )
    
    # 提取回覆內容
    return response.choices[0].message.content