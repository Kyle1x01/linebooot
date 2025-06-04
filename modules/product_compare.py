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

def handle_product_compare(line_bot_api, reply_token, input_text):
    """處理產品比較"""
    try:
        # 解析輸入的兩個產品型號
        products = [p.strip() for p in input_text.split(',')]
        
        if len(products) != 2:
            safe_reply_message(
                line_bot_api,
                reply_token,
                TextSendMessage(text="請輸入兩個產品型號，以逗號分隔。例如：iPhone 13, Samsung S21")
            )
            return
        
        # 調用GPT-4.1進行網絡搜索
        response = call_gpt_with_web_search(products[0], products[1])
        
        # 檢查回覆長度，確保不超過LINE API的限制
        if len(response) > 4500:  # 設置一個安全閾值，小於5000
            logger.warning(f"回覆訊息過長({len(response)}字元)，將被截斷")
            response = response[:4450] + "\n\n[訊息過長，已截斷]\n請嘗試比較更具體的產品型號。"
        
        # 回覆用戶
        safe_reply_message(
            line_bot_api,
            reply_token,
            TextSendMessage(text=response)
        )
    except Exception as e:
        error_message = f"比較時發生錯誤：{str(e)}"
        logger.error(error_message)
        safe_reply_message(
            line_bot_api,
            reply_token,
            TextSendMessage(text=error_message)
        )

def call_gpt_with_web_search(product1, product2):
    """調用GPT-4.1進行網絡搜索並返回產品比較"""
    try:
        # 設定系統訊息
        system_message = """
        你是一個專業的3C產品比較助手。請根據用戶提供的兩個產品型號，提供這兩個產品的詳細比較。
        
        回覆要求：
        1. 回覆必須控制在400字以內，避免超過LINE訊息長度限制
        2. 確保比較的是台灣發行版本的產品
        3. 比較應包括但不限於：性能、相機、電池、顯示屏、設計、價格等關鍵方面
        4. 使用表格或清晰的分類方式呈現比較結果
        5. 在比較的最後，根據不同使用場景給出簡短的建議
        6. 如果找不到確切型號，請明確說明並提供最相近型號的比較
        7. 盡可能的減少特殊字符 ex: ** 等 避免在line上排版不好
        8. 請盡可能的使用繁體中文回覆
        9. 優先引用製造商官網來源
        10.兩裝裝置以換行處理 範例： 處理器 :
                                     裝置1:處理器1
                                     裝置2:處理器2
        11.來源網址提供在最下方
        12.顯示屏==螢幕（避免使用中國名詞，使用台灣的名詞）
        13.請盡可能的使用繁體中文回覆
        """
        
        # 設定用戶訊息
        user_message = f"請比較{product1}和{product2}這兩款產品的優缺點和適用場景，請確保回覆簡潔且不超過4000字元"
        
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
        return f"比較產品時發生錯誤：{str(e)}"