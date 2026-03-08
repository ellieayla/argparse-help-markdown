from argparse import ArgumentParser


def main() -> None:
    p = ArgumentParser(prog="default", add_help=False)
    p.add_argument("--opt", type=str, help="contains [markdown](link) subject line")

    _ = p.parse_args()
    raise ValueError("Should never reach here.")  # pragma: no cover


if __name__ == "__main__":
    main()
