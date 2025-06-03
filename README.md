# 3C小助手 LineBot

這是一個專業的3C產品查詢LineBot，提供產品規格、價格、比較、推薦、排行和評價等功能，並支持願望清單管理。

## 功能說明

### 3C小助手功能

1. **產品規格查詢**：輸入「查詢裝置」，然後輸入具體型號，獲取產品規格信息。
2. **產品價格查詢**：輸入「我想查詢價格」，然後輸入具體型號，獲取台灣地區的產品價格。
3. **產品比較**：輸入「大車拼」，然後輸入兩種裝置型號（以逗號分隔），獲取產品比較結果。
4. **推薦產品**：輸入「求推薦」，然後輸入需求和預算，獲取產品推薦。
5. **熱門排行**：輸入「金榜題名」，然後輸入具體產品類型（如手機），獲取台灣地區熱門產品排行。
6. **產品評價**：輸入「評價大師」，然後輸入具體型號，獲取產品評價和專業網頁鏈結。

### 願望清單功能

- **新增**：在產品價格查詢後，可選擇添加到願望清單。
- **查看**：輸入「查看我的車車」，顯示購物清單。
- **移除**：輸入「移除+產品名稱」，從願望清單中移除指定產品。
- **清空**：輸入「清空購物車」，清空願望清單。

### 其他指令

- **說明**：輸入「說明」，顯示功能說明。
- **離開**：輸入「離開」，終止當前程序，顯示說明。

## 技術架構

- **後端**：Python Flask
- **LineBot API**：line-bot-sdk
- **AI模型**：OpenAI GPT-4.1
- **部署平台**：Render

## 部署指南

### 本地開發

1. 克隆專案：
   ```
   git clone <repository-url>
   cd gitlinebot-master
   ```

2. 安裝依賴：
   ```
   pip install -r requirements.txt
   ```

3. 設置環境變數：
   創建或編輯 `.env` 文件，添加以下內容：
   ```
   LINE_CHANNEL_ACCESS_TOKEN=你的Line頻道訪問令牌
   LINE_CHANNEL_SECRET=你的Line頻道密鑰
   OPENAI_API_KEY=你的OpenAI API密鑰
   ```

4. 啟動應用：
   ```
   python app.py
   ```

### 部署到Render

1. 在Render上創建一個新的Web Service。
2. 連接到你的GitHub倉庫。
3. 設置以下環境變數：
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
   - `OPENAI_API_KEY`
4. 部署應用。

## 目錄結構

```
.
├── app.py                 # 主應用程序
├── modules/               # 功能模組
│   ├── __init__.py
│   ├── product_query.py   # 產品規格查詢
│   ├── price_query.py     # 產品價格查詢
│   ├── product_compare.py # 產品比較
│   ├── product_recommend.py # 產品推薦
│   ├── popular_ranking.py # 熱門排行
│   ├── product_review.py  # 產品評價
│   ├── wishlist.py        # 願望清單管理
│   └── user_state.py      # 用戶狀態管理
├── data/                  # 數據存儲
│   └── wishlists/         # 願望清單數據
├── .env                   # 環境變數
├── requirements.txt       # 依賴包列表
├── Procfile               # Render部署配置
└── README.md              # 專案說明
```

## 注意事項

- 確保Line Bot的Webhook URL設置正確，指向你的應用程序的`/callback`路徑。
- 在Line Developer Console中啟用Webhook。
- 確保OpenAI API密鑰有足夠的額度用於GPT-4.1調用。