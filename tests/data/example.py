from argparse import ArgumentParser
from pathlib import Path


def main() -> None:
    p = ArgumentParser(prog="Example", description="Desc", epilog="Epilogue")
    p.add_argument("positional", help="Positional")
    p.add_argument("positional_path", type=Path, help="File location")
    p.add_argument("positional_required", help="Required positional")
    p.add_argument("--option", action="store_true", help="a flag")
    p.add_argument("--option-path", type=Path, help="a path")
    p.add_argument("--option-req", required=True, type=int, help="A required integer option")

    _ = p.parse_args()
    raise ValueError("Should never reach here.")  # pragma: no cover


if __name__ == "__main__":
    main()
