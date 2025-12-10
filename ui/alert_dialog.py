"""
提醒设置对话框
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QDoubleSpinBox, QListWidget, QListWidgetItem,
    QGroupBox, QMessageBox, QWidget
)
from PySide6.QtCore import Qt
from core.alert_manager import AlertRule, AlertType


class AlertDialog(QDialog):
    """提醒设置对话框"""
    
    def __init__(self, controller, stock_code: str, stock_name: str, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.stock_code = stock_code
        self.stock_name = stock_name
        
        self.setWindowTitle(f"设置提醒 - {stock_name} ({stock_code})")
        self.setMinimumWidth(400)
        # Styles are now handled by styles.py (QDialog, QGroupBox, QListWidget, etc.)
        self.setStyleSheet(self.controller.theme_manager.get_style())
        
        self._setup_ui()
        self._load_rules()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 添加新规则区域
        add_group = QGroupBox("添加提醒规则")
        add_layout = QHBoxLayout(add_group)
        
        # 类型选择
        self.type_combo = QComboBox()
        self.type_combo.addItem("价格高于", AlertType.PRICE_ABOVE)
        self.type_combo.addItem("价格低于", AlertType.PRICE_BELOW)
        self.type_combo.addItem("涨幅超过", AlertType.CHANGE_ABOVE)
        self.type_combo.addItem("跌幅超过", AlertType.CHANGE_BELOW)
        add_layout.addWidget(self.type_combo)
        
        # 阈值输入
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0, 99999)
        self.threshold_spin.setDecimals(2)
        self.threshold_spin.setValue(0)
        add_layout.addWidget(self.threshold_spin)
        
        # 单位提示
        self.unit_label = QLabel("元")
        add_layout.addWidget(self.unit_label)
        
        # 添加按钮
        add_btn = QPushButton("添加")
        add_btn.setProperty("class", "btn-primary")
        add_btn.clicked.connect(self._add_rule)
        add_layout.addWidget(add_btn)
        
        layout.addWidget(add_group)
        
        # 类型变化时更新单位
        self.type_combo.currentIndexChanged.connect(self._update_unit)
        
        # 现有规则列表
        rules_group = QGroupBox("当前规则")
        rules_layout = QVBoxLayout(rules_group)
        
        self.rules_list = QListWidget()
        rules_layout.addWidget(self.rules_list)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        delete_btn = QPushButton("删除选中")
        delete_btn.setProperty("class", "btn-danger")
        delete_btn.clicked.connect(self._delete_rule)
        btn_layout.addWidget(delete_btn)
        
        reset_btn = QPushButton("重置触发状态")
        reset_btn.clicked.connect(self._reset_triggered)
        btn_layout.addWidget(reset_btn)
        
        btn_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        
        rules_layout.addLayout(btn_layout)
        layout.addWidget(rules_group)
    
    def _update_unit(self):
        """更新单位显示"""
        alert_type = self.type_combo.currentData()
        if alert_type in (AlertType.PRICE_ABOVE, AlertType.PRICE_BELOW):
            self.unit_label.setText("元")
        else:
            self.unit_label.setText("%")
    
    def _load_rules(self):
        """加载当前股票的规则"""
        self.rules_list.clear()
        rules = self.controller.alert_manager.get_rules_for_stock(self.stock_code)
        
        for rule in rules:
            text = self._format_rule(rule)
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, rule)
            
            # 已触发的规则显示不同颜色
            if rule.triggered:
                item.setForeground(Qt.gray)
            
            self.rules_list.addItem(item)
    
    def _format_rule(self, rule: AlertRule) -> str:
        """格式化规则显示"""
        type_names = {
            AlertType.PRICE_ABOVE: "价格高于",
            AlertType.PRICE_BELOW: "价格低于",
            AlertType.CHANGE_ABOVE: "涨幅超过",
            AlertType.CHANGE_BELOW: "跌幅超过"
        }
        
        unit = "元" if rule.alert_type in (AlertType.PRICE_ABOVE, AlertType.PRICE_BELOW) else "%"
        status = " [已触发]" if rule.triggered else ""
        
        return f"{type_names.get(rule.alert_type, '未知')} {rule.threshold}{unit}{status}"
    
    def _add_rule(self):
        """添加规则"""
        alert_type = self.type_combo.currentData()
        threshold = self.threshold_spin.value()
        
        if threshold <= 0:
            QMessageBox.warning(self, "提示", "请输入有效的阈值")
            return
        
        rule = AlertRule(
            code=self.stock_code,
            alert_type=alert_type,
            threshold=threshold
        )
        
        self.controller.alert_manager.add_rule(rule)
        self._load_rules()
    
    def _delete_rule(self):
        """删除选中的规则"""
        item = self.rules_list.currentItem()
        if not item:
            return
        
        rule = item.data(Qt.UserRole)
        self.controller.alert_manager.remove_rule(rule.code, rule.alert_type)
        self._load_rules()
    
    def _reset_triggered(self):
        """重置触发状态"""
        self.controller.alert_manager.reset_triggered(self.stock_code)
        self._load_rules()
        QMessageBox.information(self, "提示", "已重置触发状态，规则将重新生效")
