#!/usr/bin/env python3

"""
  File:           linkture

  Description:    Parse and process Bible scripture references

  MIT License:    Copyright (c) 2025 Eryk J.

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
"""

__app__ = 'linkture'
__version__ = 'v3.2.5'


import json, regex, sqlite3
import pandas as pd
from pathlib import Path
from unidecode import unidecode


_available_languages = ('Cebuano', 'Chinese', 'Danish', 'Dutch', 'English', 'Ewe', 'French', 'German', 'Greek', 'Hungarian', 'Indonesian', 'Italian', 'Japanese', 'Korean', 'Norwegian', 'Polish', 'Portuguese', 'Romanian', 'Russian', 'Spanish', 'Swedish', 'Tagalog', 'Ukrainian')
_non_latin = ('Chinese', 'Greek', 'Japanese', 'Korean', 'Russian', 'Ukrainian')


class Scriptures():

    def __init__(self, language='English', translate=None, form=None, separator=' ', upper=False, verbose=False):
        self._verbose = verbose
        self._separator = separator
        if language not in _available_languages:
            raise ValueError("Indicated source language is not an option!")
        if translate:
            if translate not in _available_languages:
                raise ValueError("Indicated translation language is not an option!")
        else:
            translate = language
        if language in _non_latin:
            self._nl = True
        else:
            self._nl = False
        self._rewrite = bool((language != translate) or form)
        self._upper = upper
        if form == "full":
            form = 3
        elif form == "standard":
            form = 4
        elif form == "official":
            form = 5
        else:
            form = 3
        self._src_book_names = {}
        path = Path(__file__).resolve().parent

        self._tr_book_names = ['Bible']
        con = sqlite3.connect(path / 'res/resources.db')
        cur = con.cursor()
        for rec in cur.execute(f"SELECT * FROM Books WHERE Language = '{translate}';").fetchall():
            if self._upper:
                tr = rec[form].upper()
            else:
                tr = rec[form]
            self._tr_book_names.insert(rec[2], tr)
        for rec in cur.execute(f"SELECT * FROM Books WHERE Language = '{language}';").fetchall():
            for i in range(3,6):
                item = rec[i]
                if not self._nl:
                    item = unidecode(item)
                normalized = regex.sub(r'\p{P}|\p{Z}', '', item.upper())
                self._src_book_names[normalized] = rec[2]
        with open(path / 'res/custom.json', 'r', encoding='UTF-8') as json_file:
            b = json.load(json_file)
        if language in b.keys():
            for row in b[language]:
                names = row[1].split(', ')
                for item in names:
                    if not self._nl:
                        item = unidecode(item)
                    normalized = regex.sub(r'\p{P}|\p{Z}', '', item.upper())
                    self._src_book_names[normalized] = row[0]
        self._ranges = pd.read_sql_query("SELECT * FROM Ranges;", con)
        self._verses = pd.read_sql_query("SELECT * FROM Verses;", con)
        self._chapters = pd.read_sql_query("SELECT * FROM Chapters;", con)
        self._headings = (3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 92, 98, 100, 101, 102, 103, 108, 109, 110, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 138, 139, 140, 141, 142, 143, 144, 145)
        cur.close()
        con.close()
        self._reported = []
        self._encoded = {}
        self._linked = {}

        # Scripture reference parser:
        self._first_pass = regex.compile(r"""(
                {{.*?}}                              |

                (?:[1-5] (?:\p{Z}    |
                            \.\p{Z}? |
                            \p{Pd}   |
                            \p{L}{1,2} (?:\p{Z}     |
                                          \.\p{Z}?  |
                                          \p{Pd}))? |
                   [IV]{1,3} (?:\p{Z}    |
                                \.\p{Z}? |
                                \p{Pd})             )?
                (?!.*[\p{Pd}\.]{2})\p{L}[\p{L}\p{Pd}\.]+\p{Z}?
                (?:\d+\p{Z}?[:,\.\p{Pd};]\p{Z}?)*
                (?<=[\p{L},:\p{Pd}]\p{Z} |
                    [\p{L},:\p{Pd}]      |
                    \.)\d+
                (?![,\p{Pd}\p{L}])                  |

                (?:[1-5] (?:\p{Z}    |
                            \.\p{Z}? |
                            \p{Pd}   |
                            \p{L}{1,2} (?:\p{Z}     |
                                          \.\p{Z}?  |
                                          \p{Pd}))? |
                   [IV]{1,3} (?:\p{Z}    |
                                \.\p{Z}? |
                                \p{Pd})             )
                (?!.*[\p{Pd}\.]{2})\p{L}[\p{L}\p{Pd}\.]*\p{L}
            )""", flags=regex.VERBOSE | regex.IGNORECASE)

        self._second_pass = regex.compile(r"""(
                (?![^{]*}) # ignore already marked
                \p{L}[\p{L}\p{Pd}\.]+\p{Z}?
                (?:\d+\p{Z}?[:,\p{Pd};]\p{Z}?)*\d+
                (?![,\p{Pd}\p{L}])
            )""", flags=regex.VERBOSE)

        self._bk_ref = regex.compile(r"""
                ((?:[1-5]\p{L}{0,2} |
                    [IV]{1,3}         )?
                [\p{Pd}\.]?[\p{L}\p{Pd}\.\p{Z}]{2,})(.*)
            """, flags=regex.VERBOSE | regex.IGNORECASE)

        self._tagged = regex.compile(r'({{.*?}})')

        self._cv_cv = regex.compile(r'(\d+):(\d+)-(\d+):(\d+)')
        self._v_cv = regex.compile(r'(\d+)-(\d+):(\d+)')
        self._cv_v = regex.compile(r'(\d+):(\d+)-(\d+)')
        self._cv = regex.compile(r'(\d+):(\d+)')
        self._ddd = regex.compile(r'(\d+),(\d+),(\d+)')
        self._dd_d = regex.compile(r'(\d+),(\d+)-(\d+)')
        self._d_dd = regex.compile(r'(\d+)-(\d+),(\d+)')
        self._d_d = regex.compile(r'(\d+)-(\d+)(?!:)')
        self._dd = regex.compile(r'(\d+),(\d+)')
        self._d = regex.compile(r'(\d+)')

        self._chunk = regex.compile(r'([^,;\p{Z}]+.*)')
        self._sep = regex.compile(r'(?<!;)\s')

    def _error_report(self, scripture, message):
        if self._verbose and (scripture not in self._reported):
            print(f'** "{scripture}" - {message}')
            self._reported.append(scripture)

    def _scripture_parts(self, scripture):

        def check_book(bk_name):
            if not self._nl:
                bk_name = unidecode(bk_name) # NOTE: this converts Génesis to Genesis and English recognizes it !! Feature :-)
            bk_name = regex.sub(r'\p{P}|\p{Z}', '', bk_name.upper())
            if bk_name not in self._src_book_names:
                return None, 0
            else:
                bk_num = self._src_book_names[bk_name]
            return self._ranges.loc[(self._ranges.Book == bk_num) & (self._ranges.Chapter.isnull()), ['Book', 'Last']].values[0]

        reduced = regex.sub(r'\p{Z}', '', scripture)
        reduced = regex.sub(r'\p{Pd}', '-', reduced)
        result = self._bk_ref.search(reduced)
        if result:
            bk_name, rest = result.group(1).strip(), result.group(2).strip()
            bk_num, last = check_book(bk_name)
            if bk_num:
                tr_name = self._tr_book_names[bk_num]
                return tr_name, rest.replace('.', ':'), bk_num, last # for period notation cases (Gen 1.1)
        return None, None, None, 0

    def _locate_scriptures(self, text):

        def r(match):
            scripture = match.group(1)
            if regex.match(r'{{.*}}', scripture):
                tag = True
                scripture = scripture.strip('}{')
            else:
                tag = False
            if scripture in self._encoded.keys():
                return '{{' + scripture +'}}'
            _, rest, bk_num, last = self._scripture_parts(scripture)
            if bk_num:
                code = self._code_scripture(scripture, bk_num, rest, last) # validation performed
                if code:
                    self._encoded[scripture] = code
                    return '{{' + scripture +'}}'
            if tag:
                return '»»|' + scripture +'|««' # So as not to lose {{ }} on unrecognized pre-tagged scriptures (other language, etc.)
            else:
                return scripture

        self._reported = []
        text = regex.sub(self._first_pass, r, text)
        return regex.sub(self._second_pass, r, text)


    def list_scriptures(self, text):
        lst = []
        text = self._locate_scriptures(text)
        for scripture in regex.findall(self._tagged, text):
            script = scripture.strip('}{')
            if self._rewrite:
                script = self.decode_scriptures(self._encoded[script])[0]
            if self._upper:
                script = script.upper()
            lst.append(script)
        return lst

    def tag_scriptures(self, text):
        return self.rewrite_scriptures(text, True)

    def rewrite_scriptures(self, text, tag=False):

        def r(match):
            script = match.group(1).strip('}{')
            if self._rewrite:
                script = self.decode_scriptures(self._encoded[script])[0]
            if self._upper:
                script = script.upper()
            if tag:
                return '{{'+script+'}}'
            else:
                return script

        text = self._locate_scriptures(text)
        return regex.sub(self._tagged, r, text).replace('»»|', '{{').replace('|««', '}}')


    def _code_scripture(self, scripture, bk_num, rest, last):

        def reform_series(txt): # rewrite comma-separated consecutive sequences as (1, 2, 3) as ranges (1-3)
            for result in self._d_dd.finditer(txt, overlapped=True):
                    end = result.group(3)
                    mid = result.group(2)
                    start = result.group(1)
                    if int(end) - int(mid) == 1:
                        txt = regex.sub(result.group(), f"{start}-{end}", txt)
            for result in self._ddd.finditer(txt, overlapped=True):
                end = result.group(3)
                start = result.group(1)
                if int(end) - int(start) == 2:
                    txt = regex.sub(result.group(), f"{start}-{end}", txt)
            for result in self._ddd.finditer(txt, overlapped=True):
                end = result.group(3)
                start = result.group(1)
                if int(end) - int(start) == 2:
                    txt = regex.sub(result.group(), f"{start}-{end}", txt)
            for result in self._dd.finditer(txt, overlapped=True):
                    end = result.group(2)
                    start = result.group(1)
                    if int(end) - int(start) == 1:
                        txt = regex.sub(result.group(), f"{start}-{end}", txt)
            return txt

        def validate(b, ch, vs):
            c = int(ch)
            v = int(vs)
            if not (0 < b <= 66): # book out of range
                return None
            if not (0 < c <= self._ranges.loc[(self._ranges.Book == b) & (self._ranges.Chapter.isnull()), ['Last']].values[0]): # chapter out of range
                return None
            if not (0 < v <= self._ranges.loc[(self._ranges.Book == b) & (self._ranges.Chapter == c), ['Last']].values[0]): # verse out of range
                return None
            return True

        def code_verses(chunk, book, multi):
            b = str(book).zfill(2)

            result = self._cv_cv.search(chunk)
            if result:
                c = result.group(1)
                v = result.group(2)
                if not validate(book, c, v):
                    return None, 0
                ch1 = c.zfill(3)
                v1 = v.zfill(3)

                c = result.group(3)
                v = result.group(4)
                if not validate(book, c, v):
                    return None, 0
                ch2 = c.zfill(3)
                v2 = v.zfill(3)
                return (b+ch1+v1, b+ch2+v2), ch2

            result = self._cv_v.search(chunk)
            if result:
                c = result.group(1)
                v = result.group(2)
                if not validate(book, c, v):
                    return None, 0
                ch1 = c.zfill(3)
                v1 = v.zfill(3)

                v = result.group(3)
                if not validate(book, c, v):
                    return None, 0
                v2 = v.zfill(3)
                return (b+ch1+v1, b+ch1+v2), ch1

            result = self._v_cv.search(chunk)
            if result:
                c = str(ch)
                v = result.group(1)
                if not validate(book, c, v):
                    return None, 0
                ch1 = c
                v1 = v.zfill(3)

                c = result.group(2)
                v = result.group(3)
                if not validate(book, c, v):
                    return None, 0
                ch2 = c.zfill(3)
                v2 = v.zfill(3)
                return (b+ch1+v1, b+ch2+v2), ch2

            result = self._cv.search(chunk)
            if result:
                c = result.group(1)
                v = result.group(2)
                if not validate(book, c, v):
                    return None, 0
                ch1 = c.zfill(3)
                v1 = v.zfill(3)
                return (b+ch1+v1, b+ch1+v1), ch1

            result = self._d_d.search(chunk)
            if result:
                if multi:
                    c = result.group(1)
                    v = 1
                    if not validate(book, c, v):
                        return None, 0
                    ch1 = c.zfill(3)
                    if book == 19 and int(c) in self._headings: # some chapters start at verse 0
                        v1 = '000'
                    else:
                        v1 = '001'

                    c = result.group(2)
                    if not validate(book, c, v):
                        return None, 0
                    ch2 = c.zfill(3)
                    v2 = str(self._ranges.loc[(self._ranges.Book == book) & (self._ranges.Chapter == int(ch2)), ['Last']].values[0][0]).zfill(3)
                    return (b+ch1+v1, b+ch2+v2), None
                else:
                    c = 1
                    v = result.group(1)
                    if not validate(book, c, v):
                        return None, 0
                    ch1 = '001'
                    v1 = v.zfill(3)

                    v = result.group(2)
                    if not validate(book, c, v):
                        return None, 0
                    ch2 = ch1
                    v2 = v.zfill(3)
                    return (b+ch1+v1, b+ch2+v2), ch2

            result = self._d.search(chunk)
            if result:
                if multi:
                    c = result.group(1)
                    v = 1
                    if not validate(book, c, v):
                        return None, 0
                    ch1 = c.zfill(3)
                    if book == 19 and int(c) in self._headings: # some chapters start at verse 0
                        v1 = '000'
                    else:
                        v1 = '001'
                    v2 = str(self._ranges.loc[(self._ranges.Book == book) & (self._ranges.Chapter == int(ch1)), ['Last']].values[0][0]).zfill(3)
                    return (b+ch1+v1, b+ch1+v2), None
                else:
                    c = 1
                    v = result.group(1)
                    if not validate(book, c, v):
                        return None, 0
                    ch1 = '001'
                    v1 = v.zfill(3)
                return (b+ch1+v1, b+ch1+v1), None

            return None, None

        lst = []
        if rest == '': # whole book
            v = self._ranges.loc[(self._ranges.Book == bk_num) & (self._ranges.Chapter == last), ['Last']].values[0][0]
            if last == 1:
                rest = f'1-{v}'
            else:
                rest = f'1:1-{last}:{v}'
        else:
            rest = reform_series(rest)
        for chunk in rest.split(';'):
            ch = None
            for bit in chunk.split(','):
                if ch:
                    tup, ch = code_verses(f"{ch}:{bit}", bk_num, last>1)
                else:
                    tup, ch = code_verses(bit, bk_num, last>1)
                if not tup:
                    self._error_report(scripture, f'"{bit.strip()}" OUT OF RANGE')
                    return None
                lst.append(tup)
        return lst

    def code_scriptures(self, text):
        text = self._locate_scriptures(text)
        lst = []
        for scripture in regex.findall(self._tagged, text):
            bcv_ranges = self._encoded[scripture.strip('}{')]
            for bcv_range in bcv_ranges:
                lst.append(bcv_range)
        return lst


    def _decode_scripture(self, bcv_range, book='', chap=0, sep=';'):
        if not bcv_range:
            return None, '', 0, False
        start, end = bcv_range
        sb = int(start[:2])
        sc = int(start[2:5])
        sv = int(start[5:])
        eb = int(end[:2])
        ec = int(end[2:5])
        ev = int(end[5:])

        if not (sb == eb):
            return None, '', 0, False
        if not ((0 < sb <= 66) & (sb == eb)): # book out of range
            return None, '', 0, False
        lc = self._ranges.loc[(self._ranges.Book == sb) & (self._ranges.Chapter.isnull()), ['Last']].values[0][0]
        if not (0 < sc <= ec <= lc): # chapter(s) out of range
            return None, '', 0, False
        se = self._ranges.loc[(self._ranges.Book == sb) & (self._ranges.Chapter == sc), ['Last']].values[0][0]
        le = self._ranges.loc[(self._ranges.Book == sb) & (self._ranges.Chapter == ec), ['Last']].values[0][0]
        minsv = minev = 1
        if sb == 19:
            if sc in self._headings: # some chapters start at verse 0
                minsv = 0
            if ec in self._headings:
                minev = 0
        if not ((minsv <= sv <= se) & (minev <= ev <= le)): # verse(s) out of range
            return None, '', 0, False
        bk_name = self._tr_book_names[sb]
        if book == bk_name:
            cont = True
        else:
            cont = False
            book = bk_name
        c = ec - sc + 1
        v = ev - sv + 1
        if lc == 1:
            if cont:
                bk_name = ','
            if v == le:
                scripture = f"{bk_name.strip(',')}"
            elif v == 1:
                scripture = f"{bk_name} {sv}"
            elif v == 2:
                scripture = f"{bk_name} {sv}, {ev}"
            else:
                scripture = f"{bk_name} {sv}‑{ev}"
            sep = ';'
        else:
            ch = f"{sc}:"
            if v == le:
                if cont:
                    bk_name = sep
                if c == lc:
                    scripture = f"{bk_name.strip(',')}"
                elif c == 1:
                    scripture = f"{bk_name} {sc}"
                elif c == 2:
                    scripture = f"{bk_name} {sc}, {ec}"
                else:
                    scripture = f"{bk_name} {sc}‑{ec}"
                sep = ','
            elif c == 1:
                if cont:
                    if sc == chap:
                        bk_name = ''
                        ch = ', '
                    else:
                        bk_name = ';'
                if v == 1:
                    scripture = f"{bk_name} {ch}{sv}"
                elif v == 2:
                    scripture = f"{bk_name} {ch}{sv}, {ev}"
                else:
                    scripture = f"{bk_name} {ch}{sv}‑{ev}"
                sep = ';'
            else:
                if cont and (sc == chap):
                    bk_name = ''
                    ch = ', '
                scripture = f"{bk_name} {ch}{sv}‑{ec}:{ev}"
                sep = ';'
        chap = ec
        if self._separator != ' ':
            scripture = regex.sub(self._sep, self._separator, scripture)
        return scripture.strip(), book, chap, cont, sep

    def decode_scriptures(self, bcv_ranges=[]):
        try:
            scriptures = []
            bk = ''
            ch = 0
            sep = ';'
            for bcv_range in bcv_ranges:
                scripture, bk, ch, cont, sep = self._decode_scripture(bcv_range, bk, ch, sep)
                if scripture:
                    if cont:
                        scriptures[-1] = scriptures[-1] + scripture
                    else:
                        scriptures.append(scripture)
            return scriptures
        except:
            return None


    def link_scriptures(self, text, prefix='<a href=', suffix='>'):
        # this always rewrites (full by default); if rewrite not desired, get code the scripture and build your own link

        def convert_range(bcv_range):
            if not bcv_range:
                return None, None
            start, end = bcv_range
            sb = int(start[:2])
            sc = int(start[2:5])
            sv = int(start[5:])
            eb = int(end[:2])
            ec = int(end[2:5])
            ev = int(end[5:])
            if start == end:
                return f"{sb}:{sc}:{sv}"
            else:
                return f"{sb}:{sc}:{sv}-{eb}:{ec}:{ev}"

        def r1(match):

            def r2(match):
                return f'{prefix}{lnk}{suffix}{match.group(1)}</a>'

            scripture = match.group(1).strip('}{')
            if scripture in self._linked.keys():
                return self._linked[scripture]
            output = ''
            bk = ''
            ch = 0
            sep = ';'
            for bcv_range in self._encoded[scripture]:
                scrip, bk, ch, _, sep = self._decode_scripture(bcv_range, bk, ch, sep)
                lnk = convert_range(bcv_range)
                output += regex.sub(self._chunk, r2, scrip)
            self._linked[scripture] = output.strip(' ;,')
            if self._upper:
                output = output.upper()
            return output.strip(' ;,')

        text = self._locate_scriptures(text)
        return regex.sub(self._tagged, r1, text).replace('»»|', '{{').replace('|««', '}}')


    def book_name(self, num):
        try:
            return self._tr_book_names[int(num)]
        except:
            self._error_report(num, 'OUT OF RANGE')
            return None

    def serial_chapter_number(self, bcv):
        try:
            return int(self._chapters.loc[(self._chapters['Book'] == int(bcv[0:2])) & (self._chapters['Chapter'] == int(bcv[2:5]))].values[0][0])
        except:
            self._error_report(bcv, 'OUT OF RANGE')
            return None

    def serial_verse_number(self, bcv):
        try:
            return int(self._verses.loc[(self._verses['Book'] == int(bcv[0:2])) & (self._verses['Chapter'] == int(bcv[2:5])) & (self._verses['Verse'] == int(bcv[5:]))].values[0][0]) + 1
        except:
            self._error_report(bcv, 'OUT OF RANGE')
            return None

    def code_chapter(self, chapter):
        try:
            book, chapter = self._chapters[self._chapters['ChapterId'] == int(chapter)].values[0][1:]
            last = self._ranges.loc[(self._ranges.Book == book) & (self._ranges.Chapter == chapter), ['Last']].values[0][0]
            bc = str(book).zfill(2) + str(chapter).zfill(3)
            if book == 19 and chapter in self._headings: # some chapters start at verse 0
                v = '000'
            else:
                v = '001'
            return f"('{bc}{v}', '{bc}{str(last).zfill(3)}')"
        except:
            self._error_report(chapter, 'OUT OF RANGE')
            return None

    def code_verse(self, verse):
        bcv = ''
        try:
            for i in self._verses[self._verses['VerseId'] == int(verse)-1].values[0][1:]:
                bcv += str(i).zfill(3)
            return f"('{bcv[1:]}', '{bcv[1:]}')"
        except:
            self._error_report(verse, 'OUT OF RANGE')
            return None
