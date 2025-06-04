import os
import json
import datetime
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
        
        # 添加產品到願望清單
        wishlist.append({
            'name': product_name,
            'added_at': datetime.datetime.now().isoformat()
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
            wishlist_text += f"{i}. {item['name']}\n"
        
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