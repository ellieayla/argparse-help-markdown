from pathlib import Path

import pytest

from argparse_help_markdown import ParseArgsNotCalledError, run

FIXTURE_DIR = Path(__file__).parent.resolve() / "data"


@pytest.mark.datafiles(FIXTURE_DIR / "example.py")
def test_run_simple(datafiles: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert datafiles.is_dir()

    subject: Path = datafiles / "example.py"

    run(filename=str(subject.absolute()), include_usage=False, writer=None)

    captured = capsys.readouterr()

    assert r"<pre>positional\_required</pre>" in captured.out
    for line in captured.out.splitlines():
        assert line[0] == "|"


@pytest.mark.datafiles(FIXTURE_DIR / "no_argparse.py")
def test_script_with_no_argparse_raises_exception(datafiles: Path) -> None:
    subject: Path = datafiles / "no_argparse.py"

    with pytest.raises(ParseArgsNotCalledError):
        run(filename=str(subject.absolute()), include_usage=False, writer=None)


@pytest.mark.datafiles(FIXTURE_DIR / "example.py")
def test_write_markdown_file(datafiles: Path) -> None:
    subject: Path = datafiles / "example.py"
    output: Path = datafiles / "output.md"

    assert not output.exists()

    with Path.open(output, "w") as fh:
        run(filename=str(subject.absolute()), include_usage=False, writer=fh)

    content = output.read_text()
    assert "A required integer option" in content


@pytest.mark.datafiles(FIXTURE_DIR / "example.py")
def test_usage(datafiles: Path, capsys: pytest.CaptureFixture[str]) -> None:
    subject: Path = datafiles / "example.py"

    run(filename=str(subject.absolute()), include_usage=True)

    captured = capsys.readouterr()

    assert captured.err == ""

    assert "usage: Example [-h]" in captured.out


@pytest.mark.datafiles(FIXTURE_DIR / "example.py")
def test_no_usage(datafiles: Path, capsys: pytest.CaptureFixture[str]) -> None:
    subject: Path = datafiles / "example.py"

    run(filename=str(subject.absolute()), include_usage=False)

    captured = capsys.readouterr()

    assert captured.err == ""

    assert "usage: Example [-h]" not in captured.out
