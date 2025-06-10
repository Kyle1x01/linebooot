import os
import openai
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

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
        try:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=response)
            )
        except LineBotApiError as api_error:
            print(f"LINE API Error when replying: {str(api_error)}")
    except Exception as e:
        error_message = f"推薦時發生錯誤：{str(e)}"
        try:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=error_message)
            )
        except LineBotApiError as api_error:
            print(f"LINE API Error in error handler: {str(api_error)}")

def call_gpt_with_web_search(user_requirements, device_type=None):
    """調用GPT-4.1進行網絡搜索並返回產品推薦"""
    try:
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
        7. 盡可能的減少特殊字符 ex: ** | - 等 
        8. 請盡可能的使用繁體中文回覆
        9. 優先引用製造商官網來源
        11.來源網址提供在回覆的最下方，必免中斷閱讀體驗，且確保能夠準確提供網址
        12.顯示屏==螢幕（避免使用中國名詞，使用台灣的名詞）
        13.重要：只回覆與3C產品（電腦、手機、平板、相機、耳機、智能手錶等電子產品）相關的內容
        14.如果用戶查詢的不是3C產品，請回覆：「很抱歉，我只能提供3C電子產品的推薦信息。請嘗試查詢電腦、手機、平板、相機、耳機、智能手錶等電子產品。」
        15.在回答前，請先判斷查詢的產品是否為3C產品，如果不是，則回覆上述訊息
        16.重要：請務必推薦多款不同品牌和價位的產品，不要只推薦單一產品（如iPhone 16 Pro）
        17.對於手機類產品，請至少推薦3種不同的產品（如Apple、Samsung、Google等）
        """
        
        # 設定用戶訊息
        if device_type:
            # 確保查詢明確要求多樣化推薦
            user_message = f"請推薦適合的{device_type}，根據以下需求和預算：{user_requirements}。請提供至少3種不同品牌的選擇。請先判斷{device_type}是否為3C產品，如果不是，請回覆相應的錯誤訊息。"
        else:
            user_message = f"根據以下需求和預算，請推薦適合的3C產品：{user_requirements}。請提供至少3種不同品牌的選擇。請先判斷是否為3C產品相關查詢，如果不是，請回覆相應的錯誤訊息。"
        
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
        content = response.choices[0].message.content
        
        # 檢查回覆是否包含實際的產品推薦
        if len(content.strip()) < 50 or "推薦" not in content:
            # 回覆內容太短或不包含推薦，可能是模型沒有正確理解請求
            return f"您查詢的是{device_type if device_type else '3C產品'}推薦，為了提供更精準的建議，請提供以下資訊：\n\n1. 您的預算範圍（例如：10000-20000元）\n2. 您的主要使用需求（例如：攝影、遊戲、工作等）\n3. 您偏好的品牌或特定功能（如有）\n\n有了這些資訊，我們能為您推薦更符合需求的產品選擇。"
        
        return content
    except Exception as e:
        print(f"Error in call_gpt_with_web_search: {str(e)}")
        return f"很抱歉，系統暫時無法處理您的請求。請稍後再試或提供更詳細的資訊。錯誤：{str(e)}"