from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QMenu, QApplication, 
    QGraphicsDropShadowEffect, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal, QPoint, QTimer, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QCursor, QAction, QColor, QFont, QPainter, QBrush, QPen, QLinearGradient

class MiniWindow(QWidget):
    switch_to_expanded = Signal()
    close_app = Signal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        # Theme Setup
        self.theme = self.controller.theme_manager.get_current_theme()
        self.controller.theme_manager.theme_changed.connect(self.update_theme)
        
        # Flags
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 8, 10, 8)
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)
        
        # 状态提示标签（显示刷新状态）
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            color: rgba(255,255,255,0); 
            font-size: 9pt;
            padding: 0;
            margin: 0;
        """)
        self.status_label.setAlignment(Qt.AlignRight)
        self.status_label.setFixedHeight(14)  
        self.main_layout.addWidget(self.status_label)
        
        # 股票内容容器
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(3)
        self.main_layout.addWidget(self.content_widget)

        # State
        self.old_pos = None
        self.is_locked = False
        self.is_hovered = False
        self.labels = {}  # code -> QLabel
        self._bg_opacity = 0.0
        self._show_ratio = True 
        self._cached_data = {} 
        
        # 动画
        self._opacity_animation = QPropertyAnimation(self, b"bgOpacity")
        self._opacity_animation.setDuration(200)
        self._opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Connect
        self.controller.stock_data_updated.connect(self.update_data)
        
        # 刷新状态定时器
        self._last_update_time = None
        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._update_status_text)
        self._status_timer.start(1000)

    def update_theme(self, theme):
        self.theme = theme
        self.update() # Repaint background
        if self._cached_data:
            self._render_data(self._cached_data)

    # 背景透明度属性动画
    def get_bg_opacity(self):
        return self._bg_opacity
    
    def set_bg_opacity(self, value):
        self._bg_opacity = value
        self.update()
    
    bgOpacity = Property(float, get_bg_opacity, set_bg_opacity)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 根据悬停状态绘制背景
        if self._bg_opacity > 0.01:
            # 绘制圆角矩形背景
            rect = self.rect().adjusted(2, 2, -2, -2)
            
            # 渐变背景
            gradient = QLinearGradient(0, 0, 0, rect.height())
            base_color = QColor(self.theme.get("MINI_BG_COLOR", "#1a1a2e"))
            base_color.setAlphaF(self._bg_opacity * 0.95)
            gradient.setColorAt(0, base_color)
            
            darker = QColor(self.theme.get("MINI_BG_HOVER_COLOR", "#16213e"))
            darker.setAlphaF(self._bg_opacity * 0.98)
            gradient.setColorAt(1, darker)
            
            painter.setBrush(gradient)
            
            # 边框
            border_color = QColor(self.theme.get("BRAND_PRIMARY", "#4ECDC4"))
            border_color.setAlphaF(self._bg_opacity * 0.6)
            painter.setPen(QPen(border_color, 1.5))
            
            painter.drawRoundedRect(rect, 10, 10)
        
        # Do not call super().paintEvent(event) for transparent widgets if we handle painting?
        # Actually QWidget.paintEvent is empty.
        
    def enterEvent(self, event):
        """鼠标进入时显示背景，方便拖拽和右键操作"""
        self.is_hovered = True
        self._opacity_animation.stop()
        self._opacity_animation.setStartValue(self._bg_opacity)
        self._opacity_animation.setEndValue(1.0)
        self._opacity_animation.start()
        
        # 显示状态 - 使用透明度而不是show/hide
        self.status_label.setStyleSheet("""
            color: rgba(255,255,255,0.5); 
            font-size: 9pt;
            padding: 0;
            margin: 0;
        """)
        self.setCursor(Qt.OpenHandCursor if not self.is_locked else Qt.ArrowCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开时隐藏背景"""
        self.is_hovered = False
        self._opacity_animation.stop()
        self._opacity_animation.setStartValue(self._bg_opacity)
        self._opacity_animation.setEndValue(0.0)
        self._opacity_animation.start()
        
        # 隐藏状态 - 使用透明度而不是show/hide
        self.status_label.setStyleSheet("""
            color: rgba(255,255,255,0); 
            font-size: 9pt;
            padding: 0;
            margin: 0;
        """)
        self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)

    def _update_status_text(self):
        """更新状态文本，显示距离上次刷新的时间"""
        if self._last_update_time:
            from datetime import datetime
            now = datetime.now()
            delta = (now - self._last_update_time).total_seconds()
            if delta < 60:
                self.status_label.setText(f"⟳ {int(delta)}秒前")
            else:
                self.status_label.setText(f"⟳ {int(delta/60)}分钟前")
        else:
            self.status_label.setText("⟳ 等待数据...")

    def update_data(self, data):
        from datetime import datetime
        self._last_update_time = datetime.now()
        self._cached_data = data  # 缓存数据用于切换显示
        self._render_data(data)
    
    def _render_data(self, data):
        """渲染股票数据"""
        # 按配置的顺序获取股票列表
        stock_order = self.controller.get_stocks_list()
        current_codes = set(data.keys())
        existing_codes = set(self.labels.keys())

        # 清理已移除的
        for code in existing_codes - current_codes:
            self.content_layout.removeWidget(self.labels[code])
            self.labels[code].deleteLater()
            del self.labels[code]

        # 按配置的顺序排列
        sorted_codes = [c for c in stock_order if c in data]
        
        for code in sorted_codes:
            info = data[code]
            
            # 计算涨跌颜色和符号
            try:
                if '%' in info['ratio']:
                    ratio_val = float(info['ratio'].replace('%', ''))
                else:
                    ratio_val = 0.0
            except:
                ratio_val = 0.0

            if ratio_val > 0:
                color = self.theme.get("COLOR_UP", "#FF6B6B")
                symbol = "▲"
            elif ratio_val < 0:
                color = self.theme.get("COLOR_DOWN", "#4ECDC4")
                symbol = "▼"
            else:
                color = self.theme.get("COLOR_FLAT", "#F7F7F7")
                symbol = "●"

            # 识别市场类型
            market_prefix = self._get_market_prefix(code)
            
            # 根据显示模式选择显示涨跌幅还是涨跌额
            if self._show_ratio:
                change_display = info['ratio']
            else:
                increase = info.get('increase', '--')
                change_display = str(increase)
            
            # 格式: [市场] 名称 价格 涨跌幅/涨跌额 符号
            name_display = f"{market_prefix}{info['name']}" if market_prefix else info['name']
            display_text = f"{name_display}  {info['price']}  {change_display} {symbol}"
            
            # 丰富的悬停提示
            high = info.get('high', '--')
            low = info.get('low', '--')
            open_price = info.get('open', '--')
            increase = info.get('increase', '--')
            
            mode_hint = "涨跌幅" if self._show_ratio else "涨跌额"
            tooltip = (
                f"📊 {info['name']} ({code})\n"
                f"━━━━━━━━━━━━━━\n"
                f"💰 现价: {info['price']}\n"
                f"📈 涨跌幅: {info['ratio']}\n"
                f"📉 涨跌额: {increase}\n"
                f"📊 今开: {open_price}\n"
                f"🔺 最高: {high}\n"
                f"🔻 最低: {low}\n"
                f"📦 成交量: {info['volume']}\n"
                f"━━━━━━━━━━━━━━\n"
                f"💡 双击展开 | 右键切换{mode_hint}"
            )

            if code not in self.labels:
                lbl = QLabel(display_text)
                
                # 阴影效果
                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(12)
                shadow.setColor(QColor(self.theme.get("MINI_TEXT_SHADOW", "#000000"))) # Themed shadow
                shadow.setOffset(1, 1)
                lbl.setGraphicsEffect(shadow)
                
                self.content_layout.addWidget(lbl)
                self.labels[code] = lbl
            
            # 更新标签
            lbl = self.labels[code]
            lbl.setText(display_text)
            lbl.setToolTip(tooltip)
            
            # 动态样式
            lbl.setStyleSheet(f"""
                color: {color}; 
                font-weight: bold; 
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif; 
                font-size: 13pt;
                padding: 2px 4px;
                background: transparent;
            """)

        self.adjustSize()

    # --- Interaction ---
    def mousePressEvent(self, event):
        if self.is_locked: 
            return
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self.is_locked: 
            return
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if self.old_pos:
            self.controller.config.update_window_settings("mini_pos", [self.x(), self.y()])
            self.old_pos = None
            if self.is_hovered:
                self.setCursor(Qt.OpenHandCursor)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.switch_to_expanded.emit()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { 
                background-color: #1e1e1e; 
                color: #e0e0e0; 
                border: 1px solid #4ECDC4; 
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item { 
                padding: 8px 25px;
                border-radius: 4px;
            }
            QMenu::item:selected { 
                background-color: rgba(78, 205, 196, 0.3); 
            }
            QMenu::separator {
                height: 1px;
                background: #3e3e3e;
                margin: 5px 10px;
            }
        """)
        
        # 切换涨跌幅/涨跌额
        if self._show_ratio:
            toggle_text = "📉 显示涨跌额"
        else:
            toggle_text = "📈 显示涨跌幅"
        toggle_action = QAction(toggle_text, self)
        toggle_action.triggered.connect(self._toggle_display_mode)
        menu.addAction(toggle_action)
        
        menu.addSeparator()
        
        # 锁定位置
        lock_icon = "🔒" if self.is_locked else "🔓"
        lock_action = QAction(f"{lock_icon} {'解锁位置' if self.is_locked else '锁定位置'}", self)
        lock_action.setCheckable(True)
        lock_action.setChecked(self.is_locked)
        lock_action.triggered.connect(self.toggle_lock)
        menu.addAction(lock_action)
        
        menu.addSeparator()
        
        # 立即刷新
        refresh_action = QAction("🔄 立即刷新", self)
        refresh_action.triggered.connect(self.controller._on_timer_tick)
        menu.addAction(refresh_action)

        # 展开设置
        expand_action = QAction("⚙️ 展开设置", self)
        expand_action.triggered.connect(self.switch_to_expanded.emit)
        menu.addAction(expand_action)
        
        menu.addSeparator()

        # 退出程序
        exit_action = QAction("❌ 退出程序", self)
        exit_action.triggered.connect(self.close_app.emit)
        menu.addAction(exit_action)

        menu.exec(event.globalPos())

    def toggle_lock(self):
        self.is_locked = not self.is_locked
        if self.is_hovered:
            self.setCursor(Qt.ArrowCursor if self.is_locked else Qt.OpenHandCursor)

    def _toggle_display_mode(self):
        """切换涨跌幅/涨跌额显示模式"""
        self._show_ratio = not self._show_ratio
        # 用缓存的数据重新渲染
        if self._cached_data:
            self._render_data(self._cached_data)

    def showEvent(self, event):
        # 恢复位置
        pos = self.controller.config.get_window_settings().get("mini_pos", [100, 100])
        self.move(int(pos[0]), int(pos[1]))
        super().showEvent(event)

    def _get_market_prefix(self, code: str) -> str:
        """
        根据股票代码识别市场类型，返回对应前缀
        """
        code = str(code).strip()
        
        # 港股 - 5位数字
        if len(code) == 5 and code.isdigit():
            return "[港] "
        
        # A股
        if len(code) == 6 and code.isdigit():
            # 沪市：60开头（主板）、68开头（科创板）
            if code.startswith('60') or code.startswith('68'):
                return "[沪] "
            # 深市：00开头（主板）、30开头（创业板）
            elif code.startswith('00') or code.startswith('30'):
                return "[深] "
            # 北交所：8开头
            elif code.startswith('8') or code.startswith('4'):
                return "[北] "
        
        # 无法识别的保持空
        return ""


