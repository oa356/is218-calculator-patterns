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
