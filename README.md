# linkture


## Purpose

Functions to convert Bible scripture references to a list of coded (non-contiguous) ranges (and vice-versa) or to HTML \<href> links (specifically for use in *jwpub* archives, but these can be easily modified as needed). The ranges are in the format `bbcccvvv`, where `b` is book, `c` is chapter, and `v` is verse.

The *res/books.json* list contains Bible book names in English, Spanish, German, French, Italian and Portuguese; it can be modified for other languages. The first entry is the official full name; the second is the standard abbreviation; the third is the official abbreviation. After that can be added any other variants of the book name.

**Note** that this script _does not_ parse text files for scriptures - it only parses what is enclosed within `{{ }}`, or provided as a string argument. Also, it doesn't check if chapters or verses are within range (actually exist).

____
## Usage

```
python3 linkture.py [-h] [-v] (-f in-file out-file | -s reference)
                   [--language {English,Spanish,German,French,Italian,Portuguese}]
                   [--full | --official | --standard] [-l | -r] [-q]

process and link/encode Bible scripture references; see README for more information

options:
  -h, --help            show this help message and exit
  -v, --version         show version and exit
  --language {English,Spanish,German,French,Italian,Portuguese}
                        indicate language of book names (English if unspecified)
  -q, --quiet           don't show processing status

operational method:
  choose between terminal or files input/output:

  -f in-file out-file   work with files (UTF-8)
  -s reference          process "reference(s)"

output format (optional):
  if provided, book names will be rewritten accordingly:

  --full                output as full name
  --official            output as official abbreviation
  --standard            output as standard abbreviation

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
```

Or import it into your script:
```
from linkture import Scriptures

s = Scriptures(language='English', form=1, rewrite=True)

url = s.link_scripture("John 17:3, 26")
codes = s.code_scripture("Psalm 83:18; Mt 6:9")
scriptures = s.decode_scripture([('43017017', '43017017'), ('55003016', '55003017')])
scriptures = s.rewrite_scripture("EXOD 3:15; Re 21:4")
```
Parameters:
* *form*
  * **0** for full name format (default)
  * **1** for standard abbreviation format
  * **2** for official abbreviation format
* *rewrite*
  * **False** - book names not rewritten (default)
  * **True** - rewrite book names

____
## Feedback

Feel free to [get in touch and post any issues and suggestions](https://github.com/erykjj/linkture/issues).
