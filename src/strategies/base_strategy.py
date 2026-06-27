import pandas as pd

class BaseStrategy:
    def __init__(self, name = "Base Strategy"):
        self.name = name

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("Every strategy must create its own generate_signals rules")