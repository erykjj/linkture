# linkture CHANGELOG

## [Unreleased]

### Added

### Changed

- code optimization

### Fixed

### Removed

____
## [2.1.1] - 2023-02-27
### Fixed

- Restricted greediness of parser
- Don't add space if no chapter(s)/verse(s) follow book name

## [2.1.0] - 2023-02-25
### Added

- Added option (`-u`) for **capitalization** (upper-case) of book names

### Changed

- Much **code clean-up/optimization**
- Providing prefix and suffix for linking from commandline is optional
  - `-l` provides a default prefix and suffix
- Links always rewritten (`--full` by default)

### Fixed

- Fixed variour edge-case in link re-writing

### Removed

- Removed unidecode dependence
  - already handled by regex

## [2.0.2] - 2023-02-14
### Fixed

- Fixed: books with numbers that were't supposed to be rewritten were actually rewritten with out a space (eg. '1 Timothy' was turned into '1Timothy')

## [2.0.1] - 2023-02-08
### Changed

- Renamed internal variables
- Separated parsing from tagging

### Fixed

- Fixed linking and translation not working well together
- Fixed linking whole book (eg., '2 John')

## [2.0.0] - 2023-02-07
### Added

- BIG CODE REWRITE to include **parser** and **validation**
  - you *will* need to adjust your code

### Changed

- Moved constant resources (book names and ranges) to SQLite db instead of json
  - *custom.json* is still there for easier modification

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
[2.1.1]:https://github.com/erykjj/linkture/releases/tag/v2.1.1
[2.1.0]:https://github.com/erykjj/linkture/releases/tag/v2.1.0
[2.0.2]:https://github.com/erykjj/linkture/releases/tag/v2.0.2
[2.0.1]:https://github.com/erykjj/linkture/releases/tag/v2.0.1
[2.0.0]:https://github.com/erykjj/linkture/releases/tag/v2.0.0
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
