import os
import openai
from linebot.models import TextSendMessage

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
        
        # 回覆用戶
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=response)
        )
    except Exception as e:
        error_message = f"推薦時發生錯誤：{str(e)}"
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=error_message)
        )

def call_gpt_with_web_search(user_requirements, device_type=None):
    """調用GPT-4.1進行網絡搜索並返回產品推薦"""
    # 設定系統訊息
    system_message = """
    你是一個專業的3C產品推薦助手。請根據用戶提供的需求和預算，推薦最適合的產品。
    
    回覆要求：
    1. 回覆必須控制在500字以內
    2. 只推薦台灣發行版本的產品
    3. 推薦應基於用戶的具體需求和預算
    4. 每個推薦產品應包含簡短的規格說明和推薦理由
    5. 推薦3-5款不同價位或不同品牌的產品，以供用戶選擇
    6. 如果用戶預算不足以滿足需求，應誠實說明並提供最接近的選擇
    """
    
    # 設定用戶訊息
    if device_type:
        user_message = f"請推薦適合的{device_type}，根據以下需求和預算：{user_requirements}"
    else:
        user_message = f"根據以下需求和預算，請推薦適合的3C產品：{user_requirements}"
    
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