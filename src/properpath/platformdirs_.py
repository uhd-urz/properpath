from dataclasses import asdict, dataclass
from pathlib import Path

from platformdirs import PlatformDirs
from platformdirs.android import Android
from platformdirs.macos import MacOS
from platformdirs.unix import Unix
from platformdirs.windows import Windows


@dataclass(frozen=True)
class PlatformDirsCommonAttrs:
    site_cache_dir: str = "site_cache_dir"
    site_cache_path: str = "site_cache_path"
    site_config_dir: str = "site_config_dir"
    site_config_path: str = "site_config_path"
    site_data_dir: str = "site_data_dir"
    site_data_path: str = "site_data_path"
    site_runtime_dir: str = "site_runtime_dir"
    site_runtime_path: str = "site_runtime_path"
    user_cache_dir: str = "user_cache_dir"
    user_cache_path: str = "user_cache_path"
    user_config_dir: str = "user_config_dir"
    user_config_path: str = "user_config_path"
    user_data_dir: str = "user_data_dir"
    user_data_path: str = "user_data_path"
    user_desktop_dir: str = "user_desktop_dir"
    user_desktop_path: str = "user_desktop_path"
    user_documents_dir: str = "user_documents_dir"
    user_documents_path: str = "user_documents_path"
    user_downloads_dir: str = "user_downloads_dir"
    user_downloads_path: str = "user_downloads_path"
    user_log_dir: str = "user_log_dir"
    user_log_path: str = "user_log_path"
    user_music_dir: str = "user_music_dir"
    user_music_path: str = "user_music_path"
    user_pictures_dir: str = "user_pictures_dir"
    user_pictures_path: str = "user_pictures_path"
    user_runtime_dir: str = "user_runtime_dir"
    user_runtime_path: str = "user_runtime_path"
    user_state_dir: str = "user_state_dir"
    user_state_path: str = "user_state_path"
    user_videos_dir: str = "user_videos_dir"


platformdirs_attrs = PlatformDirsCommonAttrs()


class _PlatformDirsGetAttrPatcher:
    def __init__(self, path_cls: type[Path]):
        self.path_cls = path_cls

    def patch(
        self,
        attr: str,
        super_obj: PlatformDirs | Unix | MacOS | Windows | Android,
    ):
        if attr in asdict(platformdirs_attrs).values():
            return self.path_cls(getattr(super_obj, attr))
        return super_obj.__getattribute__(attr)


class ProperPlatformDirs(_PlatformDirsGetAttrPatcher, PlatformDirs):
    def __init__(self, *args, path_cls: type[Path], **kwargs):
        super().__init__(path_cls=path_cls)
        super(PlatformDirs, self).__init__(*args, **kwargs)

    def __getattribute__(self, item):
        return super().patch(item, super())


class ProperUnix(_PlatformDirsGetAttrPatcher, Unix):
    def __init__(self, *args, path_cls: type[Path], **kwargs):
        super().__init__(path_cls=path_cls)
        super(Unix, self).__init__(*args, **kwargs)

    def __getattribute__(self, item):
        return super().patch(item, super())


class ProperMacOS(_PlatformDirsGetAttrPatcher, MacOS):
    def __init__(self, *args, path_cls: type[Path], **kwargs):
        super().__init__(path_cls=path_cls)
        super(MacOS, self).__init__(*args, **kwargs)

    def __getattribute__(self, item):
        return super().patch(item, super())


class ProperAndroid(_PlatformDirsGetAttrPatcher, Android):
    def __init__(self, *args, path_cls: type[Path], **kwargs):
        super().__init__(path_cls=path_cls)
        super(Android, self).__init__(*args, **kwargs)

    def __getattribute__(self, item):
        return super().patch(item, super())


class ProperWindows(_PlatformDirsGetAttrPatcher, Windows):
    def __init__(self, *args, path_cls: type[Path], **kwargs):
        super().__init__(path_cls=path_cls)
        super(Windows, self).__init__(*args, **kwargs)

    def __getattribute__(self, item):
        return super().patch(item, super())
