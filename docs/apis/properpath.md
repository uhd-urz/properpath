# `ProperPath`

::: properpath

### Other `pathlib.Path` methods and attributes

As a subclass of `pathlib.Path`, a `properpath` instance supports all other [
`pathlib.Path` methods and attributes](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path) that
are not listed here.

## `P`

`P` is an alias for `ProperPath`. `P` is the preferred way to import `ProperPath` as it is much shorter and easier to
type.

```python
from properpath import P, ProperPath

assert P == ProperPath
```
