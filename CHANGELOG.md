# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.8] - 2025-10-16

Release with minor features.

### Added

- Added [`get_text`](https://uhd-urz.github.io/properpath/apis/properpath/#properpath.ProperPath.get_text) and
  [`get_bytes`](https://uhd-urz.github.io/properpath/apis/properpath/#properpath.ProperPath.get_bytes) methods

### Changed

- Avoid resolving the path in `open` method

## [0.2.7] - 2025-10-09

This release adds Pydantic support and Rich pretty REPL printing support to ProperPath. 2 additional optional
dependencies have been added: `properpath[pydantic]`,` properpath[rich]`.

## [0.2.6] - 2025-09-29

Release with minor improvements.

### Added

- Added alias `P` for `ProperPath`
- Improved documentation
- Show `is_symlink()` in `__repr__` output

## [0.2.5] - 2025-09-28

A bugfix release. See the main changes below.

### Changed

- Added better `__deepcopy__` implementation

## [0.2.4] - 2025-09-26

A bugfix release. See the main changes below.

### Fixed

- `__deepcopy__` throwing unexpected errors (#2)

## [0.2.3] - 2025-09-26

Initial release of `properpath`.

### Fixed

- Unexpected `kind` caching (#1)

### Added

- ProperPath documentation: https://uhd-urz.github.io/properpath/
- PyPI package: https://pypi.org/project/properpath/
