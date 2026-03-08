from pathlib import Path

import pytest

from argparse_help_markdown import ESCAPE_PUNCTUATION_TABLE, run

FIXTURE_DIR = Path(__file__).parent.resolve() / "data"


@pytest.mark.datafiles(FIXTURE_DIR / "underscore_and_pipes.py")
def test_underscores_and_pipes_escaped(datafiles: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert datafiles.is_dir()

    subject: Path = datafiles / "underscore_and_pipes.py"

    run(filename=str(subject.absolute()), include_usage=False, writer=None)

    captured = capsys.readouterr()

    for row in captured.out.splitlines():
        if "subject line" in row:
            option, values, help = (x.strip(" |") for x in row.split(" | "))

            assert option == r"<pre>--option\|\_names</pre>"
            assert values == r"Type: str<br/>Default: `def\|\_aults`"
            assert help == r"help\|\_text subject line"
            break
    else:
        # Fail the test
        raise pytest.fail.Exception(f"Did not find subject line in captured output;\n{captured.out}")  # pragma: no cover


@pytest.mark.datafiles(FIXTURE_DIR / "md_link.py")
def test_link_characters_in_help(datafiles: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert datafiles.is_dir()

    subject: Path = datafiles / "md_link.py"

    run(filename=str(subject.absolute()), include_usage=False, writer=None)

    captured = capsys.readouterr()

    for row in captured.out.splitlines():
        if "subject line" in row:
            option, values, help = (x.strip(" |") for x in row.split(" | "))

            print(option, values, help)
            assert help == r"contains \[markdown\]\(link\) subject line"
            break
    else:
        # Fail the test
        raise pytest.fail.Exception(f"Did not find subject line in captured output;\n{captured.out}")  # pragma: no cover


def test_escape_table() -> None:
    print(ESCAPE_PUNCTUATION_TABLE)

    assert r"a_b|c\d".translate(ESCAPE_PUNCTUATION_TABLE) == r"a\_b\|c\\d"
