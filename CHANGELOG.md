# Changelog

All notable changes to this project are documented in this file.
The format is [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Version numbers follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Validity search: the series, classification, level, and item lists can ask which codes cover a date, including LDO on 15 May. The inquiry `inquire_validity` answers the same window and can also take a period.
- An impossible day, or a validity date combined with a registered version, does not run the search. An inverted period is reordered and the operator is told.
