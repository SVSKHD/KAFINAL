# main.py
import time
from data import initialize_mt5
from strategy.main_strategy import main_strategy, execute_trade
from trade_managment.trade import close_losing_trades
import MetaTrader5 as mt5
from datetime import datetime, timedelta

MT5_LOGIN = 212792645
MT5_PASSWORD = 'pn^eNL4U'
MT5_SERVER = 'OctaFX-Demo'

initialize_mt5(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER)

symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSD', 'ETHUSD', 'XAUUSD', 'XAGUSD']

initial_balance = mt5.account_info().balance
daily_profit_target = initial_balance * 1.05  # Example: aiming for a 5% increase


def check_balance():
    account_info = mt5.account_info()
    if account_info is not None:
        return account_info.balance
    else:
        print("Failed to get account info")
        return None


def run_trading_bot():
    global initial_balance, daily_profit_target
    start_time = datetime.now()
    end_time = start_time + timedelta(days=1)

    while datetime.now() < end_time:
        current_balance = check_balance()
        if current_balance >= daily_profit_target:
            print(f"Daily profit target met. Stopping trading for the day. Current balance: {current_balance}")
            break

        # Close losing trades before placing new ones
        close_losing_trades()

        for symbol in symbols:
            decision = main_strategy(symbol)
            execute_trade(symbol, decision, current_balance, daily_profit_target)

        # Delay between each run (1 minute, 60 seconds for high frequency)
        time.sleep(60)

    # Set up for the next day
    initial_balance = check_balance()
    daily_profit_target = initial_balance * 1.05


if __name__ == "__main__":
    run_trading_bot()
