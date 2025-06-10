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
    6. 如果可能，請在最後提供排行的來源和更新時間
    7. 盡可能的減少特殊字符 ex: ** | - 等 以換行做區隔
    8. 請盡可能的使用繁體中文回覆 
    9. 來源網址提供在回覆的最下方，必免中斷閱讀體驗，且確保能夠準確提供網址
    10. 重要：只回覆與3C產品（電腦、手機、平板、相機、耳機、智能手錶等電子產品）相關的內容
    11. 如果用戶查詢的不是3C產品，請回覆：「很抱歉，我只能提供3C電子產品的排行榜信息。請嘗試查詢電腦、手機、平板、相機、耳機、智能手錶等電子產品。」
    12. 在回答前，請先判斷查詢的產品是否為3C產品，如果不是，則回覆上述訊息
    """
    
    # 設定用戶訊息
    user_message = f"請提供台灣地區最熱門的前五名{product_type}排行榜"
    
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