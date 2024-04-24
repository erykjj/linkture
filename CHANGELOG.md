# linkture CHANGELOG

## [Unreleased]

### Added

### Changed

- Restructured project layout
- Renamed main script to __main__.py for packaging

### Fixed

### Removed

- Removed setup.py and requirements.txt - superceded by pyproject.toml

____
## [2.5.4] - 2024-04-24
### Changed

- Corrections for PyPi package distribution

## [2.5.3] - 2024-04-23
### Added

- Added fall-back for no arguments
- Added requirements.txt and pyproject.toml

### Changed

- Increased min Python version to 3.9 in order for Pandas to work
- Keep Pandas at v2.2.*

## [2.5.2] - 2024-02-12
### Added

- Added Hungarian (Magyar, hu)

## [2.5.1] - 2024-01-23
### Changed

- Replaced hyphen with non-breaking hyphen

## [2.5.0] - 2024-01-15
### Added

- Added segment separator option (space by default)

## [2.4.4] - 2024-01-10
### Changed

- Adjusted verse numbering

## [2.4.3] - 2024-01-09
### Added

- Added Ukrainian to list of available languages

### Fixed

- Fixed upper-case links

## [2.4.2] - 2023-06-30
### Added

- Added Cebuano and Tagalog to list of available languages

## [2.4.1] - 2023-06-28
### Added

- Added two more auxiliary look-up functions

### Changed

- Renamed auxiliary functions
  - Adjusted command-line options
- Adjusted output format for verse code lookup

## [2.4.0] - 2023-06-23
### Added

- Added verse number lookup functions and data
  - Excludes spurious John 7:53-8:11

### Changed

- Corrected last verse:
  - Mark 16:8
  - John 7:52

## [2.3.1] - 2023-04-18
### Fixed

- Improved scripture detection
- Improved selecting correct chapter separator (',' or ';')

## [2.3.0] - 2023-04-10
### Changed

- Standardized `<a>` tag prefix/suffix for commandline and function
  - If no prefix or suffix is provided, *both* return a skeleton `<a>` tag; to get a proper tag, add a prefix and suffix as required

## [2.2.0] - 2023-03-04
### Added

- Re-added unidecode for latin-based languages only
  - Now Chinese, Japanese, etc. work correctly

### Changed

- Another **major code reduction and optimization**
  - re-using previously processed results to imporove functionality
- Decoding expands into combined strings

### Fixed

- Fixed tags on pre-tagged scriptures were being removed if the scripture was not recognized (another language, etc.)

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
[2.5.4]:https://github.com/erykjj/linkture/releases/tag/v2.5.4
[2.5.3]:https://github.com/erykjj/linkture/releases/tag/v2.5.3
[2.5.2]:https://github.com/erykjj/linkture/releases/tag/v2.5.2
[2.5.1]:https://github.com/erykjj/linkture/releases/tag/v2.5.1
[2.5.0]:https://github.com/erykjj/linkture/releases/tag/v2.5.0
[2.4.4]:https://github.com/erykjj/linkture/releases/tag/v2.4.4
[2.4.3]:https://github.com/erykjj/linkture/releases/tag/v2.4.3
[2.4.2]:https://github.com/erykjj/linkture/releases/tag/v2.4.2
[2.4.1]:https://github.com/erykjj/linkture/releases/tag/v2.4.1
[2.4.0]:https://github.com/erykjj/linkture/releases/tag/v2.4.0
[2.3.1]:https://github.com/erykjj/linkture/releases/tag/v2.3.1
[2.3.0]:https://github.com/erykjj/linkture/releases/tag/v2.3.0
[2.2.0]:https://github.com/erykjj/linkture/releases/tag/v2.2.0
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
