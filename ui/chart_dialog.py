"""
分时走势图对话框
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QApplication
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor

try:
    import pyqtgraph as pg
    HAS_PYQTGRAPH = True
except ImportError:
    HAS_PYQTGRAPH = False


class ChartDialog(QDialog):
    """分时走势图对话框"""
    
    def __init__(self, controller, stock_code: str, stock_name: str, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.theme = self.controller.theme_manager.get_current_theme()
        
        self.setWindowTitle(f"分时走势 - {stock_name} ({stock_code})")
        self.resize(700, 450)
        self.setStyleSheet(self.controller.theme_manager.get_style())
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 顶部信息栏
        header = QHBoxLayout()
        
        self.title_label = QLabel(f"📊 {self.stock_name} ({self.stock_code})")
        self.title_label.setProperty("class", "chart-title")
        header.addWidget(self.title_label)
        
        header.addStretch()
        
        self.price_label = QLabel("--")
        self.price_label.setProperty("class", "chart-price")
        header.addWidget(self.price_label)
        
        self.change_label = QLabel("--")
        self.change_label.setProperty("class", "chart-change")
        header.addWidget(self.change_label)
        
        layout.addLayout(header)
        
        # 图表区域
        if HAS_PYQTGRAPH:
            # 配置 pyqtgraph 样式
            pg.setConfigOptions(antialias=True)
            
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.setBackground(self.theme['APP_BG'])
            self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
            
            # 设置坐标轴样式
            axis_pen = pg.mkPen(color=self.theme['BORDER_COLOR'])
            text_pen = pg.mkPen(color=self.theme['TEXT_COLOR'])
            self.plot_widget.getAxis('left').setPen(axis_pen)
            self.plot_widget.getAxis('bottom').setPen(axis_pen)
            self.plot_widget.getAxis('left').setTextPen(text_pen)
            self.plot_widget.getAxis('bottom').setTextPen(text_pen)
            
            layout.addWidget(self.plot_widget)
        else:
            # 没有 pyqtgraph 时显示提示
            no_chart_label = QLabel("需要安装 pyqtgraph 才能显示图表\npip install pyqtgraph")
            no_chart_label.setAlignment(Qt.AlignCenter)
            no_chart_label.setProperty("class", "chart-placeholder")
            layout.addWidget(no_chart_label)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        
        self.status_label = QLabel("加载中...")
        self.status_label.setProperty("class", "text-secondary")
        self.status_label.setStyleSheet("font-size: 11px;")
        btn_layout.addWidget(self.status_label)
        
        btn_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self._load_data)
        btn_layout.addWidget(refresh_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_data(self):
        """加载分时数据"""
        self.status_label.setText("加载中...")
        QApplication.processEvents()
        
        result = self.controller.api_client.fetch_minute_data(self.stock_code)
        
        if not result.get("success"):
            self.status_label.setText(f"加载失败: {result.get('error', '未知错误')}")
            return
        
        data = result["data"]
        points = data.get("points", [])
        pre_close = data.get("preClose", 0)
        
        if not points:
            self.status_label.setText("暂无分时数据")
            return
        
        # 更新价格信息
        last_point = points[-1]
        current_price = last_point["price"]
        change = last_point["change"]
        change_pct = last_point["change_pct"]
        
        self.price_label.setText(f"{current_price:.2f}")
        
        if change >= 0:
            color = self.theme['COLOR_UP']
        else:
            color = self.theme['COLOR_DOWN']
            
        # Only setting color, font sizes handled by class
        self.price_label.setStyleSheet(f"color: {color};")
        
        sign = "+" if change >= 0 else ""
        self.change_label.setText(f"{sign}{change:.2f} ({sign}{change_pct:.2f}%)")
        self.change_label.setStyleSheet(f"color: {color};")
        
        if HAS_PYQTGRAPH:
            self._draw_chart(points, pre_close)
        
        self.status_label.setText(f"共 {len(points)} 个数据点")
    
    def _draw_chart(self, points, pre_close):
        """绘制分时图，根据市场交易时间对齐坐标轴"""
        self.plot_widget.clear()
        
        if not points:
            return
        
        # 1. 确定市场类型和交易时间段
        # 默认 A股: 9:30-11:30, 13:00-15:00 (共241分钟, 含9:30和15:00, 通常API给的点数是241或240)
        # 港股: 9:30-12:00, 13:00-16:00 (共330分钟)
        market_type = "A"
        if self.stock_code.startswith("0") and len(self.stock_code) == 5:
            market_type = "HK"
        
        # 生成标准时间轴
        time_slots = []
        if market_type == "HK":
            # Morning: 9:30 - 12:00
            # 9:30 - 9:59
            for m in range(30, 60): time_slots.append(f"09:{m:02d}")
            # 10:00 - 11:59
            for h in range(10, 12):
                for m in range(60): time_slots.append(f"{h:02d}:{m:02d}")
            time_slots.append("12:00")
            
            # Afternoon: 13:00 - 16:00
            # 13:00 - 15:59
            for h in range(13, 16):
                for m in range(60): time_slots.append(f"{h:02d}:{m:02d}")
            time_slots.append("16:00")
            
        else: # A-Share
            # Morning: 9:30 - 11:30
            # 9:30 - 9:59
            for m in range(30, 60): time_slots.append(f"09:{m:02d}")
            # 10:00 - 10:59
            for m in range(60): time_slots.append(f"10:{m:02d}")
            # 11:00 - 11:29
            for m in range(30): time_slots.append(f"11:{m:02d}")
            time_slots.append("11:30")
            
            # Afternoon: 13:00 - 15:00
            # 13:00 - 14:59
            for h in range(13, 15):
                for m in range(60): time_slots.append(f"{h:02d}:{m:02d}")
            time_slots.append("15:00")
            
        # 2. 映射数据点到时间轴
        total_minutes = len(time_slots)
        
        # ... (Data mapping logic remains conceptually same but ensure we use updated time_slots)
        
        price_map = {} 
        avg_price_map = {}
        for p in points:
            price_map[p['time']] = p['price']
            avg_price_map[p['time']] = p.get('avg_price', 0)
            
        last_time = points[-1]['time']
        
        # Robust Index Finding
        current_idx = 0
        if last_time in time_slots:
            current_idx = time_slots.index(last_time)
        else:
            # Try to find closest time slot (e.g. "15:01" -> "15:00")
            # Or just use total length if it's already closed?
            # Basic fallback: match by string comparison or just linear fill?
            # Since this is a chart, correct positioning is key.
            # Let's try to match HH:MM
            try:
                # If exact match fails, check if time > last slot (market closed) -> use last slot
                if last_time > time_slots[-1]:
                    current_idx = len(time_slots) - 1
                elif last_time < time_slots[0]:
                    current_idx = 0
                else:
                    # Search for insertion point?
                    # Simple fallback: linear last index
                    current_idx = len(points) - 1
            except:
                 current_idx = len(points) - 1
            
        final_x = []
        final_prices = []
        final_avgs = []
        
        last_valid_price = pre_close
        last_valid_avg = pre_close
        
        for i in range(current_idx + 1):
            t_str = time_slots[i]
            if t_str in price_map:
                p = price_map[t_str]
                a = avg_price_map[t_str]
                final_x.append(i)
                final_prices.append(p)
                final_avgs.append(a)
                last_valid_price = p
                last_valid_avg = a
            else:
                # Fill gaps
                if final_prices:
                    final_x.append(i)
                    final_prices.append(last_valid_price)
                    final_avgs.append(last_valid_avg)

        # 绘制曲线
        # 昨收基准线
        line_base = pg.InfiniteLine(angle=0, movable=False, pos=pre_close, 
                                  pen=pg.mkPen(color=self.theme['COLOR_FLAT'], style=Qt.DashLine, width=1))
        self.plot_widget.addItem(line_base)
        
        # 均价线 (黄色/橙色)
        self.plot_widget.plot(final_x, final_avgs, 
                            pen=pg.mkPen(color='#ffc107', width=1.5), name="均价")
        
        # 价格线 (分段绘制以实现涨红跌绿)
        # 这种方式对于点数较少(分时图约240点)是性能可接受的
        for i in range(len(final_x) - 1):
            x_seg = [final_x[i], final_x[i+1]]
            y_seg = [final_prices[i], final_prices[i+1]]
            
            # 颜色逻辑：根据最新点于昨收的关系
            # 如果 y > pre_close 用红，否则用绿
            # 或者更细致：如果整段都在上方红，都在下方绿，跨越则拆分？
            # 简单策略：由终点决定颜色 (最常见做法)
            is_up = final_prices[i+1] >= pre_close
            seg_color = self.theme['COLOR_UP'] if is_up else self.theme['COLOR_DOWN']
            
            self.plot_widget.plot(x_seg, y_seg, pen=pg.mkPen(color=seg_color, width=2))

        # 添加一个淡色的填充 (可选)
        # self.plot_widget.plot(final_x, final_prices, pen=None, fillLevel=pre_close, brush=(100, 100, 100, 20))
        

        
        # Connect the segments
        # This draws line segments colored by value vs pre_close
        for i in range(len(final_x) - 1):
            x1, x2 = final_x[i], final_x[i+1]
            y1, y2 = final_prices[i], final_prices[i+1]
            
            # Determine color logic
            # Use y2 comparison? Or max(y1, y2)?
            # Standard: if current point >= pre_close -> Red
            is_up = y2 >= pre_close
            seg_color = self.theme['COLOR_UP'] if is_up else self.theme['COLOR_DOWN']
            
            self.plot_widget.plot([x1, x2], [y1, y2], pen=pg.mkPen(color=seg_color, width=2))

        # Add fill for entire curve (optional, generic faint color)
        # fill_curve = self.plot_widget.plot(final_x, final_prices, pen=None, fillLevel=pre_close, brush=(50, 50, 50, 30))
        

        # 设置 X 轴标签
        # A股: 9:30, 10:30, 11:30/13:00 (Center), 14:00, 15:00
        ticks = []
        
        if market_type == "HK":
            key_times = ["09:30", "10:30", "11:30", "13:00", "14:00", "15:00"]
        else:
            # 11:30 & 13:00 are adjacent. Showing both overlaps.
            # We can show "11:30/13:00" at the midpoint?
            # Or just show 11:30.
            key_times = ["09:30", "10:30", "11:30", "14:00", "15:00"]
            
        for kt in key_times:
            if kt in time_slots:
                idx = time_slots.index(kt)
                ticks.append((idx, kt))
        
        # Add a special separator tick or combined label if needed?
        # For now, distinct labels are fine if selected carefully to not overlap.
        
        self.plot_widget.getAxis('bottom').setTicks([ticks])
        self.plot_widget.setXRange(0, total_minutes) # 固定 X 轴范围
        
        # 自动调整 Y 轴范围
        valid_values = final_prices + ([pre_close] if pre_close > 0 else [])
        if valid_values:
            min_price = min(valid_values)
            max_price = max(valid_values)
            if min_price == max_price:
                margin = min_price * 0.01
            else:
                margin = (max_price - min_price) * 0.1
            self.plot_widget.setYRange(min_price - margin, max_price + margin)
