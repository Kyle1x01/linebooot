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
        
        # 檢查裝置類型是否為3C產品
        if device_type and not is_3c_product(device_type):
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="很抱歉，我只能提供3C電子產品的推薦信息。請嘗試查詢電腦、手機、平板、相機、耳機、智能手錶等電子產品。")
            )
            return
        
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

# 檢查是否為3C產品
def is_3c_product(device_type):
    """檢查裝置類型是否為3C產品"""
    # 定義3C產品類型列表
    c3_products = [
        "手機", "電腦", "筆電", "平板", "相機", "耳機", "智能手錶", "智慧手錶", "手表", "手錶",
        "電視", "顯示器", "螢幕", "鍵盤", "滑鼠", "音箱", "喇叭", "投影機", "印表機", "掃描儀",
        "路由器", "充電器", "行動電源", "攝影機", "麥克風", "遊戲機", "主機", "配件", "3c", "電子產品"
    ]
    
    # 檢查裝置類型是否在3C產品列表中
    for product in c3_products:
        if product in device_type.lower():
            return True
    
    return False

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
    7. 盡可能的減少特殊字符 ex: ** | - 等 
    8. 請盡可能的使用繁體中文回覆
    9. 優先引用製造商官網來源
    11.來源網址提供在回覆的最下方，必免中斷閱讀體驗，且確保能夠準確提供網址
    12.顯示屏==螢幕（避免使用中國名詞，使用台灣的名詞）
    13.重要：只回覆與3C產品（電腦、手機、平板、相機、耳機、智能手錶等電子產品）相關的內容
    14.如果用戶查詢的不是3C產品，請回覆：「很抱歉，我只能提供3C電子產品的推薦信息。請嘗試查詢電腦、手機、平板、相機、耳機、智能手錶等電子產品。」
    15.在回答前，請先判斷查詢的產品是否為3C產品，如果不是，則回覆上述訊息
    16.重要：請務必推薦多款不同品牌和價位的產品，不要只推薦單一產品（如iPhone 16 Pro）
    17.對於手機類產品，請至少推薦3種不同品牌的產品（如Apple、Samsung、Google等）
    """
    
    # 設定用戶訊息
    if device_type:
        # 確保查詢明確要求多樣化推薦
        user_message = f"請推薦適合的{device_type}，根據以下需求和預算：{user_requirements}。請提供至少3種不同品牌的選擇。"
    else:
        user_message = f"根據以下需求和預算，請推薦適合的3C產品：{user_requirements}。請提供至少3種不同品牌的選擇。"
    
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
    
    # 檢查回覆是否包含非3C產品的錯誤訊息
    if "很抱歉，我只能提供3C電子產品的推薦信息" in content and device_type and is_3c_product(device_type):
        # 如果裝置類型是3C產品但仍然收到錯誤訊息，重新嘗試
        return f"您查詢的是{device_type}的推薦，但系統暫時無法提供完整資訊。請嘗試提供更具體的需求和預算，或稍後再試。"
    
    return content