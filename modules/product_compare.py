import os
import openai
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

def handle_product_compare(line_bot_api, reply_token, input_text):
    """處理產品比較"""
    try:
        # 解析輸入的兩個產品型號
        products = [p.strip() for p in input_text.split(',')]
        
        if len(products) != 2:
            try:
                line_bot_api.reply_message(
                    reply_token,
                    TextSendMessage(text="請輸入兩個產品型號，以逗號分隔。例如：iPhone 13, Samsung S21")
                )
            except LineBotApiError as api_error:
                print(f"LINE API Error in handle_product_compare (invalid format): {str(api_error)}")
            return
        
        # 調用GPT-4.1進行網絡搜索
        response = call_gpt_with_web_search(products[0], products[1])
        
        # 回覆用戶
        try:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=response)
            )
        except LineBotApiError as api_error:
            print(f"LINE API Error in handle_product_compare: {str(api_error)}")
    except Exception as e:
        error_message = f"比較時發生錯誤：{str(e)}"
        try:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=error_message)
            )
        except LineBotApiError as api_error:
            print(f"LINE API Error in handle_product_compare error handler: {str(api_error)}")

def call_gpt_with_web_search(product1, product2):
    """調用GPT-4.1進行網絡搜索並返回產品比較"""
    # 設定系統訊息
    system_message = """
    你是一個專業的3C產品比較助手。請根據用戶提供的兩個產品型號，提供這兩個產品的詳細比較。
    
    回覆要求：
    1. 回覆必須控制在500字以內
    2. 確保比較的是台灣發行版本的產品
    3. 比較應包括但不限於：性能、相機、電池、顯示屏、設計、價格等關鍵方面
    4. 使用表格或清晰的分類方式呈現比較結果
    5. 在比較的最後，根據不同使用場景給出簡短的建議
    6. 如果找不到確切型號，請明確說明並提供最相近型號的比較
    7. 盡可能的減少特殊字符 ex: ** | - 等 
    8. 請盡可能的使用繁體中文回覆
    9. 優先引用製造商官網來源
    10.兩裝裝置以換行處理 範例： 處理器 :
                                     裝置1:處理器1
                                     裝置2:處理器2
    11.來源網址提供在回覆的最下方，必免中斷閱讀體驗，且確保能夠準確提供網址
    12.顯示屏==螢幕（避免使用中國名詞，使用台灣的名詞）
    13.以換行做區隔,不使用makedown格式輸出表格
    13.請盡可能的使用繁體中文回覆
    14.重要：只回覆與3C產品（電腦、手機、平板、相機、耳機、智能手錶等電子產品）相關的內容
    15.如果用戶查詢的不是3C產品，請回覆：「很抱歉，我只能提供3C電子產品的比較信息。請嘗試查詢電腦、手機、平板、相機、耳機、智能手錶等電子產品。」
    16.在回答前，請先判斷查詢的產品是否為3C產品，如果不是，則回覆上述訊息
    """
    
    # 設定用戶訊息
    user_message = f"請比較{product1}和{product2}這兩款產品的優缺點和適用場景"
    
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