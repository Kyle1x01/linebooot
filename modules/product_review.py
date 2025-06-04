import os
import openai
import logging
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

# 設置日誌
logger = logging.getLogger(__name__)

# 安全回覆訊息的函數
def safe_reply_message(line_bot_api, reply_token, messages):
    """安全地回覆訊息，處理可能的LineBotApiError"""
    try:
        line_bot_api.reply_message(reply_token, messages)
        return True
    except LineBotApiError as e:
        logger.error(f"LINE API 錯誤: {e}")
        # 如果是無效的reply token，記錄但不重試
        if "Invalid reply token" in str(e):
            logger.warning("回覆令牌無效，可能已過期或已使用")
        return False
    except Exception as e:
        logger.error(f"發送訊息時發生錯誤: {e}")
        return False

def handle_product_review(line_bot_api, reply_token, product_model):
    """處理產品評價"""
    try:
        # 調用GPT-4.1進行網絡搜索
        response = call_gpt_with_web_search(product_model)
        
        # 檢查回覆長度，確保不超過LINE API的限制
        if len(response) > 4500:  # 設置一個安全閾值，小於5000
            logger.warning(f"回覆訊息過長({len(response)}字元)，將被截斷")
            response = response[:4450] + "\n\n[訊息過長，已截斷]\n請嘗試查詢更具體的產品型號。"
        
        # 回覆用戶
        safe_reply_message(
            line_bot_api,
            reply_token,
            TextSendMessage(text=response)
        )
    except Exception as e:
        error_message = f"查詢評價時發生錯誤：{str(e)}"
        logger.error(error_message)
        safe_reply_message(
            line_bot_api,
            reply_token,
            TextSendMessage(text=error_message)
        )

def call_gpt_with_web_search(product_model):
    """調用GPT-4.1進行網絡搜索並返回產品評價"""
    try:
        # 設定系統訊息
        system_message = """
        你是一個專業的3C產品評價助手。請根據用戶提供的產品型號，提供該產品的專業評價摘要。
        
        回覆要求：
        1. 回覆必須控制在400字以內，避免超過LINE訊息長度限制
        2. 確保評價針對的是台灣發行版本的產品
        3. 評價應包括產品的優點和缺點
        4. 評價應基於專業測評和用戶反饋
        5. 在回覆的最後，提供兩個專業評測的網頁鏈結
        6. 如果找不到確切型號的評價，請明確說明並提供最相近型號的評價
        7. 盡可能的減少特殊字符 ex: ** 等 避免在line上排版不好
        8. 請確保回覆總長度不超過4000字元
        """
        
        # 設定用戶訊息
        user_message = f"請提供{product_model}的專業評價摘要和兩個專業評測的網頁鏈結，請確保回覆簡潔且不超過4000字元"
        
        # 調用OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini-search-preview-2025-03-11",  # 使用支持網絡搜索的模型
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            web_search_options={},  # 啟用網絡搜索
            max_tokens=800  # 減少token數量以控制回覆長度
        )
        
        # 提取回覆內容
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"調用GPT時發生錯誤：{str(e)}")
        return f"查詢評價時發生錯誤：{str(e)}"