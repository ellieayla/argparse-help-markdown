import sys
from pathlib import Path

import pytest

from argparse_help_markdown import Loader, NoSourceError, main

FIXTURE_DIR = Path(__file__).parent.resolve() / "data"


@pytest.mark.datafiles(FIXTURE_DIR / "example.py")
def test_loader_internals(datafiles: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    assert datafiles.is_dir()

    assert (datafiles / "example.py").exists()

    with monkeypatch.context() as m:
        argv = ["yourself", "-m", "example"]

        m.chdir(datafiles)
        m.setattr(sys, "argv", argv)
        m.setattr(sys, "path", value=[str(datafiles)])

        r = Loader(filename_or_module="example", as_module=True)
        r.prepare_sys_path()

        r.generate_spec()
        assert Path(r.path_name).exists()

        py_code, main_mod = r.load_main_code()

    # use it
    sys.modules["__main__"] = main_mod

    with pytest.raises(SystemExit) as e:
        exec(py_code, main_mod.__dict__)  # noqa: S102 = exec

    assert 2 == e.value.args[0]

    captured = capsys.readouterr()

    assert "usage: Example " in captured.err


@pytest.mark.datafiles(FIXTURE_DIR / "example.py")
def test_load_module(datafiles: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert datafiles.is_dir()

    assert (datafiles / "example.py").exists()

    output = datafiles / "out.md"
    assert not output.exists()

    with monkeypatch.context() as m:
        argv = ["yourself", "-m", "example", "--write", str(output)]

        m.chdir(datafiles)
        m.setattr(sys, "argv", argv)
        m.setattr(sys, "path", value=[str(datafiles)])

        main()

    written = output.read_text()

    assert " | Flag. | " in written


@pytest.mark.datafiles()
def test_source_not_found_internal(datafiles: Path, monkeypatch: pytest.MonkeyPatch) -> None:

    with monkeypatch.context() as m:
        argv = ["yourself", "-m", "example"]

        m.chdir(datafiles)
        m.setattr(sys, "argv", argv)
        m.setattr(sys, "path", value=[str(datafiles)])

        r = Loader(filename_or_module="notfound", as_module=True)
        r.prepare_sys_path()

        with pytest.raises(NoSourceError):
            r.generate_spec()


@pytest.mark.datafiles()
def test_source_not_found(datafiles: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    assert datafiles.is_dir()

    (datafiles / "empty.py").touch()

    with monkeypatch.context() as m:
        argv = ["yourself", "-m", "notfoundx"]

        m.chdir(datafiles)
        m.setattr(sys, "argv", argv)
        m.setattr(sys, "path", value=[str(datafiles)])

        with pytest.raises(NoSourceError):
            main()
