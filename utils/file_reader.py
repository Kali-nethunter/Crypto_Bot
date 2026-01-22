"""
सभी फ़ोल्डर और सबफ़ोल्डर से रणनीतियाँ लोड करने के लिए यूटिलिटी
"""

import json
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional

class StrategyLoader:
    def __init__(self):
        self.strategies = {}
    
    def load_strategy(self, strategy_path: Path) -> Optional[Dict[str, Any]]:
        """
        एक रणनीति फ़ोल्डर लोड करें
        
        Args:
            strategy_path: रणनीति फ़ोल्डर का पाथ
            
        Returns:
            रणनीति का डेटा या None
        """
        try:
            # कॉन्फ़िग फ़ाइल चेक करें
            config_file = strategy_path / "config.json"
            if not config_file.exists():
                return None
            
            # स्ट्रैटेजी फ़ाइल चेक करें
            strategy_file = strategy_path / "strategy_logic.py"
            if not strategy_file.exists():
                return None
            
            # कॉन्फ़िग लोड करें
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # स्ट्रैटेजी मॉड्यूल लोड करें
            strategy_module = self.load_module_from_file(
                strategy_file, 
                strategy_path.name
            )
            
            return {
                'name': strategy_path.name,
                'path': str(strategy_path),
                'config': config,
                'module': strategy_module
            }
            
        except Exception as e:
            print(f"रणनीति लोड करने में त्रुटि {strategy_path}: {str(e)}")
            return None
    
    def load_module_from_file(self, file_path: Path, module_name: str):
        """
        फ़ाइल से Python मॉड्यूल लोड करें
        
        Args:
            file_path: पाइथन फ़ाइल का पाथ
            module_name: मॉड्यूल का नाम
            
        Returns:
            लोड किया गया मॉड्यूल
        """
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    def load_all_strategies_recursive(self, base_path: Path) -> Dict[str, Dict]:
        """
        रिकर्सिवली सभी रणनीतियाँ लोड करें
        
        Args:
            base_path: बेस फ़ोल्डर पाथ
            
        Returns:
            सभी रणनीतियों का डिक्शनरी
        """
        strategies = {}
        
        for item in base_path.iterdir():
            if item.is_dir():
                # सबफ़ोल्डर में रिकर्सिवली सर्च करें
                sub_strategies = self.load_all_strategies_recursive(item)
                strategies.update(sub_strategies)
                
                # करंट फ़ोल्डर में रणनीति लोड करें
                strategy = self.load_strategy(item)
                if strategy:
                    strategies[strategy['name']] = strategy
        
        return strategies
