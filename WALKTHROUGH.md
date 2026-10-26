# IS218 CLI Calculator: step-by-step walkthrough

This walkthrough follows the instructor's assignment book at https://github.com/kaw393939/is218-calculator-patterns and its fork/build/submit chapter. Read the `book/` chapters in your fork as you work. Keep the original `README.md` and book chapters.

The example supplied here was tested locally on Python 3.12: **48 tests passed, 100% line coverage**. This is local verification, not a GitHub Actions run on your account. Your own successful Actions run and run URL are still required.

These instructions assume VS Code and Windows PowerShell. The standard activated-environment Python commands also work on macOS/Linux after the appropriate activation command.

## 1. Check Git and Python

Open a terminal and run:

```powershell
git --version
python --version
```

Python must be version 3.12 or newer. If Windows recognizes `py` instead of `python`, check `py -3 --version` and use `py -3 -m venv .venv` when creating the environment. Once the environment is activated, use `python`.

Official installation pages, if needed: https://git-scm.com/downloads and https://www.python.org/downloads/ . Reopen VS Code after installing.

## 2. Fork the instructor's repository

1. Sign into your GitHub account.
2. Open https://github.com/kaw393939/is218-calculator-patterns .
3. Click **Fork**, select your own account, and create the fork.
4. Open your fork. Confirm the name at the top starts with your username.
5. Click **Code**, select HTTPS, and copy your fork's clone URL.

A public fork is easy for your instructor to access. If you use a private repository instead, give the instructor access.

## 3. Clone your fork and open it in VS Code

Replace `YOUR-USERNAME` with your GitHub username:

```powershell
git clone https://github.com/YOUR-USERNAME/is218-calculator-patterns.git
cd is218-calculator-patterns
git remote -v
```

The `origin` URL must point to your account. Open this cloned folder using **VS Code > File > Open Folder**. Use **Terminal > New Terminal**. All following commands run from this folder, the one containing `requirements.txt`.

## 4. Understand the supplied download

The ZIP contains a `calculator-files` folder. It has the instructor's book and starter files, the completed example source, additional tests, this walkthrough, and a draft `STUDENT_README.md`. It contains no `.git` folder or virtual environment.

For the quickest setup, extract the ZIP and copy the **contents** of `calculator-files` into the root of your cloned fork. Merge matching folders and replace matching example files. Your root should directly contain `calculator/`, `tests/`, `book/`, `requirements.txt`, and `STUDENT_README.md`.

Do not create an extra nested `calculator-files` folder inside the repository. Keep your clone's `.git` folder; that is what connects it to your own fork. Only copy into a fresh assignment fork, or compare and merge any work you already wrote.

For a file-by-file build instead, use the full contents shown in steps 6-10 below. Review each file and understand its job before submitting.

## 5. Create the virtual environment and install the test tools

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

For macOS/Linux, activate with `source .venv/bin/activate`.

If PowerShell blocks activation, do not change system permissions. Use the environment directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

In that case, replace the starting `python` in later run/test commands with `.\.venv\Scripts\python.exe`.

Confirm `requirements.txt` contains:

```text
pytest>=8,<10
pytest-cov>=7,<8
```

Keep the starter `.gitignore`, which ignores `.venv/`, `__pycache__/`, `.pytest_cache/`, `.coverage`, and `htmlcov/`.

## 6. Implement the four operations

Open `calculator/operations.py`. Keep addition and add subtraction, multiplication, and division. These are static methods because they use only their two arguments. Division raises the exact requested error for a zero denominator.


**`calculator/operations.py`**

```python
class Operations:
    @staticmethod
    def add(a: float, b: float) -> float:
        # This method uses only a and b. No object state is needed.
        return a + b

    @staticmethod
    def subtract(a: float, b: float) -> float:
        return a - b

    @staticmethod
    def multiply(a: float, b: float) -> float:
        return a * b

    @staticmethod
    def divide(a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
```


## 7. Keep the calculation ABC and inherited factory

The starter already has the correct `calculator/calculation.py`. Keep its method-type comments and `execute()` contract. Call `ArithmeticCalculation.create(...)`, not the abstract class's factory. The following is the complete starter file for comparison.


**`calculator/calculation.py`**

