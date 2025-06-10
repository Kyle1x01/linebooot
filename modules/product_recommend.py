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
    if not device_type:
        return False
        
    # 將輸入轉換為小寫並去除空白
    input_text = device_type.lower().strip()
    
    # 定義3C產品類型列表
    c3_products = [
        "手機", "電腦", "筆電", "平板", "相機", "耳機", "智能手錶", "智慧手錶", "手表", "手錶",
        "電視", "顯示器", "螢幕", "鍵盤", "滑鼠", "音箱", "喇叭", "投影機", "印表機", "掃描儀",
        "路由器", "充電器", "行動電源", "攝影機", "麥克風", "遊戲機", "主機", "配件", "3c", "電子產品",
        "phone", "computer", "laptop", "tablet", "camera", "headphone", "smartwatch", "watch",
        "tv", "monitor", "keyboard", "mouse", "speaker", "projector", "printer", "scanner",
        "router", "charger", "power bank", "microphone", "game console", "accessory"
    ]
    
    # 直接匹配完整的裝置類型
    if input_text in c3_products:
        return True
    
    # 檢查裝置類型是否包含3C產品列表中的任何一個詞
    for product in c3_products:
        if product in input_text:
            return True
    
    # 特殊處理一些常見的裝置類型
    special_cases = {
        "蘋果": True,  # Apple
        "apple": True,
        "iphone": True,
        "三星": True,  # Samsung
        "samsung": True,
        "華為": True,  # Huawei
        "huawei": True,
        "小米": True,  # Xiaomi
        "xiaomi": True,
        "google": True,
        "pixel": True,
        "sony": True,
        "索尼": True,
        "lg": True,
        "asus": True,
        "華碩": True,
        "acer": True,
        "宏碁": True,
        "msi": True,
        "微星": True,
        "dell": True,
        "戴爾": True,
        "hp": True,
        "惠普": True
    }
    
    # 檢查特殊情況
    for case, is_3c in special_cases.items():
        if case in input_text:
            return is_3c
    
    # 如果以上都不匹配，則不是3C產品
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
    
    # 檢查回覆是否包含非3C產品的錯誤訊息，但只有在確實不是3C產品時才返回錯誤
    error_message = "很抱歉，我只能提供3C電子產品的推薦信息"
    
    # 如果回覆包含錯誤訊息，但裝置類型確實是3C產品，則忽略錯誤並返回內容
    if error_message in content:
        # 如果沒有指定裝置類型，或者裝置類型不是3C產品，則返回錯誤訊息
        if not device_type or not is_3c_product(device_type):
            return content
        else:
            # 裝置類型是3C產品，但模型仍然返回錯誤，提供更具體的指導
            return f"您查詢的是{device_type}產品推薦，為了提供更精準的建議，請提供以下資訊：\n\n1. 您的預算範圍（例如：10000-20000元）\n2. 您的主要使用需求（例如：攝影、遊戲、工作等）\n3. 您偏好的品牌或特定功能（如有）\n\n有了這些資訊，我們能為您推薦更符合需求的產品選擇。"
    
    # 檢查回覆是否包含實際的產品推薦
    if len(content.strip()) < 50 or "推薦" not in content:
        # 回覆內容太短或不包含推薦，可能是模型沒有正確理解請求
        return f"您查詢的是{device_type if device_type else '3C產品'}推薦，為了提供更精準的建議，請提供以下資訊：\n\n1. 您的預算範圍（例如：10000-20000元）\n2. 您的主要使用需求（例如：攝影、遊戲、工作等）\n3. 您偏好的品牌或特定功能（如有）\n\n有了這些資訊，我們能為您推薦更符合需求的產品選擇。"
    
    return content