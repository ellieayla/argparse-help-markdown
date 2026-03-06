Pull argparse configuration out of a CLI tool and write it as Markdown.

Great for embedded in a README.md with cog.



<!-- [[[cog
    import src.argparse_help_markdown as m
    m.run(filename="src/argparse_help_markdown.py", leftovers=[], include_usage=True, writer=None)
]]] -->
```
usage: argparse_help_markdown.py script.py -- --help
```

| Options | Values  | Help |
| ------- | ------- | ---- |
| *positional arguments* | |
| <pre>filename</pre> | FILENAME<br/>Required. | Path to the subject script. |
| *options* | |
| <pre>-h --help</pre> | Flag. | show this help message and exit |
| <pre>--usage</pre> | Flag. | Emit the terse usage info in triple-ticks. Excluded by default. |
| <pre>--write</pre> | Optional. | Write to a file instead of stdout. |
<!-- [[[end]]] -->