```python
from abc import ABC, abstractmethod
from collections.abc import Callable

class Calculation(ABC):
    def __init__(self, a: float, b: float,
                 operation: Callable[[float, float], float]):
        # Each calculation owns its two numbers and chosen operation.
        self.a = a
        self.b = b
        self.operation = operation

    @classmethod
    def create(cls, a, b, operation):
        # cls is the concrete class that called create().
        # The factory builds a new object of that class.
        return cls(a, b, operation)

    @abstractmethod
    def execute(self) -> float:  # pragma: no cover
        # This is the promise; concrete classes supply the real work.
        # execute() replaces get_result() and returns the answer.
        pass

class ArithmeticCalculation(Calculation):
    def execute(self) -> float:
        # An instance method uses this calculation's stored values.
        return self.operation(self.a, self.b)
```


Keep `calculator/__init__.py` as a package file. A docstring is sufficient; there is no application behavior to add there.

## 8. Add the commands and shared-history behavior

Create `calculator/commands.py`. The optional label produces readable history without requiring the command to parse input or inspect concrete calculation internals. The result is calculated before the history append, so failures cannot create success entries. `HistoryCommand` returns a copy.


**`calculator/commands.py`**

```python
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
```


## 9. Connect the CLI loop and operation strategies

Create `calculator/cli.py`. The shared history list is created once, outside the loop. Validate names and operand counts before lookup/conversion. Catch only the expected `ValueError` and `EOFError` cases. An error must lead back to the prompt.


**`calculator/cli.py`**

```python
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
```


## 10. Add the module entry point

Create `calculator/__main__.py`. This is the file Python starts when you run `python -m calculator`. It only imports and starts the CLI.


**`calculator/__main__.py`**

```python
from calculator.cli import main


if __name__ == "__main__":
    main()
```


## 11. Add meaningful tests

Keep the original `tests/test_starter.py`. Add `tests/test_complete.py` with the contents below. The helper supplies explicit `exit` commands for ordinary conversations; the EOF test raises `EOFError` deliberately. The entry-point test uses `runpy` and checks that startup calls `main()`.


**`tests/test_complete.py`**

