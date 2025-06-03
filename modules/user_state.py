class UserState:
    """用戶狀態管理類"""
    
    def __init__(self):
        self.current_state = None  # 當前狀態（功能）
        self.waiting_for_input = False  # 是否等待用戶輸入
        self.context = {}  # 上下文數據存儲
    
    def set_state(self, state, waiting_for_input=False):
        """設置當前狀態"""
        self.current_state = state
        self.waiting_for_input = waiting_for_input
        
    def reset(self):
        """重置狀態"""
        self.current_state = None
        self.waiting_for_input = False
        self.context = {}
    
    def set_context(self, key, value):
        """設置上下文數據"""
        self.context[key] = value
    
    def get_context(self, key, default=None):
        """獲取上下文數據"""
        return self.context.get(key, default)