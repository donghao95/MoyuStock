from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QPushButton, QSystemTrayIcon, 
    QMenu, QApplication, QAbstractItemView, QFrame, QMessageBox,
    QLineEdit
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer, QSize
from PySide6.QtGui import QIcon, QAction, QColor
from datetime import datetime
from ui.styles import COLOR_UP, COLOR_DOWN, COLOR_FLAT

from ui.sparkline_widget import SparklineWidget
from ui.chart_dialog import ChartDialog
from ui.settings_dialog import SettingsDialog
from core.theme_manager import ThemeManager

class MainWindow(QMainWindow):
    settings_changed = Signal()
    switch_to_mini = Signal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.theme_manager = self.controller.theme_manager
        self.theme_manager.theme_changed.connect(self.apply_theme)
        
        self.setWindowTitle("📈 股票监控助手")
        self.resize(950, 600)
        
        # Initial Theme
        self.apply_theme(self.theme_manager.get_current_theme())
        
        # ... logic ...
        
        # Main Layout
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Top Bar (Add Stock) ---
        add_frame = QFrame()
        add_layout = QHBoxLayout(add_frame)
        add_layout.setContentsMargins(15, 12, 15, 12)
        
        add_label = QLabel("➕ 添加股票:")
        add_layout.addWidget(add_label)
        
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("输入股票代码 (如 601888, 00700)")
        self.input_code.setFixedWidth(200)
        self.input_code.returnPressed.connect(self.on_add_stock) 
        add_layout.addWidget(self.input_code)

        self.btn_add = QPushButton("添加")
        self.btn_add.setFixedWidth(80)
        self.btn_add.clicked.connect(self.on_add_stock)
        add_layout.addWidget(self.btn_add)
        
        self.add_status_label = QLabel("")
        add_layout.addWidget(self.add_status_label)
        
        # Settings Button
        add_layout.addStretch()
        btn_settings = QPushButton("设置")
        btn_settings.setFixedSize(60, 28)
        # Using theme style for buttons
        btn_settings.clicked.connect(self.on_settings_click)
        add_layout.addWidget(btn_settings)
        
        layout.addWidget(add_frame)

        # --- Table Section ---
        table_frame = QFrame()
        # Transparent background handled by central_widget style
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(15, 0, 15, 0)
        
        # 表格标题栏
        table_header = QHBoxLayout()
        table_title = QLabel("📋 监控列表")
        table_title.setProperty("class", "text-title")
        table_header.addWidget(table_title)
        
        table_header.addStretch()
        
        # 排序提示
        sort_hint = QLabel("💡 点击表头排序 | 使用上下箭头调整显示顺序")
        sort_hint.setProperty("class", "text-secondary")
        table_header.addWidget(sort_hint)
        
        table_layout.addLayout(table_header)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(["代码", "名称", "走势", "现价", "涨跌幅", "涨跌额", "成交量", "最高", "最低", "操作"])
        
        # 设置列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.resizeSection(0, 70)  # 代码
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 名称
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.resizeSection(2, 80) # 走势
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.resizeSection(3, 70)  # 现价
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.resizeSection(4, 70)  # 涨跌幅
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.resizeSection(5, 70)  # 涨跌额
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        header.resizeSection(6, 80)  # 成交量
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        header.resizeSection(7, 65)  # 最高
        header.setSectionResizeMode(8, QHeaderView.Fixed)
        header.resizeSection(8, 65)  # 最低
        header.setSectionResizeMode(9, QHeaderView.Fixed)
        header.resizeSection(9, 170)  # 操作

        # 让行高根据内容自适应，确保按钮撑起行高
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # 禁止编辑
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_frame)
        
        # --- Footer ---
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(15, 10, 15, 10)
        
        # 统计信息
        self.stats_label = QLabel("共 0 只股票")
        self.stats_label.setProperty("class", "text-secondary")
        footer_layout.addWidget(self.stats_label)
        
        self.last_update_label = QLabel("等待更新...")
        self.last_update_label.setProperty("class", "text-secondary")
        self.last_update_label.setStyleSheet("margin-left: 10px;") # Keep margin
        footer_layout.addWidget(self.last_update_label)

        footer_layout.addStretch()
        
        # 手动刷新按钮
        self.btn_refresh = QPushButton("🔄 立即刷新")
        self.btn_refresh.clicked.connect(self._manual_refresh)
        # Style handled by global QPushButton theme
        footer_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(footer_layout)
        
        # 连接信号
        self.controller.stock_data_updated.connect(self.update_table)
        self.table.cellDoubleClicked.connect(self._on_table_double_click)
        self._init_table_rows()
        
        # 更新定时器
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_status_time)
        self._update_timer.start(1000)
        self._last_update_time = None

    def apply_theme(self, theme):
        self.setStyleSheet(self.theme_manager.get_style())
        
        # Update Sparkline Colors
        up = theme["COLOR_UP"]
        down = theme["COLOR_DOWN"]
        
        # Prevent crash if table not ready
        if hasattr(self, 'table'):
            for row in range(self.table.rowCount()):
                widget = self.table.cellWidget(row, 2)
                if isinstance(widget, SparklineWidget):
                    widget.set_theme_colors(up, down)
        
        # 立即刷新表格文本颜色
        if hasattr(self, '_last_data'):
            self.update_table(self._last_data)



    @Slot()
    def on_add_stock(self):
        code = self.input_code.text().strip()
        if not code: return
        
        self.btn_add.setEnabled(False)
        self.btn_add.setText("⏳")
        self.add_status_label.setText("验证中...")
        QApplication.processEvents()
        
        # Verify & Add logic
        res = self.controller.api_client.fetch_quote(code)
        if res.get("success"):
            self.controller.add_stock(code)
            self._init_table_rows()
            self.input_code.clear()
            self.add_status_label.setText(f"✓ 已添加 {res['data']['name']}")
            QTimer.singleShot(3000, lambda: self.add_status_label.setText(""))
        else:
            self.add_status_label.setText(f"✗ 失败: {res.get('error')}")
            
        self.btn_add.setEnabled(True)
        self.btn_add.setText("添加")

    def _update_status_time(self):
        """更新状态时间显示"""
        if self._last_update_time:
            delta = (datetime.now() - self._last_update_time).total_seconds()
            if delta < 60:
                self.last_update_label.setText(f"上次更新: {int(delta)}秒前")
            else:
                self.last_update_label.setText(f"上次更新: {int(delta/60)}分钟前")

    def _manual_refresh(self):
        """手动刷新"""
        self.btn_refresh.setText("⏳ 刷新中...")
        self.btn_refresh.setEnabled(False)
        QApplication.processEvents()
        
        self.controller._on_timer_tick()
        
        # 延迟恢复按钮状态
        QTimer.singleShot(1000, lambda: self._restore_refresh_btn())
    
    def _restore_refresh_btn(self):
        self.btn_refresh.setText("🔄 立即刷新")
        self.btn_refresh.setEnabled(True)

    def _init_table_rows(self):
        self.table.setSortingEnabled(False)
        codes = self.controller.get_stocks_list()
        self.table.setRowCount(0)
        for code in codes:
            self._add_row_skeleton(code)
        self.table.setSortingEnabled(True)
        self._update_stats()

    def _update_stats(self):
        """更新统计信息"""
        count = self.table.rowCount()
        self.stats_label.setText(f"共 {count} 只股票")

    def _add_row_skeleton(self, code):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # 使用 Numeric items 进行排序
        code_item = QTableWidgetItem(code)
        code_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 0, code_item)
        
        name_item = QTableWidgetItem("加载中...")
        self.table.setItem(row, 1, name_item)
        
        # 走势
        sparkline = SparklineWidget()
        self.table.setCellWidget(row, 2, sparkline)

        price_item = NumericTableItem("--")
        price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 3, price_item)
        
        ratio_item = NumericTableItem("--")
        ratio_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 4, ratio_item)
        
        # 涨跌额
        increase_item = NumericTableItem("--")
        increase_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 5, increase_item)
        
        volume_item = NumericTableItem("--")
        volume_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 6, volume_item)
        
        high_item = NumericTableItem("--")
        high_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 7, high_item)
        
        low_item = NumericTableItem("--")
        low_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 8, low_item)

        # 操作按钮 - 更紧凑的布局
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        # 增加上下边距，利用按钮撑大行高
        btn_layout.setContentsMargins(4, 6, 4, 6)
        btn_layout.setSpacing(4)
        btn_layout.setAlignment(Qt.AlignCenter)
        
        # 上移按钮
        btn_up = QPushButton("↑")
        btn_up.setFixedSize(26, 24)
        btn_up.setCursor(Qt.PointingHandCursor)
        btn_up.setToolTip("上移")
        # 重点：padding: 0px 解决文字不显示问题;
        btn_up.setProperty("class", "table_btn_up")
        btn_up.clicked.connect(lambda checked=False, c=code: self._move_stock_up(c))
        btn_layout.addWidget(btn_up)
        
        # 下移按钮
        btn_down = QPushButton("↓")
        btn_down.setFixedSize(26, 24)
        btn_down.setCursor(Qt.PointingHandCursor)
        btn_down.setToolTip("下移")
        btn_down.setProperty("class", "table_btn_down")
        btn_down.clicked.connect(lambda checked=False, c=code: self._move_stock_down(c))
        btn_layout.addWidget(btn_down)
        
        # 提醒按钮
        btn_alert = QPushButton("🔔")
        btn_alert.setFixedSize(26, 24)
        btn_alert.setCursor(Qt.PointingHandCursor)
        btn_alert.setToolTip("设置提醒")
        btn_alert.setProperty("class", "table_btn_alert")
        btn_alert.clicked.connect(lambda checked=False, c=code: self._open_alert_dialog(c))
        btn_layout.addWidget(btn_alert)
        
        # 删除按钮
        btn_del = QPushButton("×")
        btn_del.setFixedSize(26, 24)
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setToolTip("删除")
        btn_del.setProperty("class", "table_btn_del")
        btn_del.clicked.connect(lambda checked=False, c=code: self.on_delete_click(c))
        btn_layout.addWidget(btn_del)
        
        self.table.setCellWidget(row, 9, btn_widget)

    def _move_stock_up(self, code):
        """上移股票"""
        self.controller.move_stock(code, -1)
        self._init_table_rows()
        # 触发数据刷新以更新显示
        self.controller._on_timer_tick()

    def _move_stock_down(self, code):
        """下移股票"""
        self.controller.move_stock(code, 1)
        self._init_table_rows()
        # 触发数据刷新以更新显示
        self.controller._on_timer_tick()

    def _open_alert_dialog(self, code):
        """打开提醒设置对话框"""
        # 获取股票名称
        name = code
        for row in range(self.table.rowCount()):
            code_item = self.table.item(row, 0)
            if code_item and code_item.text() == code:
                name_item = self.table.item(row, 1)
                if name_item:
                    name = name_item.text()
                break
        
        dialog = AlertDialog(self.controller, code, name, self)
        dialog.exec()

    def _on_table_double_click(self, row, column):
        """双击表格行打开分时图"""
        # 忽略操作列的双击
        if column == 9:
            return
        
        code_item = self.table.item(row, 0)
        if not code_item:
            return
        
        code = code_item.text()
        name_item = self.table.item(row, 1)
        name = name_item.text() if name_item else code
        
        dialog = ChartDialog(self.controller, code, name, self)
        dialog.exec()

    @Slot()
    def on_test_click(self):
        code = self.input_code.text().strip()
        if not code: 
            return
        
        # 检查是否已存在
        existing = self.controller.get_stocks_list()
        if code in existing:
            self.test_result_label.setText(f"⚠ {code} 已在监控列表中")
            self.test_result_label.setProperty("class", "status-warn") # Will define this or use style
            self.test_result_label.setStyleSheet(f"color: {self.theme_manager.get_current_theme()['STATUS_WARN']}; font-size: 11px;")
            return
        
        self.btn_test.setText("⏳...")
        self.btn_test.setEnabled(False)
        self.test_result_label.setText("正在验证并添加...")
        self.test_result_label.setStyleSheet("color: #888888; font-size: 11px;")
        QApplication.processEvents()
        
        res = self.controller.api_client.fetch_quote(code)
        self.btn_test.setText("🔍 验证")
        self.btn_test.setEnabled(True)

        if res.get("success"):
            data = res["data"]
            # 验证成功，自动添加
            self.controller.add_stock(code)
            self._init_table_rows()
            self.input_code.clear()
            self.test_result_label.setText(f"✓ 已添加 {data['name']} ({code})")
            self.test_result_label.setStyleSheet(f"color: {self.theme_manager.get_current_theme()['STATUS_OK']}; font-size: 11px;")
            # 清除提示
            QTimer.singleShot(3000, lambda: self.test_result_label.setText(""))
        else:
            self.test_result_label.setText(f"✗ {res.get('error', '未找到')}")
            self.test_result_label.setStyleSheet(f"color: {self.theme_manager.get_current_theme()['STATUS_ERR']}; font-size: 11px;")

    @Slot()
    def on_add_click(self):
        # 兼容旧逻辑，直接触发验证
        self.on_test_click()

    def on_delete_click(self, code):
        # 确认对话框
        ret = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要移除股票 {code} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if ret == QMessageBox.Yes:
            self.controller.remove_stock(code)
            self._init_table_rows()

    @Slot(int)
    def on_rate_change(self, val):
        self.controller.set_interval(val)

    def update_table(self, data):
        self._last_data = data
        self._last_update_time = datetime.now()
        self.last_update_label.setText("刚刚更新")
        
        self.table.setSortingEnabled(False)
        
        theme = self.theme_manager.get_current_theme()
        
        for row in range(self.table.rowCount()):
            code_item = self.table.item(row, 0)
            if not code_item: 
                continue
            code = code_item.text()
            
            if code in data:
                info = data[code]
                self.table.item(row, 1).setText(info['name'])
                
                # 更新走势图
                sparkline = self.table.cellWidget(row, 2)
                if sparkline and "points" in info and "preClose" in info:
                     sparkline.set_data(info["points"], info["preClose"], code)

                # 计算颜色
                try:
                    ratio_val = float(info['ratio'].strip('%'))
                except:
                    ratio_val = 0.0

                if ratio_val > 0:
                    color = QColor(theme["COLOR_UP"])
                elif ratio_val < 0:
                    color = QColor(theme["COLOR_DOWN"])
                else:
                    color = QColor(theme["COLOR_FLAT"])

                # 价格
                it_price = self.table.item(row, 3)
                it_price.setText(str(info['price']))
                it_price.setForeground(color)
                
                # 涨跌幅
                it_ratio = self.table.item(row, 4)
                it_ratio.setText(info['ratio'])
                it_ratio.setForeground(color)
                
                # 涨跌额
                increase = info.get('increase', '--')
                it_increase = self.table.item(row, 5)
                it_increase.setText(str(increase))
                it_increase.setForeground(color)

                # 成交量
                self.table.item(row, 6).setText(str(info['volume']))
                
                # 最高/最低 (如果API返回了这些数据)
                high = info.get('high', '--')
                low = info.get('low', '--')
                
                it_high = self.table.item(row, 7)
                it_high.setText(str(high) if high else '--')
                if high and high != '--':
                    it_high.setForeground(QColor(theme["COLOR_UP"]))
                
                it_low = self.table.item(row, 8)
                it_low.setText(str(low) if low else '--')
                if low and low != '--':
                    it_low.setForeground(QColor(theme["COLOR_DOWN"]))

        self.table.setSortingEnabled(True)

    def closeEvent(self, event):
        # 保存窗口位置
        self.controller.config.update_window_settings("expanded_pos", [self.x(), self.y()])
        event.ignore()
        self.hide()

        if self.isVisible():
            self.controller.config.update_window_settings("expanded_pos", [self.x(), self.y()])
        # super().moveEvent(event)

    def on_settings_click(self):
        dialog = SettingsDialog(self.controller, self)
        if dialog.exec():
            self.settings_changed.emit()

class NumericTableItem(QTableWidgetItem):
    """
    Table item that sorts numerically.
    """
    def __lt__(self, other):
        try:
            # Try to convert to float for comparison
            # Handle %, commas, etc
            text1 = self.text().replace('%', '').replace(',', '').replace('+', '').strip()
            text2 = other.text().replace('%', '').replace(',', '').replace('+', '').strip()
            
            # Helper to handle '--' or empty
            def to_float(t):
                if not t or t == '--':
                    return -float('inf') # Or 0 depending on pref
                return float(t)
            
            val1 = to_float(text1)
            val2 = to_float(text2)
            
            return val1 < val2
        except ValueError:
            return super().__lt__(other)
