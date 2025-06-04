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

def handle_product_recommend(line_bot_api, reply_token, input_text, user_id=None):
    """處理產品推薦"""
    try:
        # 從用戶狀態獲取裝置類型
        device_type = None
        if user_id:
            from app import user_states
            if user_id in user_states:
                device_type = user_states[user_id].get_context("device_type")
        
        # 調用GPT-4.1進行網絡搜索
        response = call_gpt_with_web_search(input_text, device_type)
        
        # 檢查回覆長度，確保不超過LINE API的限制
        if len(response) > 4500:  # 設置一個安全閾值，小於5000
            logger.warning(f"回覆訊息過長({len(response)}字元)，將被截斷")
            response = response[:4450] + "\n\n[訊息過長，已截斷]\n請嘗試提供更具體的需求和預算。"
        
        # 回覆用戶
        safe_reply_message(
            line_bot_api,
            reply_token,
            TextSendMessage(text=response)
        )
    except Exception as e:
        error_message = f"推薦時發生錯誤：{str(e)}"
        logger.error(error_message)
        safe_reply_message(
            line_bot_api,
            reply_token,
            TextSendMessage(text=error_message)
        )

def call_gpt_with_web_search(user_requirements, device_type=None):
    """調用GPT-4.1進行網絡搜索並返回產品推薦"""
    try:
        # 設定系統訊息
        system_message = """
        你是一個專業的3C產品推薦助手。請根據用戶提供的需求和預算，推薦最適合的產品。
        
        回覆要求：
        1. 回覆必須控制在400字以內，避免超過LINE訊息長度限制
        2. 只推薦台灣發行版本的產品
        3. 推薦應基於用戶的具體需求和預算
        4. 每個推薦產品應包含簡短的規格說明和推薦理由
        5. 推薦3-5款不同價位或不同品牌的產品，以供用戶選擇
        6. 如果用戶預算不足以滿足需求，應誠實說明並提供最接近的選擇
        7. 盡可能的減少特殊字符 ex: ** 等 避免在line上排版不好
        8. 請確保回覆總長度不超過4000字元
        """
        
        # 設定用戶訊息
        if device_type:
            user_message = f"請推薦適合的{device_type}，根據以下需求和預算：{user_requirements}，請確保回覆簡潔且不超過4000字元"
        else:
            user_message = f"根據以下需求和預算，請推薦適合的3C產品：{user_requirements}，請確保回覆簡潔且不超過4000字元"
        
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
        return f"推薦產品時發生錯誤：{str(e)}"