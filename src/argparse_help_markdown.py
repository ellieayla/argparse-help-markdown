#!/usr/bin/env python

from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import os
import sys
from collections.abc import Callable, Generator, Iterable
from contextlib import contextmanager
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import CodeType, ModuleType
from typing import TYPE_CHECKING, Any
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


class NoSourceError(ValueError):
    """Unable to find/load the source for the given module/script"""


@contextmanager
def open_file_for_writing_or_none(write_filename: str | None) -> Generator[TextIOWrapper | None, None, None]:
    """If a write_filename was passed, open it for writing. Otherwise use stdout."""
    if write_filename is not None:
        with open(file=write_filename, mode="w") as fh:
            yield fh
    else:
        yield None


def main() -> int:
    """
    Parse CLI arguments, open an output file if needed, and run against a script.

    TODO: Support modules.
    """
    p = argparse.ArgumentParser(usage="%(prog)s script.py")
    p.add_argument("--usage", action="store_true", help="Emit the terse usage info in triple-ticks. Excluded by default.")
    p.add_argument("--write", metavar="out.md", help="Write to named file instead of stdout.")

    subject_group = p.add_mutually_exclusive_group(required=True)
    subject_group.add_argument("-m", "--module", help="Run as module.")
    subject_group.add_argument("filename", nargs="?", metavar="script.py", help="Path to the subject script.")

    options = p.parse_args()

    try:
        with open_file_for_writing_or_none(options.write) as fh:
            run(
                filename=(options.module if options.module else options.filename),
                include_usage=options.usage,
                writer=fh,
                as_module=(options.module is not None),
            )
            return 0
    except ParseArgsNotCalledError:
        p.error("Subject script never called parse_args(). You might need to pass additional arguments or environment variables.")


def find_module(module_name: str) -> tuple[str | None, str, ModuleSpec]:
    try:
        spec = importlib.util.find_spec(module_name)
    except ImportError:  # pragma: no cover
        raise NoSourceError(module_name)
    if not spec:
        raise NoSourceError(module_name)

    path_name = spec.origin
    package_name = spec.name
    if spec.submodule_search_locations:
        # module_name is actually a package.
        # Look inside the package for a __main__.py, and make a spec for that module.
        mod_main = module_name + ".__main__"
        spec = importlib.util.find_spec(mod_main)
        if not spec:
            raise NoSourceError(f"Is a package and cannot be directly executed (no {mod_main} module)")

        path_name = spec.origin
        package_name = spec.name

    package_name = package_name.rpartition(".")[0]
    return path_name, package_name, spec


class Loader:
    """inspired by coveragepy"""

    filename_or_module: str
    as_module: bool = False

    spec: ModuleSpec | None = None
    package: str | None = None
    loader: DummyLoader

    def __init__(self, filename_or_module: str, as_module: bool):
        self.filename_or_module = filename_or_module
        self.as_module = as_module

    def prepare_sys_path(self) -> None:
        """Set sys.path properly so the first element is appropriate from the perspective of filename_or_module."""

        path0: str | None

        if getattr(sys.flags, "safe_path", False):  # -P  # pragma: no cover
            path0 = None
        elif self.as_module:
            path0 = os.getcwd()
        elif os.path.isdir(self.filename_or_module):
            # if passed a directory, we really want the __main__.py file inside it, and set the path to the container
            path0 = self.filename_or_module
        else:
            path0 = os.path.abspath(os.path.dirname(self.filename_or_module))

        if path0 is not None:
            sys.path[0] = os.path.abspath(path0)

    def generate_spec(self) -> None:
        """
        Resolve the context (eg, a package) for the code to run.
        """
        if self.as_module:
            """python -m modulename"""
            self.module_name = self.filename_or_module
            path_name, self.package, self.spec = find_module(self.module_name)
            if self.spec is not None:
                self.module_name = self.spec.name
            self.loader = DummyLoader(self.module_name)
            if path_name is None:  # pragma: no cover
                raise NoSourceError("path_name is None")
            self.path_name = os.path.abspath(path_name)
            self.filename_or_module = self.path_name

        elif os.path.isdir(self.filename_or_module):
            """python modulename/"""
            for ext in (".py",):  # don't support pyc/pyo
                try_filename = os.path.abspath(os.path.join(self.filename_or_module, f"__main__{ext}"))
                if os.path.exists(try_filename):
                    self.filename_or_module = try_filename
                    break
            else:
                raise NoSourceError(f"Can't find __main__ module in {self.filename_or_module}")

            self.spec = importlib.machinery.ModuleSpec(
                name="__main__",
                loader=None,
                origin=try_filename,
            )
            self.spec.has_location = True
            self.package = ""
            self.path_name = try_filename
            self.loader = DummyLoader("__main__")
        else:
            self.path_name = self.filename_or_module
            self.spec = None
            self.loader = DummyLoader("__main__")

    def load_main_code(self) -> tuple[CodeType, ModuleType]:
        filename: str = self.path_name
        py_source = Path(filename).read_text()

        py_code = compile(py_source, filename=filename, mode="exec", dont_inherit=True)

        main_mod = ModuleType("__main__")
        main_mod.__file__ = filename
        main_mod.__loader__ = DummyLoader("__main__")  # type: ignore[assignment]
        main_mod.__builtins__ = sys.modules["builtins"]  # type: ignore[attr-defined]

        if self.package is not None:
            main_mod.__package__ = self.package

        return py_code, main_mod


def run_script(filename: str, include_usage: bool = False, cwd: Path | str | None = None) -> None:
    """Public API, helpful for calling from cog"""
    if cwd:
        os.chdir(cwd)
    run(filename=filename, as_module=False, include_usage=include_usage, writer=None)


def run_module(modulename: str, include_usage: bool = False, cwd: Path | str | None = None) -> None:
    """Public API, helpful for calling from cog"""
    if cwd:
        os.chdir(cwd)
    run(filename=modulename, as_module=True, include_usage=include_usage, writer=None)


def run(*, filename: str, as_module: bool = False, include_usage: bool, writer: TextIOWrapper | None = None) -> None:
    """
    Read source from filename, construct a __main__ module for it, patch argparse, and exec() the source.

    Inspired by approach in coverage.py
    """
    r = Loader(filename, as_module=as_module)
    r.prepare_sys_path()
    r.generate_spec()
    py_code, main_mod = r.load_main_code()

    sys.modules["__main__"] = main_mod

    # argparse prog is based on this name.
    sys.argv = [str(filename)]

    # part of argparse's public api in >=3.14, and ignored earlier
    os.environ["NO_COLOR"] = "1"

    def print_help_cb(
        parser: argparse.ArgumentParser,
        args: list[str] | None = None,  # noqa: ARG001 - unused argument
        namespace: argparse.Namespace | None = None,  # noqa: ARG001 - unused argument
    ) -> None:
        """Format and print the help instead."""
        if include_usage:
            usage_text = parser.format_usage()
            print(f"```\n{usage_text.strip()}\n```\n", file=writer)

        # patch attributes of the parser instance:
        #  formatter_class will get invoked and used to render to stdout/writer
        #  description/epilog=None so they don't mess up the middle of the table
        with patch.multiple(
            parser,
            formatter_class=MarkdownFormatter,
            description=None,
            epilog=None,
        ):
            parser.print_help(file=writer)
        raise FinishedGettingOutput  # success

    # Force the help to be printed as soon as one of the parser.parse_*args() functions is called,
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
