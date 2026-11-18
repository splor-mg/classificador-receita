# Changelog

All notable changes to this project are documented in this file.
The format is [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Version numbers follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed

- The Vigência search on the series, classification, level, and item lists keeps the chosen year and applies that window, so codes outside it and inactive records stay out of the result

## [0.2.0-rc.1] - 2026-11-17

### Added

- One meaning of "valid for this window", shared by an inquiry and by the series, classification, level, and item lists
- A Vigência search on those four lists that shows the assumed validity, version, and record day before the filter runs
- A refusal when the day does not exist or when a validity date and a registered version are combined, and a notice when a period is reordered earlier-to-later

