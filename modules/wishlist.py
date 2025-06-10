import os
import json
import datetime
import re
import openai
from linebot.models import TextSendMessage, FlexSendMessage

# 簡單的文件數據庫，用於存儲用戶的願望清單
WISHLIST_DIR = "data/wishlists"

def ensure_wishlist_dir():
    """確保願望清單目錄存在"""
    os.makedirs(WISHLIST_DIR, exist_ok=True)

def get_wishlist_path(user_id):
    """獲取用戶願望清單文件路徑"""
    ensure_wishlist_dir()
    return os.path.join(WISHLIST_DIR, f"{user_id}.json")

def load_wishlist(user_id):
    """載入用戶願望清單"""
    wishlist_path = get_wishlist_path(user_id)
    if os.path.exists(wishlist_path):
        with open(wishlist_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_wishlist(user_id, wishlist):
    """保存用戶願望清單"""
    wishlist_path = get_wishlist_path(user_id)
    with open(wishlist_path, 'w', encoding='utf-8') as f:
        json.dump(wishlist, f, ensure_ascii=False, indent=2)

def get_product_lowest_price(product_name):
    """獲取產品的最低價格"""
    try:
        # 設定系統訊息
        system_message = """
        你是一個專業的3C產品價格查詢助手。請根據用戶提供的產品型號，提供該產品在台灣地區的最低價格信息。
        
        回覆要求：
        1. 只提供台灣地區的商品最低價格，使用新台幣（NT$）為單位
        2. 只返回一個數字，不要包含任何其他文字或符號
        3. 如果找不到確切型號的價格，請返回「價格未知」
        4. 重要：只回覆與3C產品（電腦、手機、平板、相機、耳機、智能手錶等電子產品）相關的內容
        5. 如果用戶查詢的不是3C產品，請返回「非3C產品」
        6. 在回答前，請先判斷查詢的產品是否為3C產品，如果不是，則返回上述訊息
        """
        
        # 設定用戶訊息
        user_message = f"請提供{product_name}在台灣地區的最低價格，只返回數字"
        
        # 調用OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini-search-preview-2025-03-11",  # 使用支持網絡搜索的模型
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            web_search_options={},  # 啟用網絡搜索
            max_tokens=50
        )
        
        # 提取回覆內容
        price_text = response.choices[0].message.content.strip()
        
        # 檢查是否為非3C產品
        if price_text == "非3C產品":
            return "非3C產品"
        
        # 嘗試提取數字
        price_match = re.search(r'\d+(?:,\d+)*', price_text)
        if price_match:
            # 移除逗號並轉換為整數
            price = int(price_match.group(0).replace(',', ''))
            return price
        else:
            return "價格未知"
    except Exception as e:
        print(f"獲取價格時發生錯誤：{str(e)}")
        return "價格未知"

def add_to_wishlist(line_bot_api, reply_token, user_id, product_info):
    """添加產品到願望清單"""
    try:
        # 解析產品信息
        if product_info.startswith("添加到願望清單:"):
            product_name = product_info[8:].strip()
        else:
            product_name = product_info.strip()
        
        # 載入願望清單
        wishlist = load_wishlist(user_id)
        
        # 檢查產品是否已在清單中
        for item in wishlist:
            if item.get('name') == product_name:
                line_bot_api.reply_message(
                    reply_token,
                    TextSendMessage(text=f"產品 '{product_name}' 已在您的願望清單中。")
                )
                return
        
        # 獲取產品最低價格
        lowest_price = get_product_lowest_price(product_name)
        
        # 檢查是否為非3C產品
        if lowest_price == "非3C產品":
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=f"很抱歉，我只能將3C電子產品添加到願望清單。請嘗試添加電腦、手機、平板、相機、耳機、智能手錶等電子產品。")
            )
            return
        
        # 添加產品到願望清單
        wishlist.append({
            'name': product_name,
            'lowest_price': lowest_price,
            'added_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # 保存願望清單
        save_wishlist(user_id, wishlist)
        
        # 回覆用戶
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=f"已將 '{product_name}' 添加到您的願望清單。")
        )
    except Exception as e:
        error_message = f"添加到願望清單時發生錯誤：{str(e)}"
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=error_message)
        )

def view_wishlist(line_bot_api, reply_token, user_id):
    """查看願望清單"""
    try:
        # 載入願望清單
        wishlist = load_wishlist(user_id)
        
        if not wishlist:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="您的願望清單是空的。")
            )
            return
        
        # 構建願望清單訊息
        wishlist_text = "🛒 您的願望清單：\n\n"
        for i, item in enumerate(wishlist, 1):
            # 格式化日期
            added_date = "未知日期"
            if 'added_at' in item:
                try:
                    dt = datetime.datetime.fromisoformat(item['added_at'])
                    added_date = dt.strftime("%Y-%m-%d")
                except:
                    pass
            
            # 獲取價格信息
            price_info = ""
            if 'lowest_price' in item:
                if item['lowest_price'] != "價格未知":
                    price_info = f"NT${item['lowest_price']} | "
            
            wishlist_text += f"{i}. {item['name']}\n   {price_info}加入日期: {added_date}\n"
        
        wishlist_text += "\n要移除項目，請輸入「移除+產品名稱」\n要清空清單，請輸入「清空購物車」"
        
        # 回覆用戶
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=wishlist_text)
        )
    except Exception as e:
        error_message = f"查看願望清單時發生錯誤：{str(e)}"
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=error_message)
        )

def remove_from_wishlist(line_bot_api, reply_token, user_id, product_name):
    """從願望清單中移除產品"""
    try:
        # 載入願望清單
        wishlist = load_wishlist(user_id)
        
        if not wishlist:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text="您的願望清單是空的。")
            )
            return
        
        # 尋找並移除產品
        found = False
        new_wishlist = []
        for item in wishlist:
            if item.get('name') == product_name:
                found = True
            else:
                new_wishlist.append(item)
        
        if not found:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text=f"未在您的願望清單中找到 '{product_name}'。")
            )
            return
        
        # 保存更新後的願望清單
        save_wishlist(user_id, new_wishlist)
        
        # 回覆用戶
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=f"已從您的願望清單中移除 '{product_name}'。")
        )
    except Exception as e:
        error_message = f"移除願望清單項目時發生錯誤：{str(e)}"
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=error_message)
        )

def clear_wishlist(line_bot_api, reply_token, user_id):
    """清空願望清單"""
    try:
        # 保存空的願望清單
        save_wishlist(user_id, [])
        
        # 回覆用戶
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="已清空您的願望清單。")
        )
    except Exception as e:
        error_message = f"清空願望清單時發生錯誤：{str(e)}"
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=error_message)
        )