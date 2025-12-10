"""
价格提醒管理器
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AlertType(Enum):
    """提醒类型"""
    PRICE_ABOVE = "price_above"  # 价格高于
    PRICE_BELOW = "price_below"  # 价格低于
    CHANGE_ABOVE = "change_above"  # 涨幅超过
    CHANGE_BELOW = "change_below"  # 跌幅超过


@dataclass
class AlertRule:
    """提醒规则"""
    code: str  # 股票代码
    alert_type: AlertType
    threshold: float  # 阈值
    enabled: bool = True
    triggered: bool = False  # 是否已触发（避免重复提醒）
    
    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "alert_type": self.alert_type.value,
            "threshold": self.threshold,
            "enabled": self.enabled,
            "triggered": self.triggered
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AlertRule":
        return cls(
            code=data["code"],
            alert_type=AlertType(data["alert_type"]),
            threshold=data["threshold"],
            enabled=data.get("enabled", True),
            triggered=data.get("triggered", False)
        )


class AlertManager:
    """提醒管理器"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.rules: List[AlertRule] = []
        self._load_rules()
    
    def _load_rules(self):
        """从配置加载规则"""
        rules_data = self.config.data.get("alerts", [])
        self.rules = [AlertRule.from_dict(r) for r in rules_data]
    
    def _save_rules(self):
        """保存规则到配置"""
        self.config.data["alerts"] = [r.to_dict() for r in self.rules]
        self.config.save()
    
    def add_rule(self, rule: AlertRule):
        """添加规则"""
        self.rules.append(rule)
        self._save_rules()
    
    def remove_rule(self, code: str, alert_type: AlertType):
        """移除规则"""
        self.rules = [r for r in self.rules if not (r.code == code and r.alert_type == alert_type)]
        self._save_rules()
    
    def get_rules_for_stock(self, code: str) -> List[AlertRule]:
        """获取某只股票的所有规则"""
        return [r for r in self.rules if r.code == code]
    
    def reset_triggered(self, code: str):
        """重置某只股票的触发状态"""
        for rule in self.rules:
            if rule.code == code:
                rule.triggered = False
        self._save_rules()
    
    def check_alerts(self, stock_data: Dict) -> List[tuple]:
        """
        检查是否触发提醒
        返回: [(rule, stock_info), ...] 触发的规则列表
        """
        triggered = []
        
        for rule in self.rules:
            if not rule.enabled or rule.triggered:
                continue
            
            if rule.code not in stock_data:
                continue
            
            info = stock_data[rule.code]
            price = float(info.get("price", 0))
            
            # 解析涨跌幅
            ratio_str = info.get("ratio", "0%")
            try:
                ratio = float(ratio_str.replace("%", ""))
            except:
                ratio = 0.0
            
            should_trigger = False
            
            if rule.alert_type == AlertType.PRICE_ABOVE:
                should_trigger = price >= rule.threshold
            elif rule.alert_type == AlertType.PRICE_BELOW:
                should_trigger = price <= rule.threshold
            elif rule.alert_type == AlertType.CHANGE_ABOVE:
                should_trigger = ratio >= rule.threshold
            elif rule.alert_type == AlertType.CHANGE_BELOW:
                should_trigger = ratio <= -abs(rule.threshold)
            
            if should_trigger:
                rule.triggered = True
                triggered.append((rule, info))
                logger.info(f"Alert triggered: {rule.code} {rule.alert_type.value} {rule.threshold}")
        
        if triggered:
            self._save_rules()
        
        return triggered
