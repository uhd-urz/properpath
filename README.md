# ProperPath

`ProperPath` is a subclass of Python's [`pathlib.Path`](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path)
that offers some additional functionalities. `ProperPath` is written for and used
by [elAPI](https://github.com/uhd-urz/elAPI).

## Usage

`ProperPath` can be used the same way as `pathlib.Path`.

```python

>>> from properpath import ProperPath
>>> p = ProperPath("~/foo")
>>> p
ProperPath(path=/Users/culdesac/foo, actual=~/foo, kind=dir, err_logger=<RootLogger root (WARNING)>)
>>> isinstance(p, pathlib.Path)
True

```

