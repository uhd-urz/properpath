# Getting Started

<a href="#compatibility">
   <img alt="Static Badge" src="https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14-%230d7dbe">
</a>

An opinionated OS-path module for people who take paths too seriously. `ProperPath`, as a subclass of Python's popular [
`pathlib.Path`](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path), is a drop-in replacement with some
extra features. The added features/APIs are mainly aimed at improving developer experience in building CLI
tools/applications. `ProperPath` was originally created for [elAPI](https://github.com/uhd-urz/elAPI).

<img height="312" width="670" src="https://heibox.uni-heidelberg.de/f/5f8e95d5a5954d3a88c8/?dl=1" alt="properpath on the road" />


## Installation

Make sure your Python virtual environment is activated. `properpath` requires Python 3.12 and above. Install
`properpath` with `pip`.

```shell
pip install properpath
```

You can install with `uv` as well.

```shell
uv add properpath
```

## Quickstart

Open a Python REPL and try the following:

```python
>>> from properpath import ProperPath

>>> ProperPath("~")
ProperPath(path=/Users/username, actual=('~',), kind=dir, exists=True, err_logger=<RootLogger root (WARNING)>)
```

If you already have a script or a project where you've used `from pathlib import Path`, and if you're feeling
adventurous (!), you can try the following:

```python
from properpath import ProperPath as Path
```

Head over to the [Tutorial](tutorial) page for more hands-on examples.
