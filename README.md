# linkture


## Purpose

This module contains functions to parse and process Bible scripture references.

The parser can work in **Cebuano, Chinese, Danish, Dutch, English, French, German, Greek, Italian, Japanese, Korean, Norwegian, Polish, Portuguese, Russian, Spanish and Tagalog**. It will **recognize** such references and **validate** them to ensure the chapter(s) and/or verse(s) are within range.

It *does not* work with whole books (like "James") unless they are preceded by a number (like "1 John"); otherwise it would have to look up ever single word. Also, it will *not* find the multi-word book name "Song of Solomon" (and its variations), though this (and any other scripture) can be force-detected by tagging the desired reference "manually" within the source text (eg., "{{Song of Solomon 1:1}}") - *one book* per brace pair. These two limitations aside, it works with most book name variants in all the available languages (including common abbreviations): "2 Sam.", "2nd Samuel", "II Samuel", "2Sa", etc. Any special/unusual variants can be added to the *res/custom.json* list.

These found references can be **extracted** as a list of references, or a list of BCV-encoded ranges in the format `bbcccvvv` (where `b` is book, `c` is chapter, and `v` is verse). Or, they can be **tagged** (with '{{ }}') within the text, or replaced with HTML \<a> **links** (with custom prefix and suffix). All of these functions can also include a **rewrite** of the reference with either a full book name, or one of two abbreviation formats, along with **translation** into one of the available languages.

The parser tries to deal "intelligently" with different notations, but there are simply too many "edge-cases". If something isn't being parsed properly, try to rewrite the original reference(s) in a standard way or use {{ }} to force the detection.

A couple of auxiliary functions provide a verse number lookup (either by BCV reference or integer). These can be useful to calculate the number of verses between two references, etc.

____
## Installation

