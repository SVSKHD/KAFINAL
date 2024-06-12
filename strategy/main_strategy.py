# strategy/main_strategy.py
import MetaTrader5 as mt5
from data import get_historical_data, get_live_price
from indicators.rsi import calculate_rsi
from indicators.macd import calculate_macd
from models.model_training import train_model, make_prediction
from patterns.patterns import (detect_double_top, detect_double_bottom, detect_engulfing,
                      detect_head_and_shoulders, detect_inverse_head_and_shoulders,
                      detect_bullish_flag, detect_bearish_flag, detect_ascending_triangle,
                      detect_descending_triangle, detect_symmetrical_triangle,
                      detect_rising_wedge, detect_falling_wedge, detect_cup_and_handle)
import pandas as pd
from datetime import datetime, timedelta
from trade_managment.trade import order_send, close_order, get_open_positions, close_losing_trades

# Dictionary to store the last trade information and trade counts
last_trade_info = {}
trade_counts = {}
last_trade_price = {}

# Maximum number of trades allowed per symbol
MAX_TRADES_PER_SYMBOL = 3


def detect_trend(data, threshold=0.02):
    # Calculate percentage change
    data['pct_change'] = data['close'].pct_change()
    mean_change = data['pct_change'].mean()
    if mean_change > threshold:
        return "uptrend"
    elif mean_change < -threshold:
        return "downtrend"
    else:
        return "sideways"


def main_strategy(symbol):
    data = get_historical_data(symbol, mt5.TIMEFRAME_H1, 500)
    data['RSI'] = calculate_rsi(data)
    data['MACD'], data['Signal'] = calculate_macd(data)

    trend = detect_trend(data)

    X = data[['RSI', 'MACD']].dropna()
    y = (data['close'].shift(-1) > data['close']).astype(int)  # Example: label as 1 if next close is higher

    # Align X and y
    X = X.iloc[:-1]  # Remove the last row since it won't have a corresponding y value
    y = y.iloc[X.index]

    model = train_model(X, y)  # Train the model on the historical data
    predictions = make_prediction(model, X.iloc[-1:])  # Make predictions on the latest data point

    prediction = predictions[0]

    pattern = None
    if detect_double_top(data):
        pattern = "Double Top"
    elif detect_double_bottom(data):
        pattern = "Double Bottom"
    elif detect_engulfing(data):
        pattern = "Engulfing"
    elif detect_head_and_shoulders(data):
        pattern = "Head and Shoulders"
    elif detect_inverse_head_and_shoulders(data):
        pattern = "Inverse Head and Shoulders"
    elif detect_bullish_flag(data):
        pattern = "Bullish Flag"
    elif detect_bearish_flag(data):
        pattern = "Bearish Flag"
    elif detect_ascending_triangle(data):
        pattern = "Ascending Triangle"
    elif detect_descending_triangle(data):
        pattern = "Descending Triangle"
    elif detect_symmetrical_triangle(data):
        pattern = "Symmetrical Triangle"
    elif detect_rising_wedge(data):
        pattern = "Rising Wedge"
    elif detect_falling_wedge(data):
        pattern = "Falling Wedge"
    elif detect_cup_and_handle(data):
        pattern = "Cup and Handle"

    live_bid, live_ask = get_live_price(symbol)
    decision = {
        'symbol': symbol,
        'prediction': prediction,
        'pattern': pattern,
        'trend': trend,
        'live_bid': live_bid,
        'live_ask': live_ask,
        'time': datetime.now()
    }

    print(decision)
    return decision


def execute_trade(symbol, decision, current_balance, daily_profit_target):
    entry_price = decision['live_ask'] if decision['prediction'] == 1 else decision['live_bid']
    stop_loss = entry_price * 0.99 if decision['prediction'] == 1 else entry_price * 1.01
    take_profit = entry_price * 1.02 if decision['prediction'] == 1 else entry_price * 0.98

    # Initialize trade count for the symbol if not already done
    if symbol not in trade_counts:
        trade_counts[symbol] = 0

    if trade_counts[symbol] >= MAX_TRADES_PER_SYMBOL:
        print(f"Trade limit reached for {symbol}. No more trades will be placed.")
        return

    cooldown_period = timedelta(hours=1)  # Cooldown period for hourly execution
    last_trade = last_trade_info.get(symbol, {'time': datetime.min, 'direction': None})
    time_since_last_trade = decision['time'] - last_trade['time']

    if time_since_last_trade < cooldown_period:
        print(f"Skipping trade for {symbol} due to cooldown period.")
        return

    if last_trade['direction'] is not None and last_trade['direction'] != decision['prediction']:
        print(f"Skipping trade for {symbol} to avoid rapid direction change.")
        return

    if decision['pattern']:
        print(f"{decision['pattern']} detected for {symbol}")

    if symbol in last_trade_price and last_trade_price[symbol] == entry_price:
        print(f"Skipping trade for {symbol} at the same price to avoid cross trades.")
        return

    last_trade_info[symbol] = {
        'time': decision['time'],
        'direction': decision['prediction']
    }

    if current_balance >= daily_profit_target:
        print(f"Daily profit target met. No further trades for {symbol}. Current balance: {current_balance}")
        return

    # Use pattern to adjust the trade volume or stop-loss/take-profit
    if decision['pattern'] == "Double Top":
        stop_loss = entry_price * 1.02  # Example: wider stop-loss for double top
    elif decision['pattern'] == "Double Bottom":
        stop_loss = entry_price * 0.98  # Example: tighter stop-loss for double bottom

    if decision['prediction'] == 1:
        print(f"Placing a BUY order for {symbol} at {entry_price} with SL: {stop_loss} and TP: {take_profit}")
        result = order_send(symbol, mt5.ORDER_TYPE_BUY, 0.1, entry_price, stop_loss, take_profit)
    elif decision['prediction'] == 0:
        print(f"Placing a SELL order for {symbol} at {entry_price} with SL: {stop_loss} and TP: {take_profit}")
        result = order_send(symbol, mt5.ORDER_TYPE_SELL, 0.1, entry_price, stop_loss, take_profit)

    # Increment trade count only if the order was successful
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        trade_counts[symbol] += 1
        last_trade_price[symbol] = entry_price
