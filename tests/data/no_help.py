from argparse import ArgumentParser


def main() -> None:
    p = ArgumentParser(prog="Example")
    p.add_argument("positional")

    _ = p.parse_args()
    raise ValueError("Should never reach here.")  # pragma: no cover


if __name__ == "__main__":
    main()
