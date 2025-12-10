
from PySide6.QtCore import QObject, Signal
from ui.styles import THEMES, get_stylesheet

class ThemeManager(QObject):
    theme_changed = Signal(dict) # Emits the new theme dict

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.current_theme_name = self.config.get_window_settings().get("theme", "dark")
        self.current_theme = THEMES.get(self.current_theme_name, THEMES["dark"])

    def set_theme(self, theme_name):
        if theme_name in THEMES:
            self.current_theme_name = theme_name
            self.current_theme = THEMES[theme_name]
            self.config.update_window_settings("theme", theme_name)
            self.theme_changed.emit(self.current_theme)

    def get_current_theme(self):
        return self.current_theme
        
    def get_style(self):
        return get_stylesheet(self.current_theme)
