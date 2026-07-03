from pathlib import Path

import pytest

from argparse_help_markdown import run

FIXTURE_DIR = Path(__file__).parent.resolve() / "data"


@pytest.mark.datafiles(FIXTURE_DIR / "help_param_expansion.py")
def test_param_expansion_enum(datafiles: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert datafiles.is_dir()

    subject: Path = datafiles / "help_param_expansion.py"

    run(filename=str(subject.absolute()), include_usage=False, writer=None)

    captured = capsys.readouterr()

    assert r"One of a\_a, b\|b." in captured.out
    assert r"Def\; c/c" in captured.out
