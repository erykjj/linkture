# linkture


## Purpose

Functions to convert Bible scripture references to a list of coded (non-contiguous) ranges or to HTML \<href> links (specifically for use in .jwpub archives, but these can be easily modified as needed). The ranges are in the format `bbcccvvv`, where `b` is book, `c` is chapter, and `v` is verse.

**Note** that this script _does not_ parse text files for scriptures - it only parses what is enclosed within `{{ }}`, or provided as a string argument. Also, it doesn't check if chapters or verses are within range (actually exist). Make sure the scriptures use common English names/abbreviations, though the *books.json* list can be modified for other languages.

____
## Usage

```
python3 linkture.py [-h] [-l] (-s reference | -f in-file out-file) [-v] [-q]

options:
  -h, --help           show this help message and exit
  -l, --link           Create links (instead of range list)
  -s reference         Work with STDIN
  -f in-file out-file  Work with files
  -v, --version        Show version and exit
  -q, --quiet          Don't show processing status
```

Or, make it executable first and run directly:
```
$ chmod u+x linkture.py
$ ./linkture.py -s "Joh 17:17; 2Ti 3:16, 17"
...Processing "Joh 17:17; 2Ti 3:16, 17"
[('43017017', '43017017'), ('55003016', '55003017')]
```

Or import it into your script:
```
from linkture import Scriptures

s = Scriptures()
url = s.link_scripture("John 17:3, 26")
codes = s.code_scripture("Psalm 83:18; Mt 6:9")
```
____
## Sample output

```
Mark 1:1 - 2:2 --> [('41001001', '41002002')]
2 John 2-5 --> [('63001002', '63001005')]
3 John 2 --> [('64001002', '64001002')]
Lev2:3-5, 7-9 --> [('03002003', '03002005'), ('03002007', '03002009')]
2 John --> [('63001001', '63001013')]
3-John 3,4 --> [('43003001', '43004054')]
James --> [('59001001', '59005020')]
1 Timothy 6 --> [('54006001', '54006021')]
1Timothy 3-4 --> [('54003001', '54004016')]
1 Timothy 2:2-3:3 --> [('54002002', '54003003')]
1 Timothy 1, 3 --> [('54001001', '54001020'), ('54003001', '54003016')]
```
