# Getting Started

<a href="https://pypi.org/project/properpath"><img alt="Package version" src="https://badge.fury.io/py/properpath.svg/?branch=main" /></a>
<img alt="Static Badge" src="https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14-%230d7dbe">
<a href="https://github.com/uhd-urz/properpath/actions"><img alt="GitHub Action test workflow" src="https://github.com/uhd-urz/properpath/actions/workflows/test.yml/badge.svg"></a>

An opinionated OS-path module for people who take paths too seriously. `ProperPath`, as a subclass of Python's popular [
`pathlib.Path`](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path), is a drop-in replacement with some
extra features. The added features/APIs are mainly aimed at improving developer experience in building CLI
tools/applications. `ProperPath` was originally created for [elAPI](https://github.com/uhd-urz/elAPI).

![properpath on the road](https://heibox.uni-heidelberg.de/f/5f8e95d5a5954d3a88c8/?dl=1#only-light){ height="312" width="670" }
![properpath on the road](https://heibox.uni-heidelberg.de/f/548e9c6a7e6e4c7cbc07/?dl=1#only-dark){ height="312" width="670" }


## Main Features in a Nutshell

1. A drop-in `pathlib.Path` replacement with more descriptive REPL representation
2. Built-in error logging for raised exceptions
3. Simplified APIs for working with files and directories
4. Better [`platformfirs`](https://github.com/tox-dev/platformdirs) integration
5. Validation for file/directory write permission

## Installation

Make sure your Python virtual environment is activated. `properpath` requires Python 3.12 and above. Install
`properpath` with `pip`.

```shell linenums="0"
pip install properpath
```

You can install with `uv` as well.

```shell linenums="0"
uv add properpath
```

## Quickstart

Open a Python REPL and try the following:

```{ .pycon .no-copy title="Python REPL" linenums="0" }
>>> from properpath import ProperPath

>>> ProperPath("~")
ProperPath(path=/Users/username, actual=('~',), kind=dir, exists=True, err_logger=<RootLogger root (WARNING)>)
```

If you already have a script or a project where you've used `from pathlib import Path`, and if you're feeling
adventurous (!), you can try the following:

```python
from properpath import ProperPath as Path
```

Head over to the [Tutorial](tutorial.md) page for more hands-on examples.
