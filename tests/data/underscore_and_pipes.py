from argparse import ArgumentParser


def main() -> None:
    p = ArgumentParser(prog="default", add_help=False)
    p.add_argument("--option|_names", type=str, default="def|_aults", help="help|_text subject line")

    _ = p.parse_args()
    raise ValueError("Should never reach here.")  # pragma: no cover


if __name__ == "__main__":
    main()
