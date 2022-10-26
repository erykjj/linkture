# linkture


## Purpose

Functions to convert Bible scripture references to a list of coded (non-contiguous) ranges (and vice-versa) or to HTML \<href> links (specifically for use in *jwpub* archives, but these can be easily modified as needed). The ranges are in the format `bbcccvvv`, where `b` is book, `c` is chapter, and `v` is verse.

**Note** that this script _does not_ parse text files for scriptures - it only parses what is enclosed within `{{ }}`, or provided as a string argument. Also, it doesn't check if chapters or verses are within range (actually exist). Make sure the scriptures use common English names/abbreviations, though the *books.json* list can be modified for other languages.

____
## Usage

```
python3 linkture.py [-h] [-v] [-l] [-q]
                   [--language {English,Spanish,German,French,Italian,Portuguese}]
                   (-s reference | -f in-file out-file)

options:
  -h, --help            show this help message and exit
  -l, --link            Create links (instead of range list)
  --language {English,Spanish,German,French,Italian,Portuguese}
                        Indicate language of book names
                        (English if unspecified)
  -s reference          Work with STDIN
  -f in-file out-file   Work with files
  -v, --version         Show version and exit
  -q, --quiet           Don't show processing status
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
scriptures = s.decode_scripture([('43017017', '43017017'), ('55003016', '55003017')])
```
____
## Sample output

An input file containing this:
```
Some random text {{Mark 1:1 - 2:2; Jude 4}} surrounding your scripture reference.
Here is another line ({{2 John 2-5; John 17:3-26; 18:1}}).
{{3 John 2}}
{{Lev2:3-5, 7-9}}
{{2 John}}
{{3-John 3,4}}
{{James; Acts 10:1, 3, 5}}
{{1 Timothy 6}}
{{1Timothy 3-4}}
{{1 Timothy 2:2-3:3; Mark 10:37-10:52; 11:1; 12:1}}
{{1 Timothy 1, 3}}
The end.
```

Results in this:
```
Some random text <a href="jwpub://b/NWTR/41:1:1-41:2:2" class="b">Mark 1:1 - 2:2</a>; <a href="jwpub://b/NWTR/65:1:4" class="b">Jude 4</a> surrounding your scripture reference.
Here is another line (<a href="jwpub://b/NWTR/63:1:2-63:1:5" class="b">2 John 2-5</a>; <a href="jwpub://b/NWTR/43:17:3-43:17:26" class="b">John 17:3-26</a>; <a href="jwpub://b/NWTR/43:18:1" class="b">18:1</a>).
<a href="jwpub://b/NWTR/64:1:2" class="b">3 John 2</a>
<a href="jwpub://b/NWTR/3:2:3-3:2:5" class="b">Lev 2:3-5</a>, <a href="jwpub://b/NWTR/3:2:7-3:2:9" class="b">7-9</a>
<a href="jwpub://b/NWTR/63:1:1-63:1:13" class="b">2 John</a>
<a href="jwpub://b/NWTR/64:1:3-64:1:4" class="b">3-John 3, 4</a>
<a href="jwpub://b/NWTR/59:1:1-59:5:20" class="b">James</a>; <a href="jwpub://b/NWTR/44:10:1" class="b">Acts 10:1</a>, <a href="jwpub://b/NWTR/44:10:3" class="b">3</a>, <a href="jwpub://b/NWTR/44:10:5" class="b">5</a>
<a href="jwpub://b/NWTR/54:6:1-54:6:21" class="b">1 Timothy 6</a>
<a href="jwpub://b/NWTR/54:3:1-54:4:16" class="b">1Timothy 3, 4</a>
<a href="jwpub://b/NWTR/54:2:2-54:3:3" class="b">1 Timothy 2:2-3:3</a>; <a href="jwpub://b/NWTR/41:10:37-41:10:52" class="b">Mark 10:37-52</a>; <a href="jwpub://b/NWTR/41:11:1" class="b">11:1</a>; <a href="jwpub://b/NWTR/41:12:1" class="b">12:1</a>
<a href="jwpub://b/NWTR/54:1:1-54:1:20" class="b">1 Timothy 1</a>; <a href="jwpub://b/NWTR/54:3:1-54:3:16" class="b">3</a>
The end.
```

And this:
```
Some random text [('41001001', '41002002'), ('65001004', '65001004')] surrounding your scripture reference.
Here is another line ([('63001002', '63001005'), ('43017003', '43017026'), ('43018001', '43018001')]).
[('64001002', '64001002')]
[('03002003', '03002005'), ('03002007', '03002009')]
[('63001001', '63001013')]
[('64001003', '64001004')]
[('59001001', '59005020'), ('44010001', '44010001'), ('44010003', '44010003'), ('44010005', '44010005')]
[('54006001', '54006021')]
[('54003001', '54004016')]
[('54002002', '54003003'), ('41010037', '41010052'), ('41011001', '41011001'), ('41012001', '41012001')]
[('54001001', '54001020'), ('54003001', '54003016')]
The end.
```
____
## Feedback

Feel free to [get in touch and post any issues and suggestions](https://github.com/erykjj/linkture/issues).
