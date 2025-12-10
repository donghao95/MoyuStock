from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFormLayout, QComboBox
)

class SettingsDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("设置")
        self.resize(400, 300)
        
        # Connect theme signal
        self.controller.theme_manager.theme_changed.connect(self.apply_theme)
        
        # Initial Style
        self.apply_theme(self.controller.theme_manager.get_current_theme())
        
        self.hotkeys = self.controller.config.get_hotkeys()
        self._init_ui()

    def apply_theme(self, theme):
        # We need a tailored stylesheet for dialog or just generic?
        # ThemeManager.get_style() is mostly for MainWindow (has QTableWidget etc).
        # We can reuse it, but might need specific tweaks if SettingsDialog uses different widgets?
        # Or just use the generic one. It covers QDialog, QLabel, etc.
        self.setStyleSheet(self.controller.theme_manager.get_style())

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        form.setSpacing(15)
        
        # Theme Selector
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["dark", "light"])
        current_theme = self.controller.theme_manager.current_theme_name
        index = self.combo_theme.findText(current_theme)
        if index >= 0:
            self.combo_theme.setCurrentIndex(index)
        
        # Live update on change
        self.combo_theme.currentTextChanged.connect(self._on_theme_changed)
        form.addRow("界面主题:", self.combo_theme)

        # Hotkeys
        self.input_toggle_vis = QLineEdit(self.hotkeys.get("toggle_visibility", "alt+s"))
        self.input_toggle_vis.setPlaceholderText("例如: alt+s")
        form.addRow("显示/隐藏:", self.input_toggle_vis)
        
        self.input_switch_mode = QLineEdit(self.hotkeys.get("switch_mode", "alt+m"))
        self.input_switch_mode.setPlaceholderText("例如: alt+m")
        form.addRow("切换模式:", self.input_switch_mode)
        
        layout.addLayout(form)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("关闭")
        btn_cancel.setObjectName("cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("保存快捷键")
        btn_save.clicked.connect(self._save)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)

    def _on_theme_changed(self, text):
        self.controller.theme_manager.set_theme(text)

    def _save(self):
        new_hotkeys = {
            "toggle_visibility": self.input_toggle_vis.text().strip(),
            "switch_mode": self.input_switch_mode.text().strip()
        }
        self.controller.config.set_hotkeys(new_hotkeys)
        self.accept()
