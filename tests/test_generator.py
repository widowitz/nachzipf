import sys
import types
from pathlib import Path
import argparse
import subprocess
import platform

# Provide a minimal openai stub so generator can be imported without the package
openai_stub = types.SimpleNamespace(
    api_key=None,
    chat=types.SimpleNamespace(
        completions=types.SimpleNamespace(create=lambda **kwargs: None)
    ),
)
class APIError(Exception):
    pass
class RateLimitError(Exception):
    pass
class AuthenticationError(Exception):
    pass
openai_stub.APIError = APIError
openai_stub.RateLimitError = RateLimitError
openai_stub.AuthenticationError = AuthenticationError

# Provide a minimal dotenv stub as well
dotenv_stub = types.SimpleNamespace(load_dotenv=lambda: None)
sys.modules.setdefault("openai", openai_stub)
sys.modules.setdefault("dotenv", dotenv_stub)

# Ensure the repository root is in the module search path so generator can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import generator

import pytest


def test_parse_args_with_unit(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--unit", "5"])
    args = generator.parse_args()
    assert args.unit == 5


def test_parse_args_without_unit(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog"])
    args = generator.parse_args()
    assert args.unit is None


def test_setup_openai_success(monkeypatch):
    monkeypatch.setenv("OPEN_AI_KEY", "abc123")
    assert generator.setup_openai()
    assert generator.openai.api_key == "abc123"


def test_setup_openai_missing_key(monkeypatch, capsys):
    monkeypatch.delenv("OPEN_AI_KEY", raising=False)
    result = generator.setup_openai()
    captured = capsys.readouterr()
    assert not result
    assert "OPEN_AI_KEY not found" in captured.out


def test_validate_unit_valid():
    assert generator.validate_unit("3") == 3


def test_validate_unit_out_of_range(capsys):
    assert generator.validate_unit("20") is None
    assert "Unit must be between" in capsys.readouterr().out


def test_validate_unit_bad_value(capsys):
    assert generator.validate_unit("abc") is None
    assert "Please enter a valid number" in capsys.readouterr().out


def test_read_file_safely_existing(tmp_path):
    file = tmp_path / "example.txt"
    file.write_text("hello", encoding="utf-8")
    assert generator.read_file_safely(file) == "hello"


def test_read_file_safely_missing(tmp_path, capsys):
    missing = tmp_path / "missing.txt"
    assert generator.read_file_safely(missing) == ""
    assert "Error: File not found" in capsys.readouterr().out


def test_build_context(monkeypatch):
    fake_map = {
        generator.CONFIG.prompt_file: "PROMPT",
        generator.CONFIG.error_file: "ERROR",
        generator.CONFIG.fersterer_file: "CURRICULUM",
        generator.CONFIG.summary_by_unit_file: "BY_UNIT",
        generator.CONFIG.summary_short_file: "SHORT",
        generator.CONFIG.summary_long_file: "LONG",
    }
    monkeypatch.setattr(generator, "read_file_safely", lambda p: fake_map[p])
    context = generator.build_context(5)
    assert "UNIT TO FOCUS ON TODAY: 5" in context
    assert "PROMPT" in context
    assert "ERROR" in context
    assert "CURRICULUM" in context


def test_generate_exercises(monkeypatch):
    class FakeChoice:
        def __init__(self, content):
            self.message = types.SimpleNamespace(content=content)
    class FakeResponse:
        def __init__(self, content):
            self.choices = [FakeChoice(content)]
    captured = {}
    def fake_create(**kwargs):
        captured["kwargs"] = kwargs
        return FakeResponse("RESULT")
    monkeypatch.setattr(generator.openai.chat.completions, "create", fake_create)
    result = generator.generate_exercises("CTX")
    assert result == "RESULT"
    assert captured["kwargs"]["messages"][1]["content"] == "CTX"


def test_save_exercises(tmp_path, monkeypatch):
    monkeypatch.setattr(generator.CONFIG, "output_dir", tmp_path)
    path = generator.save_exercises("CONTENT", 2)
    assert path.parent == tmp_path
    text = path.read_text(encoding="utf-8")
    assert text.startswith("# Englisch Übungen für Marlene")
    assert f"**Unit:** 2" in text


def test_open_file_linux(monkeypatch):
    calls = {}
    def fake_run(cmd, check):
        calls["cmd"] = cmd
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    monkeypatch.setattr(subprocess, "run", fake_run)
    generator.open_file(Path("/tmp/test.txt"))
    assert calls["cmd"] == ["xdg-open", "/tmp/test.txt"]


def test_main_integration(monkeypatch, tmp_path):
    monkeypatch.setenv("OPEN_AI_KEY", "key")
    monkeypatch.setattr(generator, "parse_args", lambda: argparse.Namespace(unit=3))
    monkeypatch.setattr(generator, "build_context", lambda unit: "CTX")
    monkeypatch.setattr(generator, "generate_exercises", lambda ctx: "EXERCISES")
    monkeypatch.setattr(generator, "open_file", lambda path: None)
    monkeypatch.setattr(generator.CONFIG, "output_dir", tmp_path)
    generator.main()
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    assert files[0].read_text(encoding="utf-8").startswith("# Englisch Übungen für Marlene")