Download [latest source](https://github.com/erykjj/linkture/releases/latest) and `python3 -m pip install linkture-*.tar.gz`.

____
## Command-line usage

```
> python3 linkture.py -h
usage: linkture.py [-h] [-v] [-q] [-f in-file | -r reference] [-o out-file]
                   [--language {Chinese,Danish,Dutch,English,French,German,Greek,Italian,Japanese,Korean,Norwegian,Polish,Portuguese,Russian,Spanish}]
                   [--translate {Chinese,Danish,Dutch,English,French,German,Greek,Italian,Japanese,Korean,Norwegian,Polish,Portuguese,Russian,Spanish}]
                   [-u] [--full | --official | --standard]
                   [-c | -d | -l [prefix [suffix ...]] | -t | -x]
                   [-sc BCV | -sv BCV | -cc chapter | -cv verse]

PARSE and PROCESS BIBLE SCRIPTURE REFERENCES: extract, tag, link, rewrite, translate, BCV-encode and decode.
See README for more information

options:
  -h, --help            show this help message and exit
  -v                    show version and exit
  -q                    don't show errors
  -o out-file           output file (terminal output if not provided)
  --language {Chinese,Danish,Dutch,English,French,German,Greek,Italian,Japanese,Korean,Norwegian,Polish,Portuguese,Russian,Spanish}
                        indicate source language for book names (English if unspecified)
  --translate {Chinese,Danish,Dutch,English,French,German,Greek,Italian,Japanese,Korean,Norwegian,Polish,Portuguese,Russian,Spanish}
                        indicate output language for book names (same as source if unspecified)
  -u                    capitalize (upper-case) book names

data source (one required - except for auxiliary functions, which only take command-line arguments):
  choose between terminal or file input:

  -f in-file            get input from file (UTF-8)
  -r reference          process "reference; reference; etc."

output format (optional):
  if provided, book names will be rewritten accordingly:

  --full                output as full name  -  default (eg., "Genesis")
  --official            output as official abbreviation (eg., "Ge")
  --standard            output as standard abbreviation (eg., "Gen.")

type of conversion:
  if not specified, references are simply rewritten according to chosen (or default) output format:

  -c                    encode as BCV-notation ranges
  -d                    decode list of BCV-notation ranges
  -l [prefix [suffix ...]]
                        create <a></a> links; provide a "prefix" and a "suffix" (or neither for testing)
  -t                    tag scriptures with {{ }}
  -x                    extract list of scripture references

auxiliary functions:
  -sc BCV               return the serial number (1-1189) of the chapter with code "BCV" ("bbcccvvv")
  -sv BCV               return the serial number (1-31078) of the verse with code "BCV" ("bbcccvvv")
  -cc chapter           return the BCV range for serial chapter number "chapter" (integer value)
  -cv verse             return the BCV code for serial verse number "verse" (integer value)
```

Or, make it executable first and run directly:
```
$ chmod +x linkture.py
```

Some examples:
```
$ ./linkture.py -r "Joh 17:17; 2Ti 3:16, 17" --full -u
JOHN 17:17; 2 TIMOTHY 3:16, 17

$ ./linkture.py -r "Joh 17:17; 2Ti 3:16, 17" --standard
John 17:17; 2 Tim. 3:16, 17

$ ./linkture.py -r "Joh 17:17; 2Ti 3:16, 17" --official
Joh 17:17; 2Ti 3:16, 17

$ ./linkture.py -r "Joh 17:17; 2Ti 3:16, 17" -c
[('43017017', '43017017'), ('55003016', '55003017')]

$ ./linkture.py -r "[('43017017', '43017017'), ('55003016', '55003017')]" -d --translate German
['Johannes 17:17', '2. Timotheus 3:16, 17']

$ ./linkture.py -r "Joh 17:17; 2Ti 3:16, 17" -l '<a href="https://my.website.com/' '/index.html" class="test">'
<a href="https://my.website.com/43:17:17/index.html" class="test">John 17:17</a>; <a href="https://my.website.com/55:3:16-55:3:17/index.html" class="test">2 Timothy 3:16, 17</a>

$ ./linkture.py -r "Joh 17:17; 2Ti 3:16, 17" --translate Chinese
约翰福音 17:17; 提摩太后书 3:16, 17

$ ./linkture.py -r "约翰福音 17:17; 提摩太后书 3:16, 17" --language Chinese --translate Dutch
Johannes 17:17; 2 Timotheüs 3:16, 17

$ ./linkture.py -r "{{Jean 17:17}}; 2 Timothée 3:16, 17" --language French --translate Spanish --standard
Juan 17:17; 2 Tim. 3:16, 17

$ ./linkture.py -r "Mat 17:17; Paul 3:16, 17" --full -x
['Matthew 17:17']

$ ./linkture.py -cc 2
('01002001', '01002025')

$ ./linkture.py -cv 31078
('66022021', '66022021')

$ ./linkture.py -sv '01001001'
1

./linkture.py -sc '66022001'
1189
```

Of course, you can pass a whole text file to parse and process using the `-f in_file` flag, instead of `-r "references"`. And you can output to another text file (instead of the terminal) using `-o out_file`.

Unless you use `-q`, you will see in the terminal any out-of-range errors encountered while parsing. Of course, these entries will not be processed, but they will not affect the rest of the operation.

## Script/import usage

Assume the text (short string or long document) you want to process is in the variable `txt`. It's in English, but you would like the scriptures to be in Spanish, with the full book name:
```
from linkture import Scriptures

s = Scriptures(language="English", translate="Spanish", form="full")

lst = s.list_scriptures(txt)
# returns a list of (valid) extracted scriptures in the desired language and format

lst = s.code_scriptures(txt)
# returns a list of BCV-range tuples (start, end)

html = s.link_scriptures(txt, prefix='<a href="http://mywebsite.com/', suffix='" class="b"')
# this will turn all references into HTML links

tagged = s.tag_scriptures(txt)
# tagged will contain your document with the translated references enclosed within double braces

txt = s.rewrite_scriptures(txt)
# the references will simply be rewritten in the desired language and format

i = s.serial_chapter_number(txt)
# returns the serial number (1-1189) of the chapter identified by the provided BCV-format string; verse digits irrelevant

i = s.serial_verse_number(txt)
# returns the serial number (1-31078) of the verse identified by the provided BCV-format string

txt = s.code_chapter(i)
# returns a BCV-format range string for the whole chapter indicated by the provided integer (1-1189)

txt = s.code_verse(i)
# returns a BCV-format range string for the verse indicated by the provided integer (1-31078)
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
  * *None* or not supplied - no re-write will be performed, *unless* translation is performed or *linking* (in which case, "full" is the default)
* *upper* - if **True**, outputs book names in UPPER CASE (**False** by default)
* *verbose* - if **True**, show (in terminal) any out-of-range errors encountered while parsing (**False** by default)

____
## Feedback

Feel free to [get in touch and post any issues and suggestions](https://github.com/erykjj/linkture/issues).

[![RSS of releases](res/rss-36.png)](https://github.com/erykjj/linkture/releases.atom)
