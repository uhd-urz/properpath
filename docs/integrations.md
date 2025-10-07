# Integrations

## Working with Pydantic

`ProperPath` can be used with [Pydantic](https://pydantic-docs.helpmanual.io/) models or fields the same way
[`pathlib.Path` can be](https://docs.pydantic.dev/latest/api/standard_library_types/#pathlibpath).

```python title="try_with_pydantic.py"
from pydantic import BaseModel

from properpath import P


class ConfigSource(BaseModel):
    local_path: P
    system_path: P


config_source = ConfigSource(
    local_path="~/.config/app.toml", system_path="/etc/app.toml"
)
print(config_source)
# Prints: ConfigSource(local_path=ProperPath(path=/Users/culdesac/.config/app.toml, actual=('~/.config/app.toml',), kind=file, exists=False, is_symlink=False, err_logger=<RootLogger root (WARNING)>), system_path=ProperPath(path=/etc/app.toml, actual=('/etc/app.toml',), kind=file, exists=False, is_symlink=False, err_logger=<RootLogger root (WARNING)>))

```

## Rich pretty-printing in REPL

If [`rich`](https://github.com/Textualize/rich) is installed (can optionally be installed with `properpath[rich]`),
`ProperPath` instances will be pretty-printed in REPL. Make sure `from rich import pretty; pretty.install()` is run in
the REPL beforehand, or added to the [`PYTHONSTARTUP`](https://www.bitecode.dev/p/happiness-is-a-good-pythonstartup)
script.

```pycon
>>> from rich import pretty; pretty.install()
>>> config_source  # from the example before 
```
![properpath rich pretty repr screenshot light](assets/rich_pretty_repr_light_opt.png#only-light){ height="500" width="507" }
![properpath rich pretty repr screenshot dark](assets/rich_pretty_repr_dark_opt.png#only-dark){ height="500" width="507" }
