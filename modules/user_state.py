class UserState:
    """用戶狀態管理類"""
    
    def __init__(self):
        self.current_state = None  # 當前狀態（功能）
        self.waiting_for_input = False  # 是否等待用戶輸入
        self.context = {}  # 上下文數據存儲
        self.last_activity_time = None  # 最後活動時間
    
    def set_state(self, state, waiting_for_input=False):
        """設置當前狀態"""
        import time
        self.current_state = state
        self.waiting_for_input = waiting_for_input
        self.last_activity_time = time.time()  # 更新最後活動時間
        
    def reset(self):
        """重置狀態"""
        import time
        self.current_state = None
        self.waiting_for_input = False
        self.context = {}
        self.last_activity_time = time.time()  # 更新最後活動時間
    
    def set_context(self, key, value):
        """設置上下文數據"""
        import time
        self.context[key] = value
        self.last_activity_time = time.time()  # 更新最後活動時間
    
    def get_context(self, key, default=None):
        """獲取上下文數據"""
        return self.context.get(key, default)
    
    def is_expired(self, timeout_seconds=1800):  # 預設 30 分鐘超時
        """檢查用戶狀態是否已過期"""
        import time
        if self.last_activity_time is None:
            return False
        return (time.time() - self.last_activity_time) > timeout_seconds
    
    def update_activity_time(self):
        """更新最後活動時間"""
        import time
        self.last_activity_time = time.time()