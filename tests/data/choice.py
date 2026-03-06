from argparse import ArgumentParser


def main() -> None:
    p = ArgumentParser(prog="Example", add_help=False)
    p.add_argument("--choice", choices=("a", "b"), help="c")

    _ = p.parse_args()
    raise ValueError("Should never reach here.")  # pragma: no cover


if __name__ == "__main__":
    main()
