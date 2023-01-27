# linkture CHANGELOG

## [Unreleased]

### Added

### Changed

- Combined *form* and *rewrite* parameter into just *form* (not specified means no rewrite)
  - **Note:** These are now strings ("full", "standard", "official"), instead of the previous integers

### Fixed

### Removed

____
## [1.5.0] - 2023-01-25

### Added

- Additional languages
  - Now recognizing: Chinese, Danish, Dutch, English, French, German, Greek, Italian, Japanese, Korean, Norwegian, Polish, Portuguese, Russian, and Spanish
- Added **translation** to/from any of the above languages

### Changed

- Split off 'non-official' Bible book variants into a separate *custom.json*
  - **Note**: if you've modified the *books.json* with your own variants, make sure to transfer these to the *custom.json* files (follow the formatting as in the file); the *books.json* **will be over-written** by the 'official' variants in the available languages

### Fixed

- Processing of accented characters
  - not tested fully with non-Latin characters (Russian, Chinese, etc.)

## [1.4.3] - 2023-01-24

### Changed

- Added UTF-8 specification on opened files

## [1.4.2] - 2023-01-20

### Fixed

- Skip rewriting of incorrectly formatted/unrecognized scriptures

## [1.4.1] - 2022-12-13

### Fixed

- Fixed type-checking warnings
- Fixed in-range testing

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

- Added function to decode list of coded references

### Changed

- Linking removes repeated book names (eg. 'John 3:16; John 17:3' is processed as 'John 3:16; 17:3')

## [1.2.3] - 2022-08-08

### Fixed

- Refined regex for multi-word book names (eg. "Song of Solomon")

## [1.2.2] - 2022-08-08

- Initial release

____
[Unreleased]: https://github.com/erykjj/linkture
[1.5.0]:https://github.com/erykjj/linkture/releases/tag/v1.5.0
[1.4.3]:https://github.com/erykjj/linkture/releases/tag/v1.4.3
[1.4.2]:https://github.com/erykjj/linkture/releases/tag/v1.4.2
[1.4.1]:https://github.com/erykjj/linkture/releases/tag/v1.4.1
[1.4.0]:https://github.com/erykjj/linkture/releases/tag/v1.4.0
[1.3.2]:https://github.com/erykjj/linkture/releases/tag/v1.3.2
[1.3.1]:https://github.com/erykjj/linkture/releases/tag/v1.3.1
[1.3.0]:https://github.com/erykjj/linkture/releases/tag/v1.3.0
[1.2.3]:https://github.com/erykjj/linkture/releases/tag/v1.2.3
[1.2.2]:https://github.com/erykjj/linkture/releases/tag/v1.2.2
