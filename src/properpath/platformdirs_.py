from dataclasses import asdict, dataclass
from pathlib import Path

from platformdirs import PlatformDirs
from platformdirs.android import Android
from platformdirs.macos import MacOS
from platformdirs.unix import Unix
from platformdirs.windows import Windows


@dataclass(frozen=True)
class PlatformDirsCommonAttrs:
    """
    PlatformDirsCommonAttrs defines the main attributes of platformdirs.
    This class is used as a mixin, and it also ensures that IDEs/editors auto-suggestion works
    with an instantiated P.platformdirs() object.
    """

    site_cache_dir: "ProperPath" = NotImplemented
    site_cache_path: "ProperPath" = NotImplemented
    site_config_dir: "ProperPath" = NotImplemented
    site_config_path: "ProperPath" = NotImplemented
    site_data_dir: "ProperPath" = NotImplemented
    site_data_path: "ProperPath" = NotImplemented
    site_runtime_dir: "ProperPath" = NotImplemented
    site_runtime_path: "ProperPath" = NotImplemented
    user_cache_dir: "ProperPath" = NotImplemented
    user_cache_path: "ProperPath" = NotImplemented
    user_config_dir: "ProperPath" = NotImplemented
    user_config_path: "ProperPath" = NotImplemented
    user_data_dir: "ProperPath" = NotImplemented
    user_data_path: "ProperPath" = NotImplemented
    user_desktop_dir: "ProperPath" = NotImplemented
    user_desktop_path: "ProperPath" = NotImplemented
    user_documents_dir: "ProperPath" = NotImplemented
    user_documents_path: "ProperPath" = NotImplemented
    user_downloads_dir: "ProperPath" = NotImplemented
    user_downloads_path: "ProperPath" = NotImplemented
    user_log_dir: "ProperPath" = NotImplemented
    user_log_path: "ProperPath" = NotImplemented
    user_music_dir: "ProperPath" = NotImplemented
    user_music_path: "ProperPath" = NotImplemented
    user_pictures_dir: "ProperPath" = NotImplemented
    user_pictures_path: "ProperPath" = NotImplemented
    user_runtime_dir: "ProperPath" = NotImplemented
    user_runtime_path: "ProperPath" = NotImplemented
    user_state_dir: "ProperPath" = NotImplemented
    user_state_path: "ProperPath" = NotImplemented
    user_videos_dir: "ProperPath" = NotImplemented


platformdirs_attrs = PlatformDirsCommonAttrs()


class _PlatformDirsGetAttrPatcher:
    def __init__(self, path_cls: type[Path]):
        self.path_cls = path_cls

    def patch(
        self,
        attr: str,
        super_obj: PlatformDirs | Unix | MacOS | Windows | Android,
    ):
        if attr in asdict(platformdirs_attrs).keys():
            return self.path_cls(getattr(super_obj, attr))
        return super_obj.__getattribute__(attr)


# MyPy complains about the attributes of PlatformDirsCommonAttrs to be of different
# types (ProperPath) from the base class PlatformDirs's attributes' types (str).
# Hence, ProperPlatformDirs and similar classes are type-ignored.
class ProperPlatformDirs(  # type: ignore
    _PlatformDirsGetAttrPatcher, PlatformDirs, PlatformDirsCommonAttrs
):
    def __init__(self, *args, path_cls: type[Path], **kwargs):
        super().__init__(path_cls=path_cls)
        super(PlatformDirs, self).__init__(*args, **kwargs)

    def __getattribute__(self, item):
        return super().patch(item, super())


class ProperUnix(_PlatformDirsGetAttrPatcher, Unix, PlatformDirsCommonAttrs):  # type: ignore
    def __init__(self, *args, path_cls: type[Path], **kwargs):
        super().__init__(path_cls=path_cls)
        super(Unix, self).__init__(*args, **kwargs)

    def __getattribute__(self, item):
        return super().patch(item, super())


class ProperMacOS(_PlatformDirsGetAttrPatcher, MacOS, PlatformDirsCommonAttrs):  # type: ignore
    def __init__(self, *args, path_cls: type[Path], **kwargs):
        super().__init__(path_cls=path_cls)
        super(MacOS, self).__init__(*args, **kwargs)

    def __getattribute__(self, item):
        return super().patch(item, super())


class ProperAndroid(_PlatformDirsGetAttrPatcher, Android, PlatformDirsCommonAttrs):  # type: ignore
    def __init__(self, *args, path_cls: type[Path], **kwargs):
        super().__init__(path_cls=path_cls)
        super(Android, self).__init__(*args, **kwargs)

    def __getattribute__(self, item):
        return super().patch(item, super())


class ProperWindows(_PlatformDirsGetAttrPatcher, Windows, PlatformDirsCommonAttrs):  # type: ignore
    def __init__(self, *args, path_cls: type[Path], **kwargs):
        super().__init__(path_cls=path_cls)
        super(Windows, self).__init__(*args, **kwargs)

    def __getattribute__(self, item):
        return super().patch(item, super())
