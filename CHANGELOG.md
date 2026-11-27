# Changelog

All notable changes to this project are documented in this file.
The format is [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Version numbers follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Title normalization overwrites the named column, and `--compare` keeps that column while writing the reading beside it. A running-text column can be normalized in place, with double quotes replaced by single quotes. A semicolon-separated file is written with commas, and a field that contains a comma is quoted
- `--classificacao` sets every `classificacao_id` cell to the given value. On transform, that value also selects the mask for the level and the parent

### Fixed

- Text normalization keeps a semicolon inside the last column and still replaces the double quotes there, reading each physical line when a quoted row would otherwise lose the column
- The text column is written between one pair of quotes around that column, while spaces beside a replaced quote stay where they were

## [0.2.0-rc.3] - 2026-11-26

### Added

- An item CSV can be shaped to the schema in place, with the item id, level, and parent taken from the open mask of its classification

### Fixed

- The Vigência search on the series, classification, level, and item lists keeps the chosen year and applies that window, so codes outside it and inactive records stay out of the result

## [0.2.0-rc.1] - 2026-11-17

### Added

- One meaning of "valid for this window", shared by an inquiry and by the series, classification, level, and item lists
- A Vigência search on those four lists that shows the assumed validity, version, and record day before the filter runs
- A refusal when the day does not exist or when a validity date and a registered version are combined, and a notice when a period is reordered earlier-to-later

