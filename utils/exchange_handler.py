"""
Binance और CoinDCX एक्सचेंज हैंडलर
"""

import ccxt
from typing import Dict, Optional, Any
import hmac
import hashlib
import time
import requests

class ExchangeManager:
    def __init__(self):
        self.exchanges = {}
    
    def add_exchange(self, name: str, config: Dict[str, Any]):
        """
        एक्सचेंज ऐड करें
        
        Args:
            name: एक्सचेंज का नाम (binance, coindcx)
            config: एक्सचेंज कॉन्फ़िगरेशन
        """
        if name.lower() == 'binance':
            exchange = BinanceExchange(config)
        elif name.lower() == 'coindcx':
            exchange = CoinDCXExchange(config)
        else:
            raise ValueError(f"असमर्थित एक्सचेंज: {name}")
        
        self.exchanges[name.lower()] = exchange
    
    def get_exchange(self, name: str):
        """
        एक्सचेंज ऑब्जेक्ट प्राप्त करें
        
        Args:
            name: एक्सचेंज का नाम
            
        Returns:
            एक्सचेंज ऑब्जेक्ट या None
        """
        return self.exchanges.get(name.lower())


class BaseExchange:
    """बेस एक्सचेंज क्लास"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key', '')
        self.api_secret = config.get('api_secret', '')
        self.testnet = config.get('testnet', False)
        
    def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100):
        """OHLCV डेटा फ़ैच करें"""
        raise NotImplementedError
    
    def create_market_buy_order(self, symbol: str, amount: float):
        """मार्केट BUY ऑर्डर क्रिएट करें"""
        raise NotImplementedError
    
    def create_market_sell_order(self, symbol: str, amount: float):
        """मार्केट SELL ऑर्डर क्रिएट करें"""
        raise NotImplementedError
    
    def get_balance(self):
        """बैलेंस प्राप्त करें"""
        raise NotImplementedError


class BinanceExchange(BaseExchange):
    """Binance एक्सचेंज हैंडलर"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        exchange_params = {
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
        }
        
        if self.testnet:
            exchange_params['urls'] = {
                'api': {
                    'public': 'https://testnet.binance.vision/api',
                    'private': 'https://testnet.binance.vision/api',
                }
            }
        
        self.exchange = ccxt.binance(exchange_params)
    
    def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100):
        return self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    
    def create_market_buy_order(self, symbol: str, amount: float):
        return self.exchange.create_market_buy_order(symbol, amount)
    
    def create_market_sell_order(self, symbol: str, amount: float):
        return self.exchange.create_market_sell_order(symbol, amount)
    
    def get_balance(self):
        return self.exchange.fetch_balance()


class CoinDCXExchange(BaseExchange):
    """CoinDCX एक्सचेंज हैंडलर"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://api.coindcx.com"
        
    def _generate_signature(self, data: str) -> str:
        """सिग्नेचर जनरेट करें"""
        return hmac.new(
            self.api_secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100):
        """
        CoinDCX से OHLCV डेटा फ़ैच करें
        
        Note: CoinDCX की अलग API स्ट्रक्चर है
        """
        # CoinDCX API के अनुसार इम्प्लीमेंट करें
        endpoint = f"{self.base_url}/exchange/trading/v1/ohlcv"
        
        # Symbol को CoinDCX फ़ॉर्मेट में कन्वर्ट करें
        coindcx_symbol = self._convert_to_coindcx_symbol(symbol)
        
        params = {
            'pair': coindcx_symbol,
            'interval': timeframe,
            'limit': limit
        }
        
        response = requests.get(endpoint, params=params)
        data = response.json()
        
        return data
    
    def create_market_buy_order(self, symbol: str, amount: float):
        """मार्केट BUY ऑर्डर क्रिएट करें"""
        endpoint = f"{self.base_url}/exchange/v1/orders/create"
        
        coindcx_symbol = self._convert_to_coindcx_symbol(symbol)
        
        order_data = {
            "side": "buy",
            "order_type": "market_order",
            "market": coindcx_symbol,
            "total_quantity": amount,
            "timestamp": int(time.time() * 1000)
        }
        
        # सिग्नेचर जनरेट करें
        signature = self._generate_signature(str(order_data))
        
        headers = {
            'X-AUTH-APIKEY': self.api_key,
            'X-AUTH-SIGNATURE': signature
        }
        
        response = requests.post(endpoint, json=order_data, headers=headers)
        return response.json()
    
    def create_market_sell_order(self, symbol: str, amount: float):
        """मार्केट SELL ऑर्डर क्रिएट करें"""
        endpoint = f"{self.base_url}/exchange/v1/orders/create"
        
        coindcx_symbol = self._convert_to_coindcx_symbol(symbol)
        
        order_data = {
            "side": "sell",
            "order_type": "market_order",
            "market": coindcx_symbol,
            "total_quantity": amount,
            "timestamp": int(time.time() * 1000)
        }
        
        # सिग्नेचर जनरेट करें
        signature = self._generate_signature(str(order_data))
        
        headers = {
            'X-AUTH-APIKEY': self.api_key,
            'X-AUTH-SIGNATURE': signature
        }
        
        response = requests.post(endpoint, json=order_data, headers=headers)
        return response.json()
    
    def _convert_to_coindcx_symbol(self, symbol: str) -> str:
        """
        स्टैंडर्ड सिंबल फ़ॉर्मेट को CoinDCX फ़ॉर्मेट में कन्वर्ट करें
        
        उदाहरण: BTC/USDT -> B-BTC_USDT
        """
        if '/' in symbol:
            base, quote = symbol.split('/')
            return f"B-{base}_{quote}"
        return symbol
    
    def get_balance(self):
        """बैलेंस प्राप्त करें"""
        endpoint = f"{self.base_url}/exchange/v1/users/balances"
        
        timestamp = int(time.time() * 1000)
        data = {"timestamp": timestamp}
        
        signature = self._generate_signature(str(data))
        
        headers = {
            'X-AUTH-APIKEY': self.api_key,
            'X-AUTH-SIGNATURE': signature
        }
        
        response = requests.post(endpoint, json=data, headers=headers)
        return response.json()
