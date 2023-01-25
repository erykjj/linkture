# linkture


## Purpose

Functions to translate and/or convert Bible scripture references to a list of coded (non-contiguous) ranges (and vice-versa) or to HTML \<href> links (specifically for use in *jwpub* archives, but these can be easily modified as needed). The ranges are in the format `bbcccvvv`, where `b` is book, `c` is chapter, and `v` is verse.

The *res/books.json* list contains Bible book names in Chinese, Danish, Dutch, English, French, German, Greek, Italian, Japanese, Korean, Norwegian, Polish, Portuguese, Russian, and Spanish. Any other variants of book names can be added to the *res/custom.json* list.

**Note** that this script _does not_ (yet) parse text files for scriptures - it only parses what is enclosed within `{{ }}`, or provided as a string argument.

____
## Installation

Download [latest source](https://github.com/erykjj/linkture/releases/latest) and `python3 -m pip install linkture-*.tar.gz`.

____
## Command-line usage

```
python3 linkture.py [-h] [-v] (-f in-file out-file | -s reference)
                    [--language {Chinese,Danish,Dutch,English,French,German,Greek,Italian,Japanese,Korean,Norwegian,Polish,Portuguese,Russian,Spanish}]
                    [--translate {Chinese,Danish,Dutch,English,French,German,Greek,Italian,Japanese,Korean,Norwegian,Polish,Portuguese,Russian,Spanish}]
                    [--full | --official | --standard] [-l | -r] [-q]

process, translate, link/encode Bible scripture references; see README for more information

options:
  -h, --help            show this help message and exit
  -v, --version         show version and exit
  --language {Chinese,Danish,Dutch,English,French,German,Greek,Italian,Japanese,Korean,Norwegian,Polish,Portuguese,Russian,Spanish}
                        indicate source language for book names (English if unspecified)
  --translate {Chinese,Danish,Dutch,English,French,German,Greek,Italian,Japanese,Korean,Norwegian,Polish,Portuguese,Russian,Spanish}
                        indicate output language for book names (same as source if unspecified)
  -q, --quiet           don't show processing status

operational method:
  choose between terminal or files input/output:

  -f in-file out-file   work with files (UTF-8)
  -s reference          process "reference; reference; etc."

output format (optional):
  if provided, book names will be rewritten accordingly:

  --full                output as full name - default (eg., "Genesis")
  --official            output as official abbreviation (eg., "Ge")
  --standard            output as standard abbreviation (eg., "Gen.")

type of conversion:
  if not specified, references are simply rewritten according to chosen output format:

  -l, --link            create jwpub link(s)
  -r, --range           create range list

```

Or, make it executable first and run directly:
```
$ chmod +x linkture.py

$ ./linkture.py -s "Joh 17:17; 2Ti 3:16, 17"
...Processing "Joh 17:17; 2Ti 3:16, 17"
John 17:17; 2 Timothy 3:16, 17

$ ./linkture.py -s "Joh 17:17; 2Ti 3:16, 17" --standard -q
John 17:17; 2 Tim. 3:16, 17

$ ./linkture.py -s "Joh 17:17; 2Ti 3:16, 17" --official -q
Joh 17:17; 2Ti 3:16, 17

$ ./linkture.py -s "Joh 17:17; 2Ti 3:16, 17" -r -q
[('43017017', '43017017'), ('55003016', '55003017')]

$ ./linkture.py -s "Joh 17:17; 2Ti 3:16, 17" --translate Chinese -q
约翰福音 17:17; 提摩太后书 3:16, 17

$ ./linkture.py -s "Jean 17:17; 2 Timothée 3:16, 17" --language French --translate German -q
Johannes 17:17; 2. Timotheus 3:16, 17
```

## Script/import usage

```
from linkture import Scriptures

s = Scriptures(language='English', form=1, rewrite=True)

url = s.link_scripture("John 17:3, 26")
codes = s.code_scripture("Psalm 83:18; Mt 6:9")
scriptures = s.decode_scripture([('43017017', '43017017'), ('55003016', '55003017')])
scriptures = s.rewrite_scripture("EXOD 3:15; Re 21:4")
```
Parameters:
* *language*
  * Chinese, Danish, Dutch, English (default), French, German, Greek, Italian, Japanese, Korean, Norwegian, Polish, Portuguese, Russian, Spanish
* *form*
  * **0** for full name format - default (eg., "Genesis")
  * **1** for standard abbreviation format (eg., "Gen.")
  * **2** for official abbreviation format (eg., "Ge")
* *rewrite*
  * **False** - book names not rewritten (default)
  * **True** - rewrite book names (according to selected *form*)

____
## Feedback

Feel free to [get in touch and post any issues and suggestions](https://github.com/erykjj/linkture/issues).
