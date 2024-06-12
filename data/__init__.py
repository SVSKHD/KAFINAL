import MetaTrader5 as mt5
import pandas as pd

def initialize_mt5(login, password, server):
    if not mt5.initialize(login=login, password=password, server=server):
        print("initialize() failed, error code =", mt5.last_error())
        quit()

def get_historical_data(symbol, timeframe, n_bars):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n_bars)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def get_live_price(symbol):
    tick = mt5.symbol_info_tick(symbol)
    return tick.bid, tick.ask
