from argparse import ArgumentParser
from pathlib import Path


def main() -> None:
    p = ArgumentParser(prog="Example", description="Desc", epilog="Epilogue")
    p.add_argument("positional", help="Positional")
    g = p.add_argument_group("group1", description="group1 desc")

    g.add_argument("positional_path", type=Path, help="File location")

    p.add_argument("--option-req", required=True, type=int, help="A required integer option")

    _ = p.parse_args()
    raise ValueError("Should never reach here.")  # pragma: no cover


if __name__ == "__main__":
    main()
