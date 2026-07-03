from argparse import ArgumentParser


def main() -> None:
    p = ArgumentParser(prog="default")
    p.add_argument("-c", choices=("a_a", "b|b"), default="c/c", help="One of %(choices)s. Def; %(default)s")

    _ = p.parse_args()
    raise ValueError("Should never reach here.")  # pragma: no cover


if __name__ == "__main__":
    main()
