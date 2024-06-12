# patterns.py
def detect_double_top(data):
    if len(data) < 3:
        return False
    last_peak = data['high'].iloc[-3]
    second_peak = data['high'].iloc[-1]
    trough = data['low'].iloc[-2]
    return second_peak >= last_peak * 0.99 and trough < last_peak * 0.95

def detect_double_bottom(data):
    if len(data) < 3:
        return False
    last_trough = data['low'].iloc[-3]
    second_trough = data['low'].iloc[-1]
    peak = data['high'].iloc[-2]
    return second_trough <= last_trough * 1.01 and peak > last_trough * 1.05

def detect_engulfing(data):
    if len(data) < 2:
        return False
    current_candle = data.iloc[-1]
    previous_candle = data.iloc[-2]
    is_bullish_engulfing = (current_candle['close'] > current_candle['open']) and \
                           (current_candle['open'] < previous_candle['close']) and \
                           (current_candle['close'] > previous_candle['open'])
    is_bearish_engulfing = (current_candle['close'] < current_candle['open']) and \
                           (current_candle['open'] > previous_candle['close']) and \
                           (current_candle['close'] < previous_candle['open'])
    return is_bullish_engulfing or is_bearish_engulfing

def detect_head_and_shoulders(data):
    if len(data) < 5:
        return False
    left_shoulder = data['high'].iloc[-5]
    head = data['high'].iloc[-3]
    right_shoulder = data['high'].iloc[-1]
    neckline = min(data['low'].iloc[-4], data['low'].iloc[-2])
    return left_shoulder < head > right_shoulder and data['low'].iloc[-4] > neckline and data['low'].iloc[-2] > neckline

def detect_inverse_head_and_shoulders(data):
    if len(data) < 5:
        return False
    left_shoulder = data['low'].iloc[-5]
    head = data['low'].iloc[-3]
    right_shoulder = data['low'].iloc[-1]
    neckline = max(data['high'].iloc[-4], data['high'].iloc[-2])
    return left_shoulder > head < right_shoulder and data['high'].iloc[-4] < neckline and data['high'].iloc[-2] < neckline

def detect_bullish_flag(data):
    if len(data) < 6:
        return False
    flagpole = data['close'].iloc[-6] < data['close'].iloc[-5]
    consolidation = all(data['close'].iloc[-5:-1] > data['close'].iloc[-6])
    breakout = data['close'].iloc[-1] > data['close'].iloc[-2]
    return flagpole and consolidation and breakout

def detect_bearish_flag(data):
    if len(data) < 6:
        return False
    flagpole = data['close'].iloc[-6] > data['close'].iloc[-5]
    consolidation = all(data['close'].iloc[-5:-1] < data['close'].iloc[-6])
    breakout = data['close'].iloc[-1] < data['close'].iloc[-2]
    return flagpole and consolidation and breakout

def detect_ascending_triangle(data):
    if len(data) < 6:
        return False
    lows = data['low'].iloc[-6:]
    highs = data['high'].iloc[-6:]
    try:
        ascending = all(lows[i] >= lows[i-1] for i in range(1, len(lows)))
        flat_top = all(abs(highs[i] - highs[i-1]) < 0.01 for i in range(1, len(highs)))
        return ascending and flat_top
    except KeyError:
        return False

def detect_descending_triangle(data):
    if len(data) < 6:
        return False
    lows = data['low'].iloc[-6:]
    highs = data['high'].iloc[-6:]
    try:
        descending = all(highs[i] <= highs[i-1] for i in range(1, len(highs)))
        flat_bottom = all(abs(lows[i] - lows[i-1]) < 0.01 for i in range(1, len(lows)))
        return descending and flat_bottom
    except KeyError:
        return False

def detect_symmetrical_triangle(data):
    if len(data) < 6:
        return False
    lows = data['low'].iloc[-6:]
    highs = data['high'].iloc[-6:]
    try:
        converging = all(abs(highs[i] - lows[i]) < abs(highs[0] - lows[0]) for i in range(1, len(highs)))
        return converging
    except KeyError:
        return False

def detect_rising_wedge(data):
    if len(data) < 6:
        return False
    lows = data['low'].iloc[-6:]
    highs = data['high'].iloc[-6:]
    try:
        rising = all(lows[i] > lows[i-1] and highs[i] > highs[i-1] for i in range(1, len(lows)))
        converging = all(abs(highs[i] - lows[i]) < abs(highs[0] - lows[0]) for i in range(1, len(highs)))
        return rising and converging
    except KeyError:
        return False

def detect_falling_wedge(data):
    if len(data) < 6:
        return False
    lows = data['low'].iloc[-6:]
    highs = data['high'].iloc[-6:]
    try:
        falling = all(lows[i] < lows[i-1] and highs[i] < highs[i-1] for i in range(1, len(lows)))
        converging = all(abs(highs[i] - lows[i]) < abs(highs[0] - lows[0]) for i in range(1, len(highs)))
        return falling and converging
    except KeyError:
        return False

def detect_cup_and_handle(data):
    if len(data) < 10:
        return False
    try:
        cup = min(data['low'].iloc[-10:-5]) < min(data['low'].iloc[-5:])
        handle = max(data['high'].iloc[-5:]) < max(data['high'].iloc[-10:-5])
        return cup and handle
    except KeyError:
        return False
