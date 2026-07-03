from pathlib import Path

import pytest

from argparse_help_markdown import run

FIXTURE_DIR = Path(__file__).parent.resolve() / "data"


@pytest.mark.datafiles(FIXTURE_DIR / "choice_enum.py")
def test_choice_enum(datafiles: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert datafiles.is_dir()

    subject: Path = datafiles / "choice_enum.py"

    run(filename=str(subject.absolute()), include_usage=False, writer=None)

    captured = capsys.readouterr()

    assert "--enum" in captured.out
    assert "Default: `no`" in captured.out
    assert "Choice: `no`, `yes`" in captured.out
