import sys
from pathlib import Path

import pytest

from argparse_help_markdown import NoSourceError, main

FIXTURE_DIR = Path(__file__).parent.resolve() / "data"


@pytest.mark.datafiles()
def test_module_directory(datafiles: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    assert datafiles.is_dir()

    (datafiles / "directorypackage").mkdir()
    (datafiles / "directorypackage" / "__main__.py").write_text("x=1")

    with monkeypatch.context() as m:
        argv = ["yourself", "-m", "directorypackage"]

        m.chdir(datafiles)
        m.setattr(sys, "argv", argv)
        m.setattr(sys, "path", value=[str(datafiles)])

        with pytest.raises(SystemExit):
            main()

    captured = capsys.readouterr()

    assert "Subject script never called parse_args" in captured.err


@pytest.mark.datafiles()
def test_path_directory(datafiles: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    assert datafiles.is_dir()

    (datafiles / "directorypackage2").mkdir()
    (datafiles / "directorypackage2" / "__main__.py").write_text("x=1")

    with monkeypatch.context() as m:
        argv = ["yourself", "directorypackage2"]

        m.chdir(datafiles)
        m.setattr(sys, "argv", argv)
        m.setattr(sys, "path", value=[str(datafiles)])

        with pytest.raises(SystemExit):
            main()

    captured = capsys.readouterr()

    assert "Subject script never called parse_args" in captured.err


@pytest.mark.datafiles()
def test_file_empty_directory(datafiles: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    assert datafiles.is_dir()

    (datafiles / "directorypackage3").mkdir()

    with monkeypatch.context() as m:
        argv = ["yourself", "directorypackage3"]

        m.chdir(datafiles)
        m.setattr(sys, "argv", argv)
        m.setattr(sys, "path", value=[str(datafiles)])

        with pytest.raises(NoSourceError) as e:
            main()

    assert "Can't find __main__ module in directorypackage3" == e.value.args[0]


@pytest.mark.datafiles()
def test_module_empty_directory(datafiles: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    assert datafiles.is_dir()

    (datafiles / "directorypackage3").mkdir()

    with monkeypatch.context() as m:
        argv = ["yourself", "-m", "directorypackage3"]

        m.chdir(datafiles)
        m.setattr(sys, "argv", argv)
        m.setattr(sys, "path", value=[str(datafiles)])

        with pytest.raises(NoSourceError) as e:
            main()

    assert "Is a package and cannot be directly executed" == e.value.args[0]
