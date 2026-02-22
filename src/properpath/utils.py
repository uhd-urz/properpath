from enum import StrEnum


class PlatformNames(StrEnum):
    """
    An Enum of platform names found in
    [sys.platform](https://docs.python.org/3.13/library/sys.html#sys.platform).
    """

    aix = "aix"
    android = "android"
    emscripten = "emscripten"
    ios = "ios"
    linux = "linux"
    darwin = "darwin"
    win32 = "win32"
    cygwin = "cygwin"
    wasi = "wasi"
