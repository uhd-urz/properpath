# ProperPath

<a href="#compatibility">
   <img alt="Static Badge" src="https://img.shields.io/badge/python-3.13-%230d7dbe">
</a>

An opinionated OS-path module for people who take paths too seriously. `ProperPath` is a subclass of Python's popular [
`pathlib.Path`](https://docs.python.org/3.12/library/pathlib.html#pathlib.Path) that offers some additional
features for convenience in building CLI applications. `ProperPath` was originally created
for [elAPI](https://github.com/uhd-urz/elAPI).

<img height="371" width="624" src="https://heibox.uni-heidelberg.de/f/5f8e95d5a5954d3a88c8/?dl=1" alt="properpath on the road" />

## Usage

`ProperPath` can be used the same way as `pathlib.Path`. On the REPL (or `repr`) will show more information about the
path.

```python

>>> from properpath import ProperPath
>>> p = ProperPath("~/foo")
>>> p
ProperPath(path= /Users/culdesac/foo, actual = ~/foo, kind=dir, err_logger=<RootLogger
root(WARNING)>)
>>> isinstance(p, pathlib.Path)
True

```

You can pass a `pathlib.Path` instance to `ProperPath` and vice versa.

### Path `kind`

A `ProperPath` instance will determine if the path is a file or a directory during instance creation and store it in
`kind` attribute. If the path doesn't exist beforehand, `PropePath` will try to assume it from the path's extension.
`ProperPath` also knows how to handle special files like `/dev/null`.

```python
>>> p = ProperPath("~/foo.txt")
>>> p.exists()
False
>>> p.kind
'file'
>>> p = ProperPath("~/foo")
>>> p.exists()
True
>>> p.kind
'dir'
```

### Path instance-wide error logging

A custom logger can be passed to `ProperPath` instance. This logger will be used throughout path operations. If no
logger is passed, `ProperPath` will use `ProperPath.default_err_logger` class attribute.

```python
logger = logging.getLogger("new_logger")
p = ProperPath("~/Downloads/metadata.txt", err_logger=logger)

with p.open("w") as f:
    f.write("Hello, world!")
# Any exception raised during path operations will be logged to the new_logger, 
# before being raised.
```

### Path `create` and `remove` methods

To create a new file or directory, `pathlib.Path` would require a boilerplate `if path.is_file():` or
`if path.is_dir():` block if the path is unknown. `ProperPath` provides the `create` method that simplifies this step.
Just call `create` on any path to create it. If the path already exists, nothing happens.

```python
ProperPath("/etc/my_app/config.toml").create()
```

Similarly, the `remove` removes the need to boilerplate check for if the path is a file or a directory, if it is empty
or not. If the path is a directory, everything inside it will be removed recursively by default. `remove` method accepts
a `parent_only` argument, which if `True`, will only remove the top-level contents only (i.e., will remove only files,
will not do a recursion into other directories).

```text
|_.local
    |_ share
        |_ my_app
            |_ config.toml
            |_ custom/
                |_ plugins/
```

```python
ProperPath("~/.local/share/my_app/").remove(parent_only=True)
# Only ~/.local/share/my_app/config.toml will be removed. custom/ and plugins/ will be left alone.
```

### Better Platformdirs

`ProperPath` comes integrated with a popular library used for managing common application
paths: [platformdirs](https://github.com/tox-dev/platformdirs). E.g., to get OS-standard locations for configuration
files, logs, caches, etc. See
platformdirs [documentation](https://github.com/tox-dev/platformdirs?tab=readme-ov-file#platformdirs-for-convenience)
for more details. Values from `platformdirs` by default are strings. But with `ProperPath.platformdirs`, you can get
`ProperPath` instances instead.

```python
>>> from properpath import ProperPath
>>> app_dirs = ProperPath.platformdirs("my_app", "my_org")
>>> app_dirs.user_config_dir
ProperPath(path=/Users/culdesac/Library/Application Support/my_app, actual=('/Users/culdesac/Library/Application Support/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_data_dir
ProperPath(path=/Users/culdesac/Library/Application Support/my_app, actual=('/Users/culdesac/Library/Application Support/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_cache_dir
ProperPath(path=/Users/culdesac/Library/Caches/my_app, actual=('/Users/culdesac/Library/Caches/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.site_data_dir
ProperPath(path=/Library/Application Support/my_app, actual=('/Library/Application Support/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.site_config_dir
ProperPath(path=/Library/Application Support/my_app, actual=('/Library/Application Support/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_documents_dir
ProperPath(path=/Users/culdesac/Documents, actual=('/Users/culdesac/Documents',), kind=dir, exists=True, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_downloads_dir
ProperPath(path=/Users/culdesac/Downloads, actual=('/Users/culdesac/Downloads',), kind=dir, exists=True, err_logger=<RootLogger root (WARNING)>)
>>>  # Etc. See whole list: https://github.com/tox-dev/platformdirs?tab=readme-ov-file#platformdirs-for-convenience
```

Platformdirs enforces a strict directory structure for macOS, but many tools out there follow the Unix-style directory
structures on macOS as well. `ProperPath` provides an additional `follow_unix` argument to `ProperPath.platformdirs`
that will enforce Unix-style directory structure on macOS, but will leave Windows as is.

```python
>>> app_dirs = ProperPath.platformdirs("my_app", "my_org", follow_unix=True)
>>> app_dirs.user_config_dir
ProperPath(path=/Users/culdesac/.config/my_app, actual=('/Users/culdesac/.config/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_data_dir
ProperPath(path=/Users/culdesac/.local/share/my_app, actual=('/Users/culdesac/.local/share/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_cache_dir
ProperPath(path=/Users/culdesac/.cache/my_app, actual=('/Users/culdesac/.cache/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.site_data_dir
ProperPath(path=/usr/local/share/my_app, actual=('/usr/local/share/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.site_config_dir
ProperPath(path=/etc/xdg/my_app, actual=('/etc/xdg/my_app',), kind=dir, exists=False, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_documents_dir
ProperPath(path=/Users/culdesac/Documents, actual=('/Users/culdesac/Documents',), kind=dir, exists=True, err_logger=<RootLogger root (WARNING)>)
>>> app_dirs.user_downloads_dir
ProperPath(path=/Users/culdesac/Downloads, actual=('/Users/culdesac/Downloads',), kind=dir, exists=True, err_logger=<RootLogger root (WARNING)>)
```

### Path validation

We often write to files, so we need to make sure if the file we're writing to is even _writable_; i.e., if the file
exists, if there is enough storage space, if there is sufficient permission, etc. `ProperPath` comes with a
`PathWriteValidator` class that can be used to do exactly that. Example: we want to write to a file from a list of
fallback files, and we want to write to the first one that works.

```python
from properpath.validators import PathValidationError, PathWriteValidator

user_desired_paths = ["/usr/usb/Downloads/", "~/Downloads"]
# PathWriteValidator will convert the strings to ProperPath instances during validation.
try:
    validated_path = PathWriteValidator(user_desired_paths).validate()
except PathValidationError as e:
    # PathValidationError is raised when all paths fail validation.
    raise e("None of the paths are writable.")
else:
    validated_path.write_text("Hooray!")
```

Of course, a single path can also be passed to `PathWriteValidator`.

`ProperPath` comes with a `PathException` attribute that stores any exception raised during any path operation. In other
words, an error raised for a path is tied to that path only. We can use this `PathException` to implement a fallback
mechanism. I.e., if we want to just forget about the error from one path, and move onto the next path. From one of our
previous examples:

```python
p = ProperPath("~/Downloads/metadata.txt")

try:
    with p.open("w") as f:
        f.write("Hello, world!")
except p.PathException as e:
    # try a different path
    p.err_logger.warning(f"Failed to write to {p}. Exception: {e!r}")
    p.err_logger.info("Trying another path...")
    ProperPath("~/metadata.txt").write_text("Hello, world!")
```

In some ways, `PathException` treats errors as values.
