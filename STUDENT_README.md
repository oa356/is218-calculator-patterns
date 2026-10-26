# CLI Calculator

A Python terminal calculator with four operations, successful-calculation history, input validation, and automated tests. Python 3.12 or newer is required.

## Setup

From the repository root:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, use the environment directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run and test

With the environment activated:

```bash
python -m calculator
python -m pytest --cov=calculator --cov-report=term-missing --cov-fail-under=100
```

Without activation on Windows:

```powershell
.\.venv\Scripts\python.exe -m calculator
.\.venv\Scripts\python.exe -m pytest --cov=calculator --cov-report=term-missing --cov-fail-under=100
```

History lasts for the current CLI session. Type `exit` to stop. EOF also stops cleanly: Ctrl+Z then Enter on Windows, or Ctrl+D on macOS/Linux.

## Example conversation

```text
> add 5 3
8.0
> subtract 5 3
2.0
> multiply 5 3
15.0
> divide 6 3
2.0
> add -2.5 1.25
-1.25
> divide 6 0
Error: Cannot divide by zero
> history
add 5 3 = 8.0
subtract 5 3 = 2.0
multiply 5 3 = 15.0
divide 6 3 = 2.0
add -2.5 1.25 = -1.25
> exit
```

The failed division is absent from history. The CLI continues after unknown commands, wrong operand counts, invalid numbers, and division by zero. `history` and `exit` take no operands.

## Static, class, and instance methods

| Method type | Example and explanation |
| --- | --- |
| Static | `Operations.add(a, b)` and the other arithmetic methods use only the supplied numbers. They need neither `self` nor `cls`. |
| Class | `Calculation.create(cls, a, b, operation)` uses `cls` to construct the concrete class that called it. `ArithmeticCalculation` inherits this factory. |
| Instance | `ArithmeticCalculation.execute(self)` uses that object's stored numbers and selected operation. The commands' instance methods coordinate their own supplied objects and history. |

## Factory, Command, and Strategy

| Pattern | Implementation |
| --- | --- |
| Factory | `ArithmeticCalculation.create(a, b, operation)` uses the inherited class factory to build a calculation. It does not choose between subclasses. |
| Command | `CalculateCommand` represents executing one calculation and recording its successful result. `HistoryCommand` represents retrieving a copy of history. Neither command performs terminal input or printing. |
| Strategy | The `operations` dictionary in `cli.main()` maps user-entered names to operation functions. The selected function is supplied to the calculation. |

For `add 5 3`, the CLI reads and validates the words, converts the operands with `float()`, selects `Operations.add`, calls the factory, executes a `CalculateCommand`, and prints its returned answer. The command records the successful history entry after the calculation returns.

The starter's addition example was extended with subtraction, multiplication, and division. Each uses the same calculation and command execution methods; only the selected operation function changes.

## OOP

| Idea | Example in this project |
| --- | --- |
| Encapsulation | `Calculation` groups its operands, selected operation, and execution contract. Commands keep their shared history reference in `_history`, and `HistoryCommand.execute()` returns a separate list so callers cannot append to or remove from the stored list through its return value. |
| Abstraction | The abstract `Calculation` class requires `execute()`. It declares the shared promise while `ArithmeticCalculation` supplies the arithmetic implementation. |
| Inheritance | `ArithmeticCalculation` inherits `__init__()` and `create()` from `Calculation`. It supplies the required `execute()` implementation. |
| Polymorphism | `CalculateCommand` accepts a `Calculation` and calls its `execute()` method. A different concrete calculation can be supplied if it keeps that contract. |
| Composition | A `CalculateCommand` holds a calculation and a shared history list. A calculation holds an operation function. |

## SOLID

| Principle | Example in this project |
| --- | --- |
| Single responsibility | `Operations` performs arithmetic; calculations store inputs and execute a strategy; commands coordinate execution/history; the CLI handles terminal input and output. |
| Open/closed | Add an operation method and register its name in the CLI dictionary. The execution code in `ArithmeticCalculation` and `CalculateCommand` can remain unchanged. |
| Liskov substitution | A replacement `Calculation` implementation must preserve `execute()` behavior: return a numeric answer or raise an appropriate error. Commands can then use it through the same interface. |
| Interface segregation | The required calculation behavior is the small `execute()` contract. Calculations do not have to implement terminal input, printing, or history methods. |
| Dependency inversion | `CalculateCommand` receives a `Calculation` abstraction, and calculations receive an operation callable. They do not hard-code addition or construct their own arithmetic dependencies. |

## Tests and GitHub Actions

Run:

```bash
python -m pytest --cov=calculator --cov-report=term-missing --cov-fail-under=100
```

The tests assert arithmetic results, factory construction and inherited `cls` behavior, rejection of abstract construction, command results, history ordering and copying, failure behavior, CLI errors and recovery, exit, EOF, and the module entry point. Parameterized cases include decimals, negatives, and zero.

The supplied implementation was checked locally on Python 3.12 with 48 passing tests and 100% line coverage across `calculator`. The workflow runs the same test arguments on pushes, pull requests, and manual dispatches.

**Successful GitHub Actions run: (https://github.com/oa356/is218-calculator-patterns/actions/runs/40385621618)**

## Coverage exclusions

Only the abstract `Calculation.execute()` placeholder has `# pragma: no cover`. It declares a required method without implementing behavior. Arithmetic, construction, command execution, history, parsing, and error handling are covered. The `__main__.py` entry point is exercised with `runpy`, so it does not need an exclusion.
