from calculator.calculation import ArithmeticCalculation
from calculator.commands import CalculateCommand, HistoryCommand
from calculator.operations import Operations


def main():
    history = []
    operations = {
        "add": Operations.add,
        "subtract": Operations.subtract,
        "multiply": Operations.multiply,
        "divide": Operations.divide,
    }

    while True:
        try:
            words = input("> ").split()
        except EOFError:
            break

        if not words:
            continue

        name = words[0].lower()

        if name in ("exit", "history"):
            if len(words) != 1:
                print(f"Error: {name} takes no operands.")
                continue
            if name == "exit":
                break
            entries = HistoryCommand(history).execute()
            if entries:
                for entry in entries:
                    print(entry)
            else:
                print("History is empty.")
            continue

        if name not in operations:
            print("Error: unknown command. Use add, subtract, multiply, divide, history, or exit.")
            continue

        if len(words) != 3:
            print(f"Error: use {name} <number> <number>.")
            continue

        try:
            a, b = float(words[1]), float(words[2])
        except ValueError:
            print("Error: operands must be numbers.")
            continue

        try:
            # Input -> operation strategy -> factory -> command -> printed result.
            operation = operations[name]
            calculation = ArithmeticCalculation.create(a, b, operation)
            command = CalculateCommand(calculation, history, " ".join(words))
            result = command.execute()
        except ValueError as error:
            print(f"Error: {error}")
            continue

        print(result)
