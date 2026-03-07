from pathlib import Path

import pytest

from argparse_help_markdown import run

FIXTURE_DIR = Path(__file__).parent.resolve() / "data"


@pytest.mark.datafiles(FIXTURE_DIR / "choice.py")
def test_choice(datafiles: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert datafiles.is_dir()

    subject: Path = datafiles / "choice.py"

    run(filename=str(subject.absolute()), include_usage=False, writer=None)

    captured = capsys.readouterr()

    assert "--choice" in captured.out
    assert "Optional." in captured.out
    assert "Choice: `a`, `b`" in captured.out
