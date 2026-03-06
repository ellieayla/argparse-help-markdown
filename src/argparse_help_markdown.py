from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, Iterable
from unittest.mock import patch

if TYPE_CHECKING:
    from io import TextIOWrapper


class DummyLoader:
    # See coveragepy, pep302
    def __init__(self, fullname: str, *_args: Any) -> None:
        self.fullname = fullname


def pre_tag(s: str) -> str:
    """Wrap strings in <pre> tags."""
    return f"<pre>{s}</pre>"


def wrap_in_backticks(s: str) -> str:
    """Wrap `strings` in backticks."""
    return f"`{s}`"


def escape_pipe(s: str) -> str:
    """Escape | characters."""
    return s.replace("|", r"\|")


class MarkdownFormatter(argparse.HelpFormatter):
    """
    ArgumentParser.format_help() calls the public api of HelpFormatter:

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        # description
        formatter.add_text(self.description)

        # positionals, optionals and user-defined groups
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        # epilog
        formatter.add_text(self.epilog)

        # determine help from format above
        return formatter.format_help()

    Normally HelpFormatter creates a list of callback functions to produce help text,
    but how is *not* part of the public api. We can do whatever we want,
    as long as format_help() returns a string.
    """

    prog: str
    items: list[tuple[Callable[..., str], Iterable[Any]]]
    in_table: bool = False

    def __init__(self, prog: str, *_args: Iterable[Any]) -> None:
        """Sneak away the prog name, ignore other arguments."""
        # may need to deal with args/kwargs?
        self.prog = prog
        self.items = []

    def _set_color(self, color: bool) -> None:  # noqa: ARG002, FBT001
        """Compatability: Called directly by ArgumentParser._get_formatter(). Make it a no-op."""
        return

    def ensure_header(self) -> str:
        if not self.in_table:
            self.in_table = True
            return (
                "| Options | Values  | Help |\n"
                "| ------- | ------- | ---- |\n"
            )  # fmt: skip
        return ""  # pragma: no cover

    def _add_item(self, func: Callable[[Any], str], args: Iterable[Any]) -> None:
        self.items.append((func, args))

    def arguments_column(self, action: argparse.Action) -> str:
        default = action.dest
        if action.option_strings:
            return pre_tag(" ".join(action.option_strings))
        return pre_tag(default)

    def _format_action(self, action: argparse.Action) -> str:
        if action.type and isinstance(action.type, type):
            typename = action.type.__name__
        else:
            typename = "Unknown"

        # 1
        column_one = self.arguments_column(action)

        # 2
        column_two_parts: list[str] = []

        if (
            action.const is None  # fmt: skip
            and action.required
            and action.nargs != 0
        ):
            column_two_parts.append(action.dest.upper())

        if action.nargs == 0:
            column_two_parts.append("Flag.")
        elif action.required:
            column_two_parts.append("Required.")
        elif not action.default or action.default is argparse.SUPPRESS:
            column_two_parts.append("Optional.")

        if action.type is not None:
            column_two_parts.append(f"Type: {typename}")
        if action.choices:
            column_two_parts.append(f"Choice: {', '.join([wrap_in_backticks(x) for x in action.choices])}")
        if action.default and action.default is not argparse.SUPPRESS and action.const is None:
            column_two_parts.append(f"Default: {wrap_in_backticks(action.default)}")

        # 3
        if action.help and action.help.strip():
            column_three = action.help.strip()
        else:
            column_three = ""  # no help
        return f"| {column_one} | {'<br/>'.join(column_two_parts)} | {column_three} |\n"

        # TODO:
        # if there are any sub-actions, add their help as well
        # for subaction in self._iter_indented_subactions(action):
        #    parts.append(self._format_action(subaction))

    def add_argument(self, action: argparse.Action) -> None:
        if action.help is not argparse.SUPPRESS:
            self._add_item(self._format_action, [action])

    def add_arguments(self, actions: Iterable[argparse.Action]) -> None:
        for action in actions:
            self.add_argument(action)

    def _format_text(self, text: str) -> str:
        return f"| {escape_pipe(text)} | |\n"

    def add_text(self, text: str | None) -> None:
        if text:
            self._add_item(self._format_text, [text])

    def add_usage(
        self,
        usage: str | None,
        actions: Iterable[argparse.Action],
        groups: Iterable[Any],
        prefix: str | None = None,
    ) -> None:
        """No implementation; usage doesn't go in the table. Just ignore the arguments."""

    def _format_heading(self, text: str) -> str:
        return f"| *{escape_pipe(text)}* | |\n"

    def start_section(self, heading: str | None) -> None:
        if heading:
            self._add_item(self._format_heading, [heading])

    def end_section(self) -> None:
        return

    def _join_parts(self, part_strings: Iterable[str]) -> str:
        return "".join([part for part in part_strings if part and part is not argparse.SUPPRESS])

    def format_help(self) -> str:
        """
        The workhorse. Run all the callbacks in self.items and return a giant string,
        similar to argparse.HelpFormatter._Section.format_help()
        """

        item_help = self._join_parts(
            [func(*args) for func, args in self.items],
        )
        return self.ensure_header() + item_help


