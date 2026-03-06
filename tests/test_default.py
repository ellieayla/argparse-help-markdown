from pathlib import Path

import pytest

from argparse_help_markdown import run

FIXTURE_DIR = Path(__file__).parent.resolve() / "data"


@pytest.mark.datafiles(FIXTURE_DIR / "default.py")
def test_choice(datafiles: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert datafiles.is_dir()

    subject: Path = datafiles / "default.py"

    run(filename=str(subject.absolute()), leftovers=[], include_usage=False, writer=None)

    captured = capsys.readouterr()

    assert "Default: `blah`" in captured.out