```python
import runpy

import pytest

from calculator.calculation import ArithmeticCalculation, Calculation
from calculator.cli import main
from calculator.commands import CalculateCommand, HistoryCommand
from calculator.operations import Operations


@pytest.mark.parametrize("operation,a,b,expected", [
    (Operations.add, 5, 3, 8),
    (Operations.add, -5, 3, -2),
    (Operations.add, 0, 0, 0),
    (Operations.add, 1.5, 2.25, 3.75),
    (Operations.subtract, 5, 3, 2),
    (Operations.subtract, -5, -3, -2),
    (Operations.subtract, 0, 0, 0),
    (Operations.subtract, 2.5, 1.2, 1.3),
    (Operations.multiply, 5, 3, 15),
    (Operations.multiply, -5, 3, -15),
    (Operations.multiply, 0, 5, 0),
    (Operations.multiply, 1.5, 2, 3),
    (Operations.divide, 6, 3, 2),
    (Operations.divide, -6, 3, -2),
    (Operations.divide, 0, 3, 0),
    (Operations.divide, 2.5, 0.5, 5),
])
def test_operations_and_calculations(operation, a, b, expected):
    assert operation(a, b) == pytest.approx(expected)
    calculation = ArithmeticCalculation.create(a, b, operation)
    assert isinstance(calculation, Calculation)
    assert calculation.a == a
    assert calculation.b == b
    assert calculation.operation is operation
    assert calculation.execute() == pytest.approx(expected)


def test_division_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        Operations.divide(6, 0)


def test_factory_uses_calling_class():
    class ChildCalculation(ArithmeticCalculation):
        pass

    calculation = ChildCalculation.create(5, 3, Operations.add)
    assert type(calculation) is ChildCalculation
    assert calculation.execute() == 8


def test_abstract_class_cannot_be_created():
    with pytest.raises(TypeError):
        Calculation(5, 3, Operations.add)
    with pytest.raises(TypeError):
        Calculation.create(5, 3, Operations.add)


def test_commands_and_history_copy():
    history = []
    viewer = HistoryCommand(history)
    assert viewer.execute() == []

    first = ArithmeticCalculation.create(5.0, 3.0, Operations.add)
    second = ArithmeticCalculation.create(6.0, 3.0, Operations.divide)
    assert CalculateCommand(first, history, "add 5 3").execute() == 8
    assert CalculateCommand(second, history, "divide 6 3").execute() == 2

    expected = ["add 5 3 = 8.0", "divide 6 3 = 2.0"]
    assert history == expected
    returned = viewer.execute()
    assert returned == expected
    assert returned is not history
    returned.append("extra")
    returned.pop(0)
    assert viewer.execute() == expected


def test_failed_command_keeps_existing_history():
    history = ["previous success"]
    calculation = ArithmeticCalculation.create(6, 0, Operations.divide)
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        CalculateCommand(calculation, history).execute()
    assert history == ["previous success"]


def run_cli(monkeypatch, capsys, inputs):
    answers = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    main()
    return capsys.readouterr().out.splitlines()


@pytest.mark.parametrize("text,expected", [
    ("add 5 3", "8.0"),
    ("subtract 5 3", "2.0"),
    ("multiply 5 3", "15.0"),
    ("divide 6 3", "2.0"),
    ("add -2.5 1.25", "-1.25"),
    ("multiply 0 4", "0.0"),
])
def test_cli_success(monkeypatch, capsys, text, expected):
    assert run_cli(monkeypatch, capsys, [text, "exit"]) == [expected]


@pytest.mark.parametrize("text,message", [
    ("power 2 3", "Error: unknown command. Use add, subtract, multiply, divide, history, or exit."),
    ("add", "Error: use add <number> <number>."),
    ("add 1", "Error: use add <number> <number>."),
    ("add 1 2 3", "Error: use add <number> <number>."),
    ("add nope 2", "Error: operands must be numbers."),
    ("subtract 2 nope", "Error: operands must be numbers."),
    ("divide 6 0", "Error: Cannot divide by zero"),
    ("history 1", "Error: history takes no operands."),
    ("exit 1", "Error: exit takes no operands."),
])
def test_cli_errors_keep_running(monkeypatch, capsys, text, message):
    lines = run_cli(monkeypatch, capsys, [text, "add 5 3", "exit"])
    assert lines == [message, "8.0"]


def test_cli_history(monkeypatch, capsys):
    lines = run_cli(monkeypatch, capsys, [
        "history", "add 5 3", "divide 6 0", "divide 6 3", "history", "exit"
    ])
    assert lines == [
        "History is empty.",
        "8.0",
        "Error: Cannot divide by zero",
        "2.0",
        "add 5 3 = 8.0",
        "divide 6 3 = 2.0",
    ]


def test_cli_blank_input_and_case(monkeypatch, capsys):
    assert run_cli(monkeypatch, capsys, ["  ", "ADD 5 3", "exit"]) == ["8.0"]


def test_cli_exit(monkeypatch, capsys):
    assert run_cli(monkeypatch, capsys, ["exit"]) == []


def test_cli_eof(monkeypatch, capsys):
    def end_of_input(prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", end_of_input)
    main()
    assert capsys.readouterr().out == ""


def test_module_entry_point(monkeypatch):
    calls = []
    monkeypatch.setattr("calculator.cli.main", lambda: calls.append(True))
    runpy.run_module("calculator", run_name="__main__")
    assert calls == [True]
```


## 12. Run the calculator and inspect its behavior

```powershell
python -m calculator
```

Enter each line separately:

```text
history
add 5 3
subtract 5 3
multiply 5 3
divide 6 3
add -2.5 1.25
divide 6 0
add hello 2
add 1
add 1 2 3
unknown 1 2
history
exit
```

Check that the arithmetic answers are `8.0`, `2.0`, `15.0`, `2.0`, and `-1.25`. The first history is empty. Errors should show useful messages and leave the calculator running. The second history should list exactly the five successful calculations in order and should omit the failures.

Start the calculator again and test EOF: Ctrl+Z then Enter on Windows, or Ctrl+D on macOS/Linux. It should return to the shell without a traceback. History begins fresh in each session, as no database or file storage is required.

## 13. Require 100% line coverage

From the repository root, with the environment activated:

```powershell
python -m pytest --cov=calculator --cov-report=term-missing --cov-fail-under=100
```

