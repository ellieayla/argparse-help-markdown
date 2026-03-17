from argparse import ArgumentParser


def main() -> None:
    p = ArgumentParser(prog="default", add_help=False)
    p.add_argument("--option", type=str, default="blah")
    p.add_argument("--num", type=int, default=1)
    p.add_argument("manypos", nargs="*", default=["."])

    _ = p.parse_args()
    raise ValueError("Should never reach here.")  # pragma: no cover


if __name__ == "__main__":
    main()
