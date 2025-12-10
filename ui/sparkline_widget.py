
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen, QBrush
from PySide6.QtCore import Qt

class SparklineWidget(QWidget):
    """
    Minimalist sparkline chart for list view.
    Renders a line chart. Parts above baseline (pre_close) are Red, below are Green.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.points = []
        self.pre_close = 0.0
        self.setMinimumWidth(60)
        self.setMinimumHeight(20)
        # Colors (Hardcoded to match app theme)
        self.color_up = QColor("#FF6B6B")
        self.color_down = QColor("#4ECDC4")
        self.color_line = QColor("#aaaaaa") 

    def set_theme_colors(self, up_color, down_color):
        self.color_up = QColor(up_color)
        self.color_down = QColor(down_color)
        self.update()

    def set_data(self, points, pre_close, code=""):
        """
        points: list of dicts with 'price' key
        pre_close: float
        code: stock code (to determine market type)
        """
        self.points = points
        self.pre_close = pre_close
        self.code = str(code)
        self.update()

    def paintEvent(self, event):
        if not self.points or self.pre_close <= 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Geometry
        w = self.width()
        h = self.height()
        
        # 1. Generate standardized time slots
        market_type = "A"
        if self.code.startswith("0") and len(self.code) == 5:
            market_type = "HK"
            
        time_slots = []
        if market_type == "HK":
            for m in range(30, 60): time_slots.append(f"09:{m:02d}")
            for h in range(10, 12):
                for m in range(60): time_slots.append(f"{h:02d}:{m:02d}")
            time_slots.append("12:00")
            for h in range(13, 16):
                for m in range(60): time_slots.append(f"{h:02d}:{m:02d}")
            time_slots.append("16:00")
        else: # A-Share
            for m in range(30, 60): time_slots.append(f"09:{m:02d}")
            for m in range(60): time_slots.append(f"10:{m:02d}")
            for m in range(30): time_slots.append(f"11:{m:02d}")
            time_slots.append("11:30")
            for h in range(13, 15):
                for m in range(60): time_slots.append(f"{h:02d}:{m:02d}")
            time_slots.append("15:00")

        total_minutes = len(time_slots)
        
        # 2. Map data
        price_map = {p['time']: p['price'] for p in self.points}
        
        final_x = []
        final_prices = []
        last_valid_price = self.pre_close
        
        # Determine how far to draw
        last_time = self.points[-1]['time']
        try:
            current_idx = time_slots.index(last_time)
        except ValueError:
            current_idx = len(self.points) - 1 # Fallback
            # If fallback, we can't use time mapping easily? 
            # Actually if fallback, current_idx might be meaningless for x_map using total_minutes.
            # Let's trust A/HK logic covers most. If failing, just draw linearly?
            # For robustness, if fallback, use linear plotting of points.
            pass
            
        # Robust linear fallback check
        use_linear = False
        if last_time not in time_slots:
             use_linear = True
             
        if use_linear:
             # Old simple logic
             prices = [p["price"] for p in self.points]
             x_ind = list(range(len(prices)))
             total_x_range = len(prices) - 1 if len(prices) > 1 else 1
        else:
            # Time mapped logic
            for i in range(current_idx + 1):
                t_str = time_slots[i]
                if t_str in price_map:
                    p = price_map[t_str]
                    final_x.append(i)
                    final_prices.append(p)
                    last_valid_price = p
                else:
                    if final_prices:
                        final_x.append(i)
                        final_prices.append(last_valid_price)
            
            prices = final_prices
            x_ind = final_x
            total_x_range = total_minutes - 1 # Fixed width scale

        if not prices:
             return

        # Determine limits
        min_p = min(min(prices), self.pre_close)
        max_p = max(max(prices), self.pre_close)
        rng = max_p - min_p if max_p != min_p else 1.0
        
        # Scaling functions
        def x_map(i):
            return i / total_x_range * w

        def y_map(p):
            ratio = (p - min_p) / rng
            return h - (ratio * h)

        # Draw Baseline
        y_base = y_map(self.pre_close)
        painter.setPen(QPen(QColor(60, 60, 60), 1, Qt.DashLine))
        painter.drawLine(0, y_base, w, y_base)

        pen_width = 1.5
        
        for k in range(len(prices) - 1):
            i1 = x_ind[k]
            i2 = x_ind[k+1]
            p1 = prices[k]
            p2 = prices[k+1]
            
            x1 = x_map(i1)
            y1 = y_map(p1)
            x2 = x_map(i2)
            y2 = y_map(p2)
            
            mid_val = (p1 + p2) / 2
            if mid_val >= self.pre_close:
                painter.setPen(QPen(self.color_up, pen_width))
            else:
                painter.setPen(QPen(self.color_down, pen_width))
                
            painter.drawLine(x1, y1, x2, y2)
