# linkture changelog

## [Unreleased]

### Added

### Changed

### Fixed

### Removed

____
## [1.4.0] - 2022-11-29

### Added

- Added option to rewrite/fix scriptures:
  - full name format (eg., "Matthew")
  - standard abbreviation format (eg., "Matt")
  - official abbreviation format (eg., "Mt")

### Changed

- Adjusted commandline options and function parameters
- Default output is a rewritten scripture (always rewrites/fixes output)
  - Range list and jwpub link are other options
- Updated README

## [1.3.2] - 2022-10-26

### Changed

- Updated set of book names in English

### Fixed

- Improved out-of-range chapter/verse detection
- Convert consecutive ranges into lists (eg. "1-2" -> "1, 2")

## [1.3.1] - 2022-08-27

### Added

- Add functionality with other language sets (English is default, Spanish, French, German, Italian, Portuguese)
  - The sets can be extended as needed

### Changed

- Updated English book names list

## [1.3.0] - 2022-08-19

### Added

- added function to decode list of coded references

### Changed

- linking removes repeated book names (eg. 'John 3:16; John 17:3' is processed as 'John 3:16; 17:3')

## [1.2.3] - 2022-08-08

### Fixed

- refined regex for multi-word book names (eg. "Song of Solomon")

## [1.2.2] - 2022-08-08

- Initial release
____
[Unreleased]: https://github.com/erykjj/linkture
[1.4.0]:https://github.com/erykjj/linkture/releases/tag/v1.4.0
[1.3.2]:https://github.com/erykjj/linkture/releases/tag/v1.3.2
[1.3.1]:https://github.com/erykjj/linkture/releases/tag/v1.3.1
[1.3.0]:https://github.com/erykjj/linkture/releases/tag/v1.3.0
[1.2.3]:https://github.com/erykjj/linkture/releases/tag/v1.2.3
[1.2.2]:https://github.com/erykjj/linkture/releases/tag/v1.2.2
