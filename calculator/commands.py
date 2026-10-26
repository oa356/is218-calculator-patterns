from calculator.calculation import Calculation


class CalculateCommand:
    def __init__(self, calculation: Calculation, history: list[str],
                 label: str = "calculation"):
        # Receive the calculation and shared history instead of building them.
        self.calculation = calculation
        self._history = history
        self.label = label

    def execute(self) -> float:
        result = self.calculation.execute()
        # Record only after execution succeeds; an error leaves history alone.
        self._history.append(f"{self.label} = {result}")
        return result


class HistoryCommand:
    def __init__(self, history: list[str]):
        self._history = history

    def execute(self) -> list[str]:
        # A copy prevents callers from editing the stored list through the result.
        return self._history.copy()
