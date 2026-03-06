import sys
from pathlib import Path

import pytest

from argparse_help_markdown import main

FIXTURE_DIR = Path(__file__).parent.resolve() / "data"


@pytest.mark.datafiles(FIXTURE_DIR / "no_help.py")
def test_main_entrypoint(datafiles: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    assert datafiles.is_dir()

    subject: Path = datafiles / "no_help.py"

    with monkeypatch.context() as m:
        argv = ["yourself", str(subject.absolute())]
        m.setattr(sys, "argv", argv)
        main()

    captured = capsys.readouterr()

    assert "Required. |  |" in captured.out


@pytest.mark.datafiles(FIXTURE_DIR / "no_help.py")
def test_write_file(datafiles: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    assert datafiles.is_dir()

    subject: Path = datafiles / "no_help.py"
    output: Path = datafiles / "output.md"

    assert not output.exists()

    with monkeypatch.context() as m:
        argv = ["yourself", "--write", str(output.absolute()), str(subject.absolute())]
        m.setattr(sys, "argv", argv)
        main()

    captured = capsys.readouterr()

    assert captured.out == ""

    assert "positional arguments" in output.read_text()


@pytest.mark.datafiles(FIXTURE_DIR / "no_argparse.py")
def test_error_printed_on_fallthrough(datafiles: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    assert datafiles.is_dir()

    subject: Path = datafiles / "no_argparse.py"

    with monkeypatch.context() as m:
        argv = ["yourself", str(subject.absolute())]
        m.setattr(sys, "argv", argv)

        with pytest.raises(SystemExit):
            main()

    captured = capsys.readouterr()

    assert captured.out == ""
    assert "Subject script never called parse_args" in captured.err
