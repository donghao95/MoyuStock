import sys
import logging
import keyboard
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Signal, QObject

from core.monitor_controller import MonitorController
from ui.mini_window import MiniWindow
from ui.main_window import MainWindow

# Hotkey Listener Helper for Thread Safety
class HotkeyListener(QObject):
    toggle_requested = Signal()
    switch_mode_requested = Signal()

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.reload()

    def reload(self):
        try:
            keyboard.unhook_all()
            hotkeys = self.config.get_hotkeys()
            
            toggle_key = hotkeys.get("toggle_visibility", "alt+s")
            if toggle_key:
                keyboard.add_hotkey(toggle_key, self.on_toggle)
            
            switch_key = hotkeys.get("switch_mode", "alt+m")
            if switch_key:
                keyboard.add_hotkey(switch_key, self.on_switch_mode)
                
        except ImportError:
            pass
        except Exception as e:
            print(f"Failed to set hotkeys: {e}")

    def on_toggle(self):
        self.toggle_requested.emit()
        
    def on_switch_mode(self):
        self.switch_mode_requested.emit()

# 配置全局日志
def setup_logging():
    """配置日志系统"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 创建根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)
    
    # 文件处理器
    try:
        file_handler = logging.FileHandler('stock_monitor.log', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(log_format))
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to create log file: {e}")
    
    return logging.getLogger(__name__)

def create_tray_icon():
    # Generate a simple icon programmatically since we don't have an image file yet
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor(0,0,0,0))
    painter = QPainter(pixmap)
    painter.setBrush(QColor("#4ECDC4")) # Brand color
    painter.setPen(QColor("white"))
    painter.drawEllipse(2, 2, 28, 28)
    painter.drawText(8, 22, "S")
    painter.end()
    return QIcon(pixmap)

def main():
    # 初始化日志
    logger = setup_logging()
    logger.info("股票监控助手启动")
    
    app = QApplication(sys.argv)
    
    # Critical: Do not quit when last window is closed (we minimize to tray)
    app.setQuitOnLastWindowClosed(False)

    controller = MonitorController()
    
    mini_win = MiniWindow(controller)
    main_win = MainWindow(controller)
    
    # Hotkey Handler
    hotkey_listener = HotkeyListener(controller.config)
    
    # --- System Tray ---
    tray = QSystemTrayIcon()
    tray.setIcon(create_tray_icon())
    tray.setVisible(True)
    
    tray_menu = QMenu()
    
    action_show_main = tray_menu.addAction("打开主界面")
    action_show_mini = tray_menu.addAction("显示悬浮窗")
    tray_menu.addSeparator()
    action_quit = tray_menu.addAction("退出")
    
    tray.setContextMenu(tray_menu)

    # --- Logic ---

    def show_mini():
        # Hide Main, Show Mini
        main_win.hide()
        mini_win.show()
        # Save config
        controller.config.update_window_settings("mode", "mini")

    def show_main():
        # Hide Mini, Show Main
        mini_win.hide()
        main_win.show()
        main_win.activateWindow()
        controller.config.update_window_settings("mode", "expanded")
    
    def switch_mode():
        """Switch between Mini and Expanded"""
        if main_win.isVisible() and not main_win.isMinimized():
            show_mini()
        elif mini_win.isVisible() and not mini_win.isMinimized():
            show_main()
        else:
            # If nothing is visible (hidden state or maximized?), default to main?
            # Or restore based on config?
            config_mode = controller.config.get_window_settings().get("mode", "expanded")
            if config_mode == "mini":
                show_mini()
            else:
                show_main()

    def toggle_visibility():
        """Handle Global Hotkey Toggle"""
        is_visible = (main_win.isVisible() and not main_win.isMinimized()) or \
                     (mini_win.isVisible() and not mini_win.isMinimized())
        
        if is_visible:
            # Hide all
            main_win.hide()
            mini_win.hide()
        else:
            # Show based on last config
            config_mode = controller.config.get_window_settings().get("mode", "expanded")
            if config_mode == "mini":
                show_mini()
            else:
                show_main()

    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.Trigger:
            toggle_visibility()

    def quit_app():
        controller.stop_monitoring()
        app.quit()

    # Signals Connection
    tray.activated.connect(on_tray_activated)
    action_show_main.triggered.connect(show_main)
    action_show_mini.triggered.connect(show_mini)
    action_quit.triggered.connect(quit_app)
    
    hotkey_listener.toggle_requested.connect(toggle_visibility)
    hotkey_listener.switch_mode_requested.connect(switch_mode)
    
    # When settings change, reload hotkeys
    main_win.settings_changed.connect(hotkey_listener.reload)

    # Window signals
    mini_win.switch_to_expanded.connect(show_main)
    mini_win.close_app.connect(quit_app)
    
    main_win.switch_to_mini.connect(show_mini)
    
    # Startup
    config_mode = controller.config.get_window_settings().get("mode", "expanded")
    controller.start_monitoring()
    
    if config_mode == "mini":
        show_mini()
    else:
        show_main()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
