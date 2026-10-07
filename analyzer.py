from collections import deque
from config import PAIRS, SHORT_WINDOW, LONG_WINDOW

class S3Analyzer:
    def __init__(self):
        # Initialize price history and signal tracking for each pair
        self.price_history = {pair: deque(maxlen=LONG_WINDOW) for pair in PAIRS}
        self.last_signal = {pair: None for pair in PAIRS}

    def analyze(self, pair: str, price: float) -> str | None:
        """
        S3 Strategy: Simple Moving Average Crossover.
        Returns 'CALL', 'PUT', or None.
        """
        history = self.price_history[pair]
        history.append(price)

        if len(history) < LONG_WINDOW:
            return None  # Not enough data yet

        # Calculate Moving Averages
        short_ma = sum(list(history)[-SHORT_WINDOW:]) / SHORT_WINDOW
        long_ma = sum(history) / LONG_WINDOW

        prev_short = sum(list(history)[-SHORT_WINDOW-1:-1]) / SHORT_WINDOW if len(history) > SHORT_WINDOW else short_ma
        prev_long = sum(list(history)[-LONG_WINDOW-1:-1]) / LONG_WINDOW if len(history) > LONG_WINDOW else long_ma

        # Detect crossover
        if prev_short <= prev_long and short_ma > long_ma:
            return "CALL"
        elif prev_short >= prev_long and short_ma < long_ma:
            return "PUT"
        return None
