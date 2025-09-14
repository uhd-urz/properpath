# ProperPath

An opinionated OS-path module for people who take paths too seriously. `ProperPath` is a subclass of Python's [
`pathlib.Path`](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path) that offers some additional
functionalities. `ProperPath` was originally created for [elAPI](https://github.com/uhd-urz/elAPI).

<img height="371" width="624" src="https://heibox.uni-heidelberg.de/f/5f8e95d5a5954d3a88c8/?dl=1" alt="elAPI features in a nutshell" />

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

