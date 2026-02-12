import typing
from pathlib import Path

if typing.TYPE_CHECKING:
    from .properpath import ProperPath

class PlatformDirsCommonAttrs:
    site_cache_dir: ProperPath
    site_cache_path: ProperPath
    site_config_dir: ProperPath
    site_config_path: ProperPath
    site_data_dir: ProperPath
    site_data_path: ProperPath
    site_runtime_dir: ProperPath
    site_runtime_path: ProperPath
    user_cache_dir: ProperPath
    user_cache_path: ProperPath
    user_config_dir: ProperPath
    user_config_path: ProperPath
    user_data_dir: ProperPath
    user_data_path: ProperPath
    user_desktop_dir: ProperPath
    user_desktop_path: ProperPath
    user_documents_dir: ProperPath
    user_documents_path: ProperPath
    user_downloads_dir: ProperPath
    user_downloads_path: ProperPath
    user_log_dir: ProperPath
    user_log_path: ProperPath
    user_music_dir: ProperPath
    user_music_path: ProperPath
    user_pictures_dir: ProperPath
    user_pictures_path: ProperPath
    user_runtime_dir: ProperPath
    user_runtime_path: ProperPath
    user_state_dir: ProperPath
    user_state_path: ProperPath
    user_videos_dir: ProperPath

class ProperPlatformDirs:
    # The following attribute hack is only necessary for mypy to get
    # the ProperPath type instead of the platformdirs "str" for the end-user
    site_cache_dir: ProperPath
    site_cache_path: ProperPath
    site_config_dir: ProperPath
    site_config_path: ProperPath
    site_data_dir: ProperPath
    site_data_path: ProperPath
    site_runtime_dir: ProperPath
    site_runtime_path: ProperPath
    user_cache_dir: ProperPath
    user_cache_path: ProperPath
    user_config_dir: ProperPath
    user_config_path: ProperPath
    user_data_dir: ProperPath
    user_data_path: ProperPath
    user_desktop_dir: ProperPath
    user_desktop_path: ProperPath
    user_documents_dir: ProperPath
    user_documents_path: ProperPath
    user_downloads_dir: ProperPath
    user_downloads_path: ProperPath
    user_log_dir: ProperPath
    user_log_path: ProperPath
    user_music_dir: ProperPath
    user_music_path: ProperPath
    user_pictures_dir: ProperPath
    user_pictures_path: ProperPath
    user_runtime_dir: ProperPath
    user_runtime_path: ProperPath
    user_state_dir: ProperPath
    user_state_path: ProperPath
    user_videos_dir: ProperPath

    def __init__(self, *args, path_cls: type[Path], **kwargs) -> None: ...

class ProperUnix:
    site_cache_dir: ProperPath
    site_cache_path: ProperPath
    site_config_dir: ProperPath
    site_config_path: ProperPath
    site_data_dir: ProperPath
    site_data_path: ProperPath
    site_runtime_dir: ProperPath
    site_runtime_path: ProperPath
    user_cache_dir: ProperPath
    user_cache_path: ProperPath
    user_config_dir: ProperPath
    user_config_path: ProperPath
    user_data_dir: ProperPath
    user_data_path: ProperPath
    user_desktop_dir: ProperPath
    user_desktop_path: ProperPath
    user_documents_dir: ProperPath
    user_documents_path: ProperPath
    user_downloads_dir: ProperPath
    user_downloads_path: ProperPath
    user_log_dir: ProperPath
    user_log_path: ProperPath
    user_music_dir: ProperPath
    user_music_path: ProperPath
    user_pictures_dir: ProperPath
    user_pictures_path: ProperPath
    user_runtime_dir: ProperPath
    user_runtime_path: ProperPath
    user_state_dir: ProperPath
    user_state_path: ProperPath
    user_videos_dir: ProperPath

    def __init__(self, *args, path_cls: type[Path], **kwargs) -> None: ...

class ProperMacOS:
    site_cache_dir: ProperPath
    site_cache_path: ProperPath
    site_config_dir: ProperPath
    site_config_path: ProperPath
    site_data_dir: ProperPath
    site_data_path: ProperPath
    site_runtime_dir: ProperPath
    site_runtime_path: ProperPath
    user_cache_dir: ProperPath
    user_cache_path: ProperPath
    user_config_dir: ProperPath
    user_config_path: ProperPath
    user_data_dir: ProperPath
    user_data_path: ProperPath
    user_desktop_dir: ProperPath
    user_desktop_path: ProperPath
    user_documents_dir: ProperPath
    user_documents_path: ProperPath
    user_downloads_dir: ProperPath
    user_downloads_path: ProperPath
    user_log_dir: ProperPath
    user_log_path: ProperPath
    user_music_dir: ProperPath
    user_music_path: ProperPath
    user_pictures_dir: ProperPath
    user_pictures_path: ProperPath
    user_runtime_dir: ProperPath
    user_runtime_path: ProperPath
    user_state_dir: ProperPath
    user_state_path: ProperPath
    user_videos_dir: ProperPath

    def __init__(self, *args, path_cls: type[Path], **kwargs) -> None: ...

class ProperAndroid:
    site_cache_dir: ProperPath
    site_cache_path: ProperPath
    site_config_dir: ProperPath
    site_config_path: ProperPath
    site_data_dir: ProperPath
    site_data_path: ProperPath
    site_runtime_dir: ProperPath
    site_runtime_path: ProperPath
    user_cache_dir: ProperPath
    user_cache_path: ProperPath
    user_config_dir: ProperPath
    user_config_path: ProperPath
    user_data_dir: ProperPath
    user_data_path: ProperPath
    user_desktop_dir: ProperPath
    user_desktop_path: ProperPath
    user_documents_dir: ProperPath
    user_documents_path: ProperPath
    user_downloads_dir: ProperPath
    user_downloads_path: ProperPath
    user_log_dir: ProperPath
    user_log_path: ProperPath
    user_music_dir: ProperPath
    user_music_path: ProperPath
    user_pictures_dir: ProperPath
    user_pictures_path: ProperPath
    user_runtime_dir: ProperPath
    user_runtime_path: ProperPath
    user_state_dir: ProperPath
    user_state_path: ProperPath
    user_videos_dir: ProperPath

    def __init__(self, *args, path_cls: type[Path], **kwargs) -> None: ...

class ProperWindows:
    site_cache_dir: ProperPath
    site_cache_path: ProperPath
    site_config_dir: ProperPath
    site_config_path: ProperPath
    site_data_dir: ProperPath
    site_data_path: ProperPath
    site_runtime_dir: ProperPath
    site_runtime_path: ProperPath
    user_cache_dir: ProperPath
    user_cache_path: ProperPath
    user_config_dir: ProperPath
    user_config_path: ProperPath
    user_data_dir: ProperPath
    user_data_path: ProperPath
    user_desktop_dir: ProperPath
    user_desktop_path: ProperPath
    user_documents_dir: ProperPath
    user_documents_path: ProperPath
    user_downloads_dir: ProperPath
    user_downloads_path: ProperPath
    user_log_dir: ProperPath
    user_log_path: ProperPath
    user_music_dir: ProperPath
    user_music_path: ProperPath
    user_pictures_dir: ProperPath
    user_pictures_path: ProperPath
    user_runtime_dir: ProperPath
    user_runtime_path: ProperPath
    user_state_dir: ProperPath
    user_state_path: ProperPath
    user_videos_dir: ProperPath

    def __init__(self, *args, path_cls: type[Path], **kwargs) -> None: ...
