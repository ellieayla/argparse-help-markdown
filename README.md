Pull argparse configuration out of a CLI tool and write it as Markdown.

Great for embedded in a README.md with cog.

Possible invocation options:

```sh
# entrypoint command, dotted module
uv run argparse-help-markdown -m tests.data.example

# script, script
argparse_help_markdown.py script.py

# import, function, custom writer
from argparse_help_markdown import run_script
with open("out.md", mode="w") as f:
    run_script("mytool.py", include_usage=True, writer=f)
```

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