class ParseArgsNotCalledError(Exception):
    """Failure - parse_args() was never called."""


class FinishedGettingOutput(Exception):  # noqa: N818
    """Success 'exception' used to escape from inside argparse."""


def main() -> int:
    """
    Parse CLI arguments, open an output file if needed, and run against a script.

    TODO: Support modules.
    """
    p = argparse.ArgumentParser(usage="%(prog)s script.py -- --help")
    p.add_argument("--usage", action="store_true", help="Emit the terse usage info in triple-ticks. Excluded by default.")
    p.add_argument("--write", metavar="out.md", help="Write to a file instead of stdout.")
    p.add_argument("filename", metavar="script.py", help="Path to the subject script.")

    options, leftovers = p.parse_known_args()

    try:
        if options.write:
            with Path.open(options.write, mode="w") as fh:
                run(filename=options.filename, leftovers=leftovers, include_usage=options.usage, writer=fh)
                return 0
        else:
            run(filename=options.filename, leftovers=leftovers, include_usage=options.usage, writer=None)
            return 0
    except ParseArgsNotCalledError:
        p.error("Subject script never called parse_args(). You might need to pass additional arguments or environment variables.")


def run(*, filename: str, leftovers: list[str], include_usage: bool, writer: TextIOWrapper | None = None) -> None:
    """
    Read source from filename, construct a __main__ module for it, patch argparse, and exec() the source.

    Inspired by approach in coverage.py
    """
    # inspired by coveragepy
    py_source = Path(filename).read_text()

    py_code = compile(py_source, filename=filename, mode="exec", dont_inherit=True)

    main_mod = ModuleType("__main__")
    main_mod.__file__ = filename
    main_mod.__loader__ = DummyLoader("__main__")  # type: ignore[assignment]
    main_mod.__builtins__ = sys.modules["builtins"]  # type: ignore[attr-defined]

    sys.modules["__main__"] = main_mod

    # part of the public api in >=3.14, ignored earlier
    os.environ["NO_COLOR"] = "1"

    # shove the arguments into sys.argv so the subject's ArgumentParser can pull them back out
    sys.argv = [filename, *leftovers]

    def print_help_cb(
        parser: argparse.ArgumentParser,
        args: list[str] | None = None,  # noqa: ARG001 - unused argument
        namespace: argparse.Namespace | None = None,  # noqa: ARG001 - unused argument
    ) -> None:
        """Format and print the help instead."""
        if include_usage:
            usage_text = parser.format_usage()
            print(f"```\n{usage_text.strip()}\n```\n", file=writer)

        with patch.multiple(
            parser,  # instance
            formatter_class=MarkdownFormatter,
            description=None,
            epilog=None,
        ):
            parser.print_help(file=writer)
        raise FinishedGettingOutput  # success

    # Force the help to be printed as soon as parser.parse_args() is called,
    # regardless of whether --help or any other argument was passed.
    with patch.multiple(
        argparse.ArgumentParser,  # not instantiated yet
        parse_args=print_help_cb,
        parse_known_args=print_help_cb,
        parse_intermixed_args=print_help_cb,
        parse_known_intermixed_args=print_help_cb,
    ):
        try:
            exec(py_code, main_mod.__dict__)  # noqa: S102 = exec
            raise ParseArgsNotCalledError  # failure
        except FinishedGettingOutput:
            return  # success


if __name__ == "__main__":
    raise SystemExit(main())  # pragma: no cover
