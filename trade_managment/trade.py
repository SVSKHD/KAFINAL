# trade_management.py
import MetaTrader5 as mt5


# Function to place an order
def order_send(symbol, order_type, volume, price, sl, tp, deviation=10):
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,  # Good till canceled
        "type_filling": mt5.ORDER_FILLING_FOK  # Fill or kill
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order failed: {result.retcode}")
    else:
        print(f"Order successful: {result}")

    return result


# Function to close an order
def close_order(order):
    symbol = order.symbol
    volume = order.volume
    position_id = order.ticket
    price = mt5.symbol_info_tick(symbol).bid if order.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL if order.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
        "position": position_id,
        "price": price,
        "deviation": 10,
        "magic": 234000,
        "comment": "python script close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Close order failed: {result.retcode}")
    else:
        print(f"Close order successful: {result}")

    return result


# Function to get open positions
def get_open_positions():
    positions = mt5.positions_get()
    if positions is None:
        print("No positions found")
        return []
    return positions


# Function to close losing trades
def close_losing_trades():
    positions = get_open_positions()
    for position in positions:
        if position.profit < 0:  # Check if the trade is in loss
            print(f"Closing losing trade: {position.symbol} with profit: {position.profit}")
            close_order(position)