Without activation on Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=calculator --cov-report=term-missing --cov-fail-under=100
```

With all supplied tests retained, the reference result is **48 passed** and **TOTAL 100%**. Your test count can change if you add meaningful tests. The requirements are passing assertions and 100% line coverage across `calculator`, not a particular test count.

If a test fails, fix the code or the incorrect expectation. If coverage is below 100%, read the `Missing` column and add tests for the missed behavior. Do not lower the threshold or exclude working application code.

## 14. Finish your STUDENT_README.md

The download includes the draft below. Review it, put the design explanations in your own words, and make sure each statement matches your code. Include setup/run/test commands, sample input/output, the three method types, Factory/Command/Strategy, all five OOP ideas, all five SOLID principles, and the coverage-exclusion explanation.

Only the abstract `Calculation.execute()` placeholder is excluded in this example. The entry point is tested, so it is not excluded.

After Actions passes on your account, replace the all-capital successful-run placeholder with the actual run URL. Local test output does not replace that link.


**`STUDENT_README.md`**

````markdown
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

**Successful GitHub Actions run: PASTE YOUR ACTUAL SUCCESSFUL RUN URL HERE BEFORE SUBMITTING.**

## Coverage exclusions

Only the abstract `Calculation.execute()` placeholder has `# pragma: no cover`. It declares a required method without implementing behavior. Arithmetic, construction, command execution, history, parsing, and error handling are covered. The `__main__.py` entry point is exercised with `runpy`, so it does not need an exclusion.
````

## 15. Keep the test workflow

The starter already provides `.github/workflows/tests.yml`. Keep it. This version includes `workflow_dispatch`, which adds a manual **Run workflow** button. It also runs on pushes and pull requests, uses Python 3.12, and enforces 100% coverage.


**`.github/workflows/tests.yml`**

```yaml
name: Calculator tests

on:
  push:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: '3.12'
      - name: Install test tools
        run: python -m pip install -r requirements.txt
      - name: Run tests and require 100% coverage
        run: python -m pytest --cov=calculator --cov-report=term-missing --cov-fail-under=100
```


## 16. Enable Actions, commit, and push to your own fork

Open your fork's **Actions** tab. If GitHub asks, click the option to enable workflows in this fork. Then return to the project terminal:

```powershell
git status
git add .
git status
git commit -m "Complete calculator operations commands CLI and tests"
git push origin main
```

Check that source, tests, requirements, documentation, and the workflow are staged. The virtual environment and coverage cache must not be staged. If Git asks for your identity, configure your own name and email, then repeat the commit. If sign-in opens in your browser, sign into the account that owns the fork.

## 17. Verify GitHub Actions and add the successful run URL

1. Open your fork on GitHub and select **Actions**.
2. Open the latest **Calculator tests** run for your implementation commit. If needed, use **Run workflow** on `main`.
3. Wait for its green check.
4. Open the **Run tests and require 100% coverage** step and verify passing tests plus `TOTAL 100%`.
5. Copy the run page URL. Its shape is `https://github.com/YOUR-USERNAME/is218-calculator-patterns/actions/runs/RUN_ID`.
6. In `STUDENT_README.md`, replace the successful-run placeholder with that actual URL.
7. Save and push the documentation update:

```powershell
git add STUDENT_README.md
git commit -m "Document successful calculator Actions run"
git push origin main
```

Confirm that this final documentation commit also passes Actions. The README can link to the earlier successful implementation run, while the latest commit's run must also be green. If a run fails, open its failed step, resolve the issue, run tests locally again, and push the fix.

## 18. Submit your own repository URL in Canvas

Open your fork's main **Code** page and copy the repository URL:

```text
https://github.com/YOUR-USERNAME/is218-calculator-patterns
```

Submit that URL in the assignment. It must be your completed repository, not the instructor's repository, your profile, or only an Actions link. Verify the instructor can access it. Your section's Canvas deadline controls submission timing.

Final check:

- Four operations, decimals, negatives, zero, helpful errors, continued input, history, exit, and EOF work.
- Failed calculations never enter history; returned history is a copy.
- Static methods, the ABC, inherited factory, instance execution, strategies, and both commands are present.
- Tests pass with 100% line coverage across the whole application.
- Original book files remain, and `STUDENT_README.md` has your reviewed explanations and actual successful run URL.
- The final pushed commit's Actions run is green.
- Canvas contains your repository URL.
