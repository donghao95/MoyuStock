from PySide6.QtCore import QObject, QThread, Signal, QTimer
from core.api_client import BaiduApiClient
from core.config_manager import ConfigManager
from core.alert_manager import AlertManager, AlertType
from core.theme_manager import ThemeManager
import logging

logger = logging.getLogger(__name__)

class DataFetcher(QObject):
    """
    Worker object for QThread.
    """
    data_ready = Signal(dict) # {code: {data...}}
    error_occurred = Signal(str)

    def __init__(self, api_client, codes):
        super().__init__()
        self.api_client = api_client
        self.codes = codes
        self._is_running = False

    def fetch_all(self):
        if not self._is_running:
            return
            
        results = {}
        # Fetch sequentially (simpler) or thread pool (faster but complex)
        # For < 50 stocks, sequential is fast enough.
        for code in self.codes:
            if not self._is_running: break
            
            res = self.api_client.fetch_quote(code)
            if res.get("success"):
                results[code] = res["data"]
            # No error emission here to avoid spamming UI, just skip
            
        if self._is_running and results:
            self.data_ready.emit(results)

    def set_running(self, running):
        self._is_running = running

    def update_codes(self, codes):
        self.codes = codes


class MonitorController(QObject):
    """
    Main controller linking UI, Config, and API.
    """
    stock_data_updated = Signal(dict) # Emitted to UI
    alert_triggered = Signal(str, str, str)  # code, name, message
    
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.api_client = BaiduApiClient()
        self.alert_manager = AlertManager(self.config)
        self.theme_manager = ThemeManager(self.config)
        self.timer = QTimer()
        
        # Setup worker thread for network 
        # Actually QTimer + running in main thread might block GUI if requests allow it.
        # Better: QTimer triggers a function that runs in a thread? 
        # Simplest PySide6 pattern: QThread worker handling the loop or One-shot run.
        # Let's use a standard Timer triggering a threaded fetch.
        
        self.timer.timeout.connect(self._on_timer_tick)
        self.is_running = False
        self.is_paused = False

    def start_monitoring(self):
        interval = self.config.get_refresh_interval() * 1000
        self.timer.start(interval)
        self.is_running = True
        self._on_timer_tick() # Immediate first run

    def stop_monitoring(self):
        self.timer.stop()
        self.is_running = False

    def _on_timer_tick(self):
        # We need to run this in a background thread to avoid freezing UI
        if self.is_paused:
            return

        # Simple implementation: Use a Thread class for the fetch job
        # Note: In production code we should reuse threads.
        import threading
        t = threading.Thread(target=self._fetch_job)
        t.daemon = True
        t.start()

    def toggle_pause(self):
        """切换暂停状态"""
        self.is_paused = not self.is_paused
        logger.info(f"Monitor paused: {self.is_paused}")
        return self.is_paused

    def _fetch_job(self):
        if self.is_paused:
            return

        codes = self.config.get_stocks()
        if not codes:
            logger.debug("No stocks to fetch")
            return
        
        logger.info(f"开始获取 {len(codes)} 只股票数据: {codes}")
            
        results = {}
        failed = []
        for code in codes:
            if not self.is_running or self.is_paused: break
            res = self.api_client.fetch_quote(code)
            if res.get("success"):
                results[code] = res["data"]
            else:
                failed.append(f"{code}: {res.get('error', 'Unknown')}")
        
        if failed:
            logger.warning(f"获取失败: {failed}")
        
        logger.info(f"获取完成: 成功 {len(results)} / 失败 {len(failed)}")
        
        # Emit signal from generic thread? Need to be careful with PySide
        # PySide6 Signals are thread-safe.
        if results:
            self.stock_data_updated.emit(results)
            
            # 检查提醒
            triggered = self.alert_manager.check_alerts(results)
            for rule, info in triggered:
                self._send_notification(rule, info)

    def add_stock(self, code):
        # First verify
        res = self.api_client.fetch_quote(code)
        if res.get("success"):
            self.config.add_stock(code)
            # Fetch immediately
            self._on_timer_tick()
            return True, res["data"]["name"]
        else:
            return False, res.get("error")

    def remove_stock(self, code):
        self.config.remove_stock(code)
        # Update UI will happen next tick

    def move_stock(self, code, direction):
        """
        移动股票在列表中的位置
        direction: -1 表示上移, 1 表示下移
        """
        return self.config.move_stock(code, direction)

    def reorder_stocks(self, new_order):
        """重新排列股票顺序"""
        return self.config.reorder_stocks(new_order)

    def set_interval(self, seconds):
        self.config.set_refresh_interval(seconds)
        if self.is_running:
            self.stop_monitoring()
            self.start_monitoring()

    def get_stocks_list(self):
        return self.config.get_stocks()
    
    def _send_notification(self, rule, info):
        """发送系统通知"""
        try:
            from plyer import notification
            
            name = info.get("name", rule.code)
            price = info.get("price", "--")
            ratio = info.get("ratio", "--")
            
            # 构建提醒消息
            if rule.alert_type == AlertType.PRICE_ABOVE:
                title = f"📈 {name} 价格突破"
                message = f"当前价格 {price} 已超过 {rule.threshold}"
            elif rule.alert_type == AlertType.PRICE_BELOW:
                title = f"📉 {name} 价格跌破"
                message = f"当前价格 {price} 已低于 {rule.threshold}"
            elif rule.alert_type == AlertType.CHANGE_ABOVE:
                title = f"🚀 {name} 涨幅提醒"
                message = f"当前涨幅 {ratio} 已超过 {rule.threshold}%"
            elif rule.alert_type == AlertType.CHANGE_BELOW:
                title = f"⚠️ {name} 跌幅提醒"
                message = f"当前跌幅 {ratio} 已超过 {rule.threshold}%"
            else:
                title = f"📊 {name} 提醒"
                message = f"价格: {price}, 涨跌幅: {ratio}"
            
            notification.notify(
                title=title,
                message=message,
                app_name="股票监控助手",
                timeout=10
            )
            
            # 同时发送信号给 UI
            self.alert_triggered.emit(rule.code, name, message)
            logger.info(f"Notification sent: {title} - {message}")
            
        except ImportError:
            logger.warning("plyer not installed, using fallback notification")
            # 如果 plyer 不可用，通过信号通知 UI 显示
            name = info.get("name", rule.code)
            self.alert_triggered.emit(rule.code, name, f"提醒触发: {rule.alert_type.value}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

