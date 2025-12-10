import json
import os
from threading import Lock

class ConfigManager:
    DEFAULT_CONFIG = {
        "refresh_interval": 3,
        "window": {
            "mode": "expanded", # 'mini' or 'expanded'
            "mini_pos": [100, 100],
            "expanded_pos": [200, 200],
            "mini_opacity": 0.8,
            "expanded_width": 900,
            "expanded_height": 600
        },
        "stocks": [
            "601888",
            "000001"
        ]
    }

    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self._lock = Lock()
        self.data = self._load()

    def _load(self):
        if not os.path.exists(self.config_file):
            return self.DEFAULT_CONFIG.copy()
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                # Merge with default to ensure new keys exist
                config = self.DEFAULT_CONFIG.copy()
                config.update(loaded)
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.DEFAULT_CONFIG.copy()

    def save(self):
        with self._lock:
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=4)
            except Exception as e:
                print(f"Error saving config: {e}")

    def get_refresh_interval(self):
        return self.data.get("refresh_interval", 3)

    def set_refresh_interval(self, seconds):
        if seconds < 1: seconds = 1
        self.data["refresh_interval"] = seconds
        self.save()

    def get_stocks(self):
        return self.data.get("stocks", [])

    def add_stock(self, code):
        if code not in self.data["stocks"]:
            self.data["stocks"].append(code)
            self.save()

    def remove_stock(self, code):
        if code in self.data["stocks"]:
            self.data["stocks"].remove(code)
            self.save()
    
    def move_stock(self, code, direction):
        """
        移动股票在列表中的位置
        direction: -1 表示上移, 1 表示下移
        """
        stocks = self.data.get("stocks", [])
        if code not in stocks:
            return False
        
        current_index = stocks.index(code)
        new_index = current_index + direction
        
        # 边界检查
        if new_index < 0 or new_index >= len(stocks):
            return False
        
        # 交换位置
        stocks[current_index], stocks[new_index] = stocks[new_index], stocks[current_index]
        self.data["stocks"] = stocks
        self.save()
        return True
    
    def reorder_stocks(self, new_order):
        """
        重新排列股票顺序
        new_order: 新的股票代码顺序列表
        """
        # 验证新顺序包含所有现有股票
        current = set(self.data.get("stocks", []))
        if set(new_order) == current:
            self.data["stocks"] = new_order
            self.save()
            return True
        return False
            
    def get_window_settings(self):
        return self.data.get("window", {})
    
    def update_window_settings(self, key, value):
        if "window" not in self.data:
            self.data["window"] = {}
        self.data["window"][key] = value
        self.save()

    def get_hotkeys(self):
        return self.data.get("hotkeys", {
            "toggle_visibility": "alt+s",
            "switch_mode": "alt+m"
        })

    def set_hotkeys(self, hotkeys):
        self.data["hotkeys"] = hotkeys
        self.save()
