#!/usr/bin/env python3
"""
मुख्य ट्रेडिंग बॉट जो सभी सबफ़ोल्डरों में रणनीतियों को स्कैन और एक्सेक्यूट करता है
"""

import os
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import schedule

from utils.file_reader import StrategyLoader
from utils.exchange_handler import ExchangeManager
from utils.logger import TradingLogger

class CryptoMultiFolderBot:
    def __init__(self, base_strategy_path: str = "strategies"):
        """
        बॉट को इनिशियलाइज़ करें
        
        Args:
            base_strategy_path: रणनीतियों का बेस पाथ
        """
        self.base_path = Path(base_strategy_path)
        self.strategy_loader = StrategyLoader()
        self.exchange_manager = ExchangeManager()
        self.logger = TradingLogger()
        
        # एक्टिव रणनीतियों को स्टोर करने के लिए
        self.active_strategies: Dict[str, Dict] = {}
        
        # ट्रेडिंग स्टेटस
        self.is_running = False
        
    def load_all_strategies(self) -> List[Dict[str, Any]]:
        """
        सभी फ़ोल्डर और सबफ़ोल्डर से रणनीतियाँ लोड करें
        
        Returns:
            लोड की गई सभी रणनीतियों की लिस्ट
        """
        strategies = []
        
        # रिकर्सिवली सभी सबफ़ोल्डर स्कैन करें
        for strategy_dir in self.base_path.rglob('*'):
            if strategy_dir.is_dir():
                strategy_data = self.strategy_loader.load_strategy(strategy_dir)
                if strategy_data:
                    strategies.append(strategy_data)
                    self.logger.info(f"रणनीति लोड की गई: {strategy_dir.name}")
        
        return strategies
    
    def initialize_exchanges(self, config_path: str = "config/exchanges"):
        """
        Binance और CoinDCX एक्सचेंज इनिशियलाइज़ करें
        """
        config_dir = Path(config_path)
        
        # Binance कॉन्फ़िग
        binance_config = config_dir / "binance_config.json"
        if binance_config.exists():
            with open(binance_config, 'r') as f:
                config = json.load(f)
            self.exchange_manager.add_exchange("binance", config)
            self.logger.info("Binance एक्सचेंज इनिशियलाइज़ हो गया")
        
        # CoinDCX कॉन्फ़िग
        coindcx_config = config_dir / "coindcx_config.json"
        if coindcx_config.exists():
            with open(coindcx_config, 'r') as f:
                config = json.load(f)
            self.exchange_manager.add_exchange("coindcx", config)
            self.logger.info("CoinDCX एक्सचेंज इनिशियलाइज़ हो गया")
    
    def execute_strategy(self, strategy: Dict[str, Any]):
        """
        एक रणनीति को एक्सेक्यूट करें
        
        Args:
            strategy: रणनीति का डेटा
        """
        try:
            strategy_name = strategy['name']
            exchange_name = strategy['config'].get('exchange', 'binance')
            
            # एक्सचेंज ऑब्जेक्ट प्राप्त करें
            exchange = self.exchange_manager.get_exchange(exchange_name)
            if not exchange:
                self.logger.error(f"{exchange_name} एक्सचेंज उपलब्ध नहीं है")
                return
            
            # मार्केट डेटा प्राप्त करें
            symbol = strategy['config'].get('symbol', 'BTC/USDT')
            timeframe = strategy['config'].get('timeframe', '1h')
            
            # ओएचएलसीवी डेटा फ़ैच करें
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
            
            # रणनीति लॉजिक एक्सेक्यूट करें
            if 'module' in strategy:
                signal = strategy['module'].generate_signal(ohlcv, strategy['config'])
                
                # ट्रेड एक्सेक्यूट करें
                if signal == 'BUY':
                    self.execute_buy(exchange, strategy)
                elif signal == 'SELL':
                    self.execute_sell(exchange, strategy)
                elif signal == 'HOLD':
                    self.logger.info(f"{strategy_name}: होल्ड सिग्नल")
            
        except Exception as e:
            self.logger.error(f"रणनीति एक्सेक्यूशन में त्रुटि: {str(e)}")
    
    def execute_buy(self, exchange, strategy: Dict[str, Any]):
        """
        BUY ऑर्डर एक्सेक्यूट करें
        """
        try:
            symbol = strategy['config'].get('symbol', 'BTC/USDT')
            amount = strategy['config'].get('trade_amount', 0.001)
            
            order = exchange.create_market_buy_order(symbol, amount)
            self.logger.info(f"BUY ऑर्डर एक्सेक्यूट हुई: {order}")
            
            # ऑर्डर डिटेल्स लॉग करें
            self.logger.trade_log(
                action="BUY",
                symbol=symbol,
                amount=amount,
                price=order.get('price', 'N/A'),
                strategy=strategy['name']
            )
            
        except Exception as e:
            self.logger.error(f"BUY ऑर्डर में त्रुटि: {str(e)}")
    
    def execute_sell(self, exchange, strategy: Dict[str, Any]):
        """
        SELL ऑर्डर एक्सेक्यूट करें
        """
        try:
            symbol = strategy['config'].get('symbol', 'BTC/USDT')
            amount = strategy['config'].get('trade_amount', 0.001)
            
            order = exchange.create_market_sell_order(symbol, amount)
            self.logger.info(f"SELL ऑर्डर एक्सेक्यूट हुई: {order}")
            
            # ऑर्डर डिटेल्स लॉग करें
            self.logger.trade_log(
                action="SELL",
                symbol=symbol,
                amount=amount,
                price=order.get('price', 'N/A'),
                strategy=strategy['name']
            )
            
        except Exception as e:
            self.logger.error(f"SELL ऑर्डर में त्रुटि: {str(e)}")
    
    def run_strategies(self):
        """
        सभी एक्टिव रणनीतियों को रन करें
        """
        if not self.active_strategies:
            self.logger.warning("कोई एक्टिव रणनीति नहीं मिली")
            return
        
        self.logger.info(f"{len(self.active_strategies)} रणनीतियाँ एक्सेक्यूट हो रही हैं...")
        
        for strategy_name, strategy_data in self.active_strategies.items():
            # प्रत्येक रणनीति को अलग थ्रेड में रन करें
            thread = threading.Thread(
                target=self.execute_strategy,
                args=(strategy_data,)
            )
            thread.start()
    
    def start(self, interval_minutes: int = 5):
        """
        बॉट स्टार्ट करें
        
        Args:
            interval_minutes: रणनीति चेक करने का इंटरवल (मिनटों में)
        """
        self.logger.info("क्रिप्टो ट्रेडिंग बॉट स्टार्ट हो रहा है...")
        
        # एक्सचेंज इनिशियलाइज़ करें
        self.initialize_exchanges()
        
        # सभी रणनीतियाँ लोड करें
        strategies = self.load_all_strategies()
        
        if not strategies:
            self.logger.error("कोई रणनीति नहीं मिली!")
            return
        
        # रणनीतियों को एक्टिव लिस्ट में जोड़ें
        for strategy in strategies:
            self.active_strategies[strategy['name']] = strategy
        
        self.is_running = True
        
        # शेड्यूलर सेटअप करें
        schedule.every(interval_minutes).minutes.do(self.run_strategies)
        
        self.logger.info(f"बॉट स्टार्ट हो गया। {interval_minutes} मिनट के इंटरवल पर रणनीतियाँ चेक होंगी।")
        
        # मेन लूप
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("बॉट मैन्युअल बंद किया जा रहा है...")
        except Exception as e:
            self.logger.error(f"अनपेक्षित त्रुटि: {str(e)}")
        finally:
            self.stop()
    
    def stop(self):
        """बॉट स्टॉप करें"""
        self.is_running = False
        self.logger.info("बॉट स्टॉप हो गया")

if __name__ == "__main__":
    # बॉट क्रिएट और स्टार्ट करें
    bot = CryptoMultiFolderBot()
    bot.start(interval_minutes=5)
