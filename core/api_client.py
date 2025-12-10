import time
import logging

try:
    from curl_cffi import requests
except ImportError:
    import requests

logger = logging.getLogger(__name__)

class BaiduApiClient:
    BASE_URL = "https://finance.pae.baidu.com/vapi/v1/getquotation"

    def fetch_quote(self, code: str):
        """
        Fetch stock quote from Baidu Finance API.
        """
        params = {
            "group": "quotation_minute_ab",
            "code": code,
            "query": code,
            "all": 1,
            "finClientType": "pc",
            "_": int(time.time() * 1000)
        }
        
        logger.debug(f"Fetching quote for {code}")
        
        try:
            # 使用 curl_cffi 模拟 Chrome 浏览器的 TLS 指纹
            response = requests.get(
                self.BASE_URL, 
                params=params, 
                impersonate="chrome120",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Check ResultCode (0 is success)
            if str(data.get("ResultCode")) != "0":
                error_msg = f"API returned code {data.get('ResultCode')}"
                logger.warning(f"[{code}] {error_msg}")
                return {"success": False, "error": error_msg}

            result = data.get("Result", {})
            if not result:
                logger.warning(f"[{code}] Empty Result object")
                return {"success": False, "error": "Empty Result object"}

            cur = result.get("cur", {})
            basic = result.get("basicinfos", {})
            
            if not cur:
                logger.warning(f"[{code}] No market data (cur) found")
                return {"success": False, "error": "No market data (cur) found"}

            # 解析盘口信息获取更多数据
            pankou_data = self._parse_pankou(result.get("pankouinfos", {}))
            
            logger.info(f"[{code}] {basic.get('name', 'Unknown')} 价格:{cur.get('price')} 涨跌:{cur.get('ratio')}")

            try:
                pre_close_val = float(pankou_data.get("preClose", 0))
            except (ValueError, TypeError):
                pre_close_val = 0.0

            return {
                "success": True,
                "data": {
                    "code": code,
                    "name": basic.get("name", "Unknown"),
                    "price": float(cur.get("price", 0) or 0),
                    "ratio": cur.get("ratio", "0%"),
                    "increase": cur.get("increase", "0"),
                    "volume": cur.get("volume", "0"),
                    "high": pankou_data.get("high", "--"),
                    "low": pankou_data.get("low", "--"),
                    "open": pankou_data.get("open", "--"),
                    "preClose": pre_close_val,
                    "amount": cur.get("amount", "0"),
                    "turnover": pankou_data.get("turnoverRatio", "--"),
                    "amplitude": pankou_data.get("amplitudeRatio", "--"),
                    "update_time": cur.get("time", 0),
                    "points": self._parse_minute_data(result)
                }
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"[{code}] 请求超时")
            return {"success": False, "error": "请求超时"}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[{code}] 网络连接错误: {e}")
            return {"success": False, "error": f"网络连接错误: {e}"}
        except Exception as e:
            logger.error(f"[{code}] 请求异常: {e}")
            return {"success": False, "error": str(e)}
    
    def _parse_pankou(self, pankouinfos: dict) -> dict:
        """
        解析盘口信息，提取关键数据
        """
        result = {}
        pankou_list = pankouinfos.get("list", [])
        
        for item in pankou_list:
            ename = item.get("ename", "")
            # 使用 originValue 获取原始数值
            value = item.get("originValue", item.get("value", "--"))
            if ename and value:
                result[ename] = value
        
        return result

    def fetch_minute_data(self, code: str):
        """
        获取分时数据，用于绘制分时走势图
        返回: {
            "success": bool,
            "data": {
                "code": str,
                "name": str,
                "preClose": float,  # 昨收价
                "points": [
                    {"time": "09:30", "price": 81.58, "avg_price": 81.58, ...},
                    ...
                ]
            }
        }
        """
        params = {
            "srcid": "5353",
            "all": 1,
            "code": code,
            "query": code,
            "eprop": "min",
            "financeType": "stock",
            "group": "quotation_minute_ab",
            "stock_type": "ab",
            "chartType": "minute",
            "finClientType": "pc",
            "_": int(time.time() * 1000)
        }
        
        try:
            # 使用 curl_cffi 模拟 Chrome 浏览器的 TLS 指纹
            response = requests.get(
                self.BASE_URL, 
                params=params, 
                impersonate="chrome120",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if str(data.get("ResultCode")) != "0":
                return {"success": False, "error": f"API returned code {data.get('ResultCode')}"}
            
            result = data.get("Result", {})
            basic = result.get("basicinfos", {})
            pankou = self._parse_pankou(result.get("pankouinfos", {}))
            
            # 解析分时数据
            points = self._parse_minute_data(result)
            
            pre_close = float(pankou.get("preClose", 0) or 0)
            
            return {
                "success": True,
                "data": {
                    "code": code,
                    "name": basic.get("name", "Unknown"),
                    "preClose": pre_close,
                    "points": points
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_minute_data(self, result: dict) -> list:
        """Helper to parse minute data from Result object"""
        new_market_data = result.get("newMarketData", {})
        market_data_list = new_market_data.get("marketData", [])
        
        if not market_data_list:
            return []
        
        # 解析 p 字段中的分时数据
        points = []
        raw_data = market_data_list[0].get("p", "")
        
        for record in raw_data.split(";"):
            if not record.strip():
                continue
            
            fields = record.split(",")
            if len(fields) >= 10: 
                try:
                    points.append({
                        "timestamp": int(fields[0]),
                        "time": fields[1].split(" ")[-1] if " " in fields[1] else fields[1],
                        "price": float(fields[2]),
                        "avg_price": float(fields[3]),
                        "change": float(fields[4]),
                        "change_pct": float(fields[5]),
                        "volume": int(fields[6]),
                        "amount": float(fields[7]),
                        "total_volume": int(fields[8]),
                        "total_amount": float(fields[9])
                    })
                except (ValueError, IndexError):
                    continue
        return points

