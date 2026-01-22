"""
ट्रेडिंग लॉगर
"""

import logging
from datetime import datetime
from pathlib import Path
import json

class TradingLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # मेन लॉगर सेटअप
        self.logger = logging.getLogger("TradingBot")
        self.logger.setLevel(logging.INFO)
        
        # फ़ाइल हैंडलर
        log_file = self.log_dir / f"trading_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # कंसोल हैंडलर
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # फ़ॉर्मैटर
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # ट्रेड लॉग फ़ाइल
        self.trade_log_file = self.log_dir / f"trades_{datetime.now().strftime('%Y%m%d')}.json"
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def trade_log(self, action: str, symbol: str, amount: float, 
                  price: str, strategy: str):
        """
        ट्रेड लॉग रिकॉर्ड करें
        
        Args:
            action: BUY/SELL
            symbol: ट्रेडिंग सिंबल
            amount: क्वांटिटी
            price: प्राइस
            strategy: रणनीति का नाम
        """
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'symbol': symbol,
            'amount': amount,
            'price': price,
            'strategy': strategy
        }
        
        # JSON फ़ाइल में अपेंड करें
        with open(self.trade_log_file, 'a') as f:
            f.write(json.dumps(trade_record) + '\n')
        
        self.info(f"ट्रेड लॉग: {trade_record}")
