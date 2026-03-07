from pathlib import Path

import pytest

from argparse_help_markdown import ParseArgsNotCalledError, run_module, run_script

FIXTURE_DIR = Path(__file__).parent.resolve() / "data"


def test_run_module_api(datafiles: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    assert datafiles.is_dir()

    (datafiles / "empty.py").touch()

    with pytest.raises(ParseArgsNotCalledError):
        run_module(modulename="empty", cwd=datafiles)


def test_run_script_api(datafiles: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    assert datafiles.is_dir()

    (datafiles / "empty.py").touch()

    with pytest.raises(ParseArgsNotCalledError):
        run_script(filename="empty.py", cwd=datafiles)


def test_dotted_module(datafiles: Path, monkeypatch: pytest.MonkeyPatch) -> None:

    assert datafiles.is_dir()

    (datafiles / "a").mkdir()
    (datafiles / "a" / "b").mkdir()
    (datafiles / "a" / "b" / "mod.py").write_text("c=1")

    with pytest.raises(ParseArgsNotCalledError):
        run_module(modulename="a.b.mod", cwd=datafiles)
