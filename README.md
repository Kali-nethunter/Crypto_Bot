Installation and Usage Guide

Installation Steps:

1. Python 3.8+ इंस्टॉल करें
2. रिक्वायरमेंट्स इंस्टॉल करें:

```bash
pip install -r requirements.txt
```

1. Setup the configuration files:

```bash
mkdir -p config/exchanges strategies utils
```

2. Put your API keys in the config files

Run the bot:

```bash
python main.py
```

Safety Precautions--

1. API Keys Security:
   · Do not put API keys directly in the code
   · Use .env file or encrypted storage
   · Keep withdraw permissions disabled on the exchange
2. Use Testnet:
   · First test on Binance Testnet
   · Perform paper trading before using real funds
3. Risk Management:
   · Set stop-loss for each trade
   · Do not risk more than 1-2% of the portfolio
   · Take regular backups
4. Monitoring:
   · Check logs regularly
   · Monitor balance and open orders
