from argparse import ArgumentParser
from enum import StrEnum


class EnumChoice(StrEnum):
    """Requesting something"""

    yes = "yes"
    no = "no"


def main() -> None:
    p = ArgumentParser(prog="Example")
    p.add_argument("--enum", choices=EnumChoice, default=EnumChoice.no, help="c")

    _ = p.parse_args()
    raise ValueError("Should never reach here.")  # pragma: no cover


if __name__ == "__main__":
    main()
