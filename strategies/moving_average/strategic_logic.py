"""
मूविंग एवरेज क्रॉसओवर रणनीति
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

class MovingAverageStrategy:
    def generate_signal(self, ohlcv_data: list, config: Dict[str, Any]) -> str:
        """
        ट्रेडिंग सिग्नल जनरेट करें
        
        Args:
            ohlcv_data: OHLCV डेटा
            config: रणनीति कॉन्फ़िगरेशन
            
        Returns:
            'BUY', 'SELL', या 'HOLD'
        """
        # डेटा को DataFrame में कन्वर्ट करें
        df = pd.DataFrame(
            ohlcv_data, 
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        
        # मूविंग एवरेज कैलकुलेट करें
        fast_period = config.get('fast_period', 10)
        slow_period = config.get('slow_period', 30)
        
        df['fast_ma'] = df['close'].rolling(window=fast_period).mean()
        df['slow_ma'] = df['close'].rolling(window=slow_period).mean()
        
        # करंट वैल्यूज प्राप्त करें
        current_fast_ma = df['fast_ma'].iloc[-1]
        current_slow_ma = df['slow_ma'].iloc[-1]
        previous_fast_ma = df['fast_ma'].iloc[-2]
        previous_slow_ma = df['slow_ma'].iloc[-2]
        
        # सिग्नल जनरेट करें
        if (previous_fast_ma <= previous_slow_ma and 
            current_fast_ma > current_slow_ma):
            return 'BUY'
        elif (previous_fast_ma >= previous_slow_ma and 
              current_fast_ma < current_slow_ma):
            return 'SELL'
        else:
            return 'HOLD'
