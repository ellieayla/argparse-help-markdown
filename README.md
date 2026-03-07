Pull argparse configuration out of a CLI tool and write it as Markdown.

Great for embedded in a README.md with [cog](https://github.com/nedbat/cog).

## Usage

Possible invocation options:

```sh
# entrypoint command, dotted module
uv tool run argparse-help-markdown -m tests.data.example

# script, script
argparse_help_markdown.py --write.md script.py

# import, function
from argparse_help_markdown import run_script
run_script("mytool.py", include_usage=True)
```

## What it does

It writes this table about itself:

<!-- [[[cog
    import src.argparse_help_markdown as m
    m.run(filename="src/argparse_help_markdown.py", include_usage=True, writer=None)
]]] -->
```
usage: argparse_help_markdown.py script.py
```

| Options | Values  | Help |
| ------- | ------- | ---- |
| *positional arguments* | |
| <pre>filename</pre> | Optional. | Path to the subject script. |
| *options* | |
| <pre>-h --help</pre> | Flag. | show this help message and exit |
| <pre>--usage</pre> | Flag. | Emit the terse usage info in triple-ticks. Excluded by default. |
| <pre>--write</pre> | Optional. | Write to named file instead of stdout. |
| <pre>-m --module</pre> | Optional. | Run as module. |
<!-- [[[end]]] -->


## Installation, or not

This is built as a single-file that can be installed as a package or used standalone. It can be imported as a module or run on the command-line. It's mostly useful inside a documentation CICD pipeline, where flexability is key.

With uv: `uv tool run argparse-help-markdown`

With pipx: `pipx run argparse-help-markdown`

Or install with pip: `pip install argparse-help-markdown`

Or grab a locked version with curl: `curl -O https://raw.githubusercontent.com/ellieayla/argparse-help-markdown/a35c9ea9cd975575adb45a4cbbf3d140adf04269/src/argparse_help_markdown.py; python3 argparse_help_markdown.py`
