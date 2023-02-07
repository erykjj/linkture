# linkture


## Purpose

This module contains functions to parse and process Bible scripture references.

The parser can work in **Chinese, Danish, Dutch, English, French, German, Greek, Italian, Japanese, Korean, Norwegian, Polish, Portuguese, Russian, and Spanish**. It will **recognize** such references and **validate** them to ensure the chapter(s) and/or verse(s) are within range.
It *does not* work with whole books (like *James*) unless they are preceded by a number (like *1 John*); otherwise it would have to look up ever single word. Also, it will *not* find the multi-word book name "Song of Solomon" (and its variations), though this (and any other scripture) can be force-detected by tagging the desired reference "manually" within the source text (eg., "{{Song of Solomon 1:1}}"). These two limitations aside, it works with most book name variants in all the available languages (including common abbreviations): "2 Sam.", "2nd Samuel", "II Samuel", "2Sa", etc. Any special/unusual variants can be added to the *res/custom.json* list.

These found references can be **extracted** as a list of references, or a list of BCV-encoded ranges in the format `bbcccvvv` (where `b` is book, `c` is chapter, and `v` is verse). Or, they can be **tagged** (with '{{ }}') within the text, or replaced with HTML \<href> **links** (with custom prefix and suffix). All of these functions can also include a **rewrite** of the reference with either a full book name, or one of two abbreviation formats, along with **translation** into one of the available languages. 

____
## Installation

Download [latest source](https://github.com/erykjj/linkture/releases/latest) and `python3 -m pip install linkture-*.tar.gz`.

____
## Command-line usage

```
python3 linkture.py [-h] [-v] [-q] (-f in-file | -r reference) [-o out-file]
                    [--language {Chinese,Danish,Dutch,English,French,German,Greek,Italian,Japanese,Korean,Norwegian,Polish,Portuguese,Russian,Spanish}]
                    [--translate {Chinese,Danish,Dutch,English,French,German,Greek,Italian,Japanese,Korean,Norwegian,Polish,Portuguese,Russian,Spanish}]
                    [--full | --official | --standard] [-c | -d | -l prefix suffix | -t | -x]

parse and process (tag, translate, link, encode/decode) Bible scripture references; see README for more
information

options:
  -h, --help            show this help message and exit
  -v                    show version and exit
  -q                    don't show errors
  -o out-file           output file (terminal output if not provided)
  --language {Chinese,Danish,Dutch,English,French,German,Greek,Italian,Japanese,Korean,Norwegian,Polish,Portuguese,Russian,Spanish}
                        indicate source language for book names (English if unspecified)
  --translate {Chinese,Danish,Dutch,English,French,German,Greek,Italian,Japanese,Korean,Norwegian,Polish,Portuguese,Russian,Spanish}
                        indicate output language for book names (same as source if unspecified)

data source (one required):
  choose between terminal or file input:

  -f in-file            get input from file (UTF-8)
  -r reference          process "reference; reference; etc."

output format (optional):
  if provided, book names will be rewritten accordingly:

  --full                output as full name - default (eg., "Genesis")
  --official            output as official abbreviation (eg., "Ge")
  --standard            output as standard abbreviation (eg., "Gen.")

type of conversion:
  if not specified, references are simply rewritten according to chosen (or default) output format:

  -c                    encode as BCV-notation ranges
  -d                    decode list of BCV-notation ranges
  -l prefix suffix      create <a href></a> links
  -t                    tag scriptures with {{ }}
  -x                    extract list of scripture references
```

Or, make it executable first and run directly:
```
$ chmod +x linkture.py
```

Some examples:
```
$ ./linkture.py -r "Joh 17:17; 2Ti 3:16, 17"
John 17:17; 2 Timothy 3:16, 17

$ ./linkture.py -r "Joh 17:17; 2Ti 3:16, 17" --standard
John 17:17; 2 Tim. 3:16, 17

$ /linkture.py -r "Joh 17:17; 2Ti 3:16, 17" --official
Joh 17:17; 2Ti 3:16, 17

$ ./linkture.py -r "Joh 17:17; 2Ti 3:16, 17" -c
[('43017017', '43017017'), ('55003016', '55003017')]

$ ./linkture.py -r "[('43017017', '43017017'), ('55003016', '55003017')]" -d --translate German
['Johannes 17:17', '2. Timotheus 3:16, 17']

$ ./linkture.py -r "Joh 17:17; 2Ti 3:16, 17" --translate Chinese
约翰福音 17:17; 提摩太后书 3:16, 17

$ ./linkture.py -r "Jean 17:17; 2 Timothée 3:16, 17" --language French --translate Spanish --standard
Juan 17:17; 2 Tim. 3:16, 17
```

Of course, you can pass a whole text file to parse and process using the `-f in_file` flag, instead of `-r "references"`. And you can output to another text file (instead of the terminal) using `-o out_file`.

Unless you use `-q`, ou will see in the terminal any errors encountered while parsing, such as unknow book names or out-of-range values. Of course, these entries will not be processed, but they will not affect the rest of the operation:
```
$ ./linkture.py -r "Mat 17:17; Paul 3:16, 17" --full
** "Paul 3:16, 17" - UNKNOWN BOOK: "Paul" **
Matthew 17:17; Paul 3:16, 17
```

## Script/import usage

```
from linkture import Scriptures

s = Scriptures(language="English", translate="Spanish", form="full")

url = s.link_scripture("John 17:3, 26")
codes = s.code_scripture("Psalm 83:18; Mt 6:9")
scriptures = s.decode_scripture([('43017017', '43017017'), ('55003016', '55003017')])
scriptures = s.rewrite_scripture("EXOD 3:15; Re 21:4")
```

Parameters:
* *language* - source language for Scripture parsing
  * Chinese, Danish, Dutch, English (default), French, German, Greek, Italian, Japanese, Korean, Norwegian, Polish, Portuguese, Russian, Spanish
* *translate* - language for Bible book name translation
  * Chinese, Danish, Dutch, English (default), French, German, Greek, Italian, Japanese, Korean, Norwegian, Polish, Portuguese, Russian, Spanish
* *form* - output format of Bible book names
  * **"full"** for full name format (eg., "Genesis")
  * **"standard"** for standard abbreviation format (eg., "Gen.")
  * **"official"** for official abbreviation format (eg., "Ge")
  * *None* or not supplied - no re-write will be performed

____
## Feedback

Feel free to [get in touch and post any issues and suggestions](https://github.com/erykjj/linkture/issues).
