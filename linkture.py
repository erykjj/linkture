#!/usr/bin/env python3

"""
  File:           linkture

  Description:    Parse and process Bible scripture references

  MIT License:    Copyright (c) 2023 Eryk J.

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

VERSION = '2.2.0'


import argparse, json, regex, sqlite3
import pandas as pd

from ast import literal_eval
from pathlib import Path


available_languages = ('Chinese', 'Danish', 'Dutch', 'English', 'French', 'German', 'Greek', 'Italian', 'Japanese', 'Korean', 'Norwegian', 'Polish', 'Portuguese', 'Russian', 'Spanish')


class Scriptures():

    def __init__(self, language='English', translate=None, form=None, upper=False, verbose=False):
        self._verbose = verbose
        if language not in available_languages:
            raise ValueError("Indicated source language is not an option!")
        if translate:
            if translate not in available_languages:
                raise ValueError("Indicated translation language is not an option!")
        else:
            translate = language
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
                normalized = regex.sub(r'\p{P}|\p{Z}', '', rec[i].upper())
                self._src_book_names[normalized] = rec[2]
        with open(path / 'res/custom.json', 'r', encoding='UTF-8') as json_file:
            b = json.load(json_file)
        if language in b.keys():
            for row in b[language]:
                names = row[1].split(', ')
                for item in names:
                    normalized = regex.sub(r'\p{P}|\p{Z}', '', item.upper())
                    self._src_book_names[normalized] = row[0]
        self._ranges = pd.read_sql_query("SELECT * FROM Ranges;", con)
        cur.close()
        con.close()
        self._reported = []

        # Scripture reference parser:
        self._first_pass = regex.compile(r"""(
                (?![^{]*}) # ignore already marked

                (?:[1-5] (?:\p{Z}    |
                            \.\p{Z}? |
                            \p{Pd}   |
                            \p{L}{1,2} (?:\p{Z}     |
                                          \.\p{Z}?  |
                                          \p{Pd}))? |
                   [IV]{1,3} (?:\p{Z}    |
                                \.\p{Z}? |
                                \p{Pd})             )?
                \p{L}[\p{L}\p{Pd}\.]+\p{Z}?
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
                \p{L}[\p{L}\p{Pd}\.]*\p{L}
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
        self._pretagged = regex.compile(r'{{(.*?)}}')

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

    def _error_report(self, scripture, message):
        if self._verbose and (scripture not in self._reported):
            print(f'** "{scripture}" - {message}')
            self._reported.append(scripture)

    def _locate_scriptures(self, text):

        def rewrite_scripture(rest=''):

            def reform_series(txt): # rewrite comma-separated consecutive sequences as (1, 2, 3) as ranges (1-3) and consecutive ranges (1-2) as comma-separated sequences (1, 2)
                found = True
                while found:
                    found = False
                    for result in self._ddd.finditer(txt):
                        end = result.group(3)
                        start = result.group(1)
                        if int(end) - int(start) == 2:
                            found = True
                            txt = regex.sub(result.group(), f"{start}-{end}", txt)
                    for result in self._d_dd.finditer(txt):
                        end = result.group(3)
                        mid = result.group(2)
                        start = result.group(1)
                        if int(end) - int(mid) == 1:
                            found = True
                            txt = regex.sub(result.group(), f"{start}-{end}", txt)
                    for result in self._dd_d.finditer(txt):
                        end = result.group(3)
                        mid = result.group(2)
                        start = result.group(1)
                        if int(mid) - int(start) == 1:
                            found = True
                            txt = regex.sub(result.group(), f"{start}-{end}", txt)
                    for result in self._d_d.finditer(txt):
                        end = result.group(2)
                        start = result.group(1)
                        if int(end) - int(start) == 1:
                            found = True
                            txt = regex.sub(result.group(), f"{start},{end}", txt)
                    for result in self._cv_cv.finditer(txt):
                        sc = result.group(1)
                        sv = result.group(2)
                        ec = result.group(3)
                        ev = result.group(4)
                        if int(sc) == int(ec):
                            found = True
                            txt = regex.sub(result.group(), f"{sc}:{sv}-{ev}", txt)
                return txt

            output = ''
            for chunk in rest.split(';'):
                chunk = reform_series(chunk)
                output += chunk.strip()+'; '
            return output.strip(';, ')

        def scripture_parts(scripture):

            def check_book(bk_name):
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
                    script = rewrite_scripture(rest)
                    return tr_name, script.replace('.', ':'), bk_num, last # for period notation cases (Gen 1.1)
            return None, None, None, 0

        def r(match):
            scripture = match.group(1)
            tr_name, script, bk_num, last = scripture_parts(scripture)
            if bk_num and tr_name:
                code = self._code_scripture(scripture, bk_num, script, last)
                if code:
                    if self._upper:
                        tr_name = tr_name.upper()
                    return '{{' +f'{scripture}|{tr_name}|{script}|{bk_num}|{last}' +'}}'
            return scripture

        self._reported = []
        text = regex.sub(self._pretagged, r, text)
        text = regex.sub(self._first_pass, r, text)
        return regex.sub(self._second_pass, r, text)


    def list_scriptures(self, text):
        lst = []
        text = self._locate_scriptures(text)
        for scripture in regex.findall(self._tagged, text):
            script, tr_name, rest, _, _ = scripture.strip('}{').split('|')
            if self._rewrite:
                if rest:
                    lst.append(tr_name+' '+rest.replace(',', ', '))
                else:
                    lst.append(tr_name)
            else:
                lst.append(script)
        return lst

    def tag_scriptures(self, text):

        def r(match):
            script, tr_name, rest, _, _ = match.group(1).strip('}{').split('|')
            if self._rewrite:
                if rest:
                    return '{{'+tr_name+' '+rest.replace(',', ', ')+'}}'
                else:
                    return '{{'+tr_name+'}}'
            else:
                return '{{'+script+'}}'

        text = self._locate_scriptures(text)
        return regex.sub(self._tagged, r, text)


    def _code_scripture(self, scripture, bk_num, rest, last):

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
        rest = rest or ''
        if rest == '': # whole book
            v = self._ranges.loc[(self._ranges.Book == bk_num) & (self._ranges.Chapter == last), ['Last']].values[0][0]
            if last == 1:
                rest = f'1-{v}'
            else:
                rest = f'1:1-{last}:{v}'
        for result in regex.finditer(self._dd, rest, overlapped=True):
            if int(result.group(2)) - int(result.group(1)) == 1:
                rest = regex.sub(result.group(), f'{result.group(1)}-{result.group(2)}', rest)
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
            script, _, rest, bk_num, last = scripture.strip('}{').split('|')
            bcv_ranges = self._code_scripture(script, int(bk_num), rest, int(last)) or []
            for bcv_range in bcv_ranges:
                lst.append(bcv_range)
        return lst


    def _decode_scripture(self, bcv_range, book='', chap=0):
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
        if not ((0 < sv <= se) & (0 < ev <= le)): # verse(s) out of range
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
                scripture = f"{bk_name} {sv}-{ev}"
        else:
            ch = f"{sc}:"
            if cont:
                bk_name = ','
            if v == le:
                if cont:
                    bk_name = ','
                if c == lc:
                    scripture = f"{bk_name.strip(',')}"
                elif c == 1:
                    scripture = f"{bk_name} {sc}"
                elif c == 2:
                    scripture = f"{bk_name} {sc}, {ec}"
                else:
                    scripture = f"{bk_name} {sc}-{ec}"
            elif c == 1:
                if cont:
                    if sc == chap:
                        bk_name = ''
                        ch = ', '
                    else:
                        bk_name = '; '
                if v == 1:
                    scripture = f"{bk_name} {ch}{sv}"
                elif v == 2:
                    scripture = f"{bk_name} {ch}{sv}, {ev}"
                else:
                    scripture = f"{bk_name} {ch}{sv}-{ev}"
            else:
                if cont and (sc == chap):
                    bk_name = ''
                    ch = ', '
                scripture = f"{bk_name} {ch}{sv}-{ec}:{ev}"
        chap = ec
        return scripture.strip(), book, chap, cont

    def decode_scriptures(self, bcv_ranges=[]):
        scriptures = []
        bk = ''
        ch = 0
        for bcv_range in bcv_ranges:
            scripture, bk, ch, cont = self._decode_scripture(bcv_range, bk, ch)
            if scripture:
                if cont:
                    scriptures[-1] = scriptures[-1] + scripture
                else:
                    scriptures.append(scripture)
        return scriptures


    def link_scriptures(self, text, prefix='<a href="https://', suffix='>'):

        def process_verses(chunk, book, multi):
            b = str(book)

            result = self._cv_cv.search(chunk)
            if result:
                ch1 = result.group(1)
                v1 = result.group(2)
                ch2 = result.group(3)
                v2 = result.group(4)
                return f"{b}:{ch1}:{v1}-{b}:{ch2}:{v2}", ch2

            result = self._cv_v.search(chunk)
            if result:
                ch1 = result.group(1)
                v1 = result.group(2)
                ch2 = ch1
                v2 = result.group(3)
                return f"{b}:{ch1}:{v1}-{b}:{ch2}:{v2}", ch1

            result = self._v_cv.search(chunk)
            if result:
                v1 = result.group(1)
                ch2 = result.group(2)
                v2 = result.group(3)
                result = regex.match(r'(.*?):', chunk)
                if result:
                    ch1 = result.group(1)
                    return f"{b}:{ch1}:{v1}-{b}:{ch2}:{v2}", ch2

            result = self._cv.search(chunk)
            if result:
                ch1 = result.group(1)
                v1 = result.group(2)
                return f"{b}:{ch1}:{v1}", ch1

            result = self._d_d.search(chunk)
            if result:
                if multi:
                    ch1 = result.group(1)
                    v1 = '1'
                    ch2 = result.group(2)
                    v2 = str(self._ranges.loc[(self._ranges.Book == book) & (self._ranges.Chapter == int(ch2)), ['Last']].values[0][0])
                    return f"{b}:{ch1}:{v1}-{b}:{ch2}:{v2}", None
                else:
                    ch1 = '1'
                    v1 = result.group(1)
                    v2 = result.group(2)
                    return f"{b}:{ch1}:{v1}-{b}:{ch1}:{v2}", ch1

            result = self._d.search(chunk)
            if result:
                if multi:
                    ch1 = result.group(1)
                    v1 = '1'
                    ch2 = ch1
                    v2 = str(self._ranges.loc[(self._ranges.Book == book) & (self._ranges.Chapter == int(ch2)), ['Last']].values[0][0])
                    return f"{b}:{ch1}:{v1}-{b}:{ch2}:{v2}", None
                else:
                    ch1 = '1'
                    v1 = result.group(1)
                return f"{b}:{ch1}:{v1}", None

            return None, None

        def r(match):
            scripture = match.group(1).strip('}{')
            _, tr_name, rest, bk_num, last = scripture.split('|')
            bk_num = int(bk_num)
            last = int(last)
            if rest == '': # whole book
                v = self._ranges.loc[(self._ranges.Book == bk_num) & (self._ranges.Chapter == last), ['Last']].values[0][0]
                if last == 1:
                    output = f'{prefix}{bk_num}:1:1-{bk_num}:1:{v}{suffix}{tr_name}</a>'
                else:
                    output = f'{prefix}{bk_num}:1:1-{bk_num}:{last}:{v}{suffix}{tr_name}</a>'
                return output
            output = ''
            rest = rest or ''
            for chunk in rest.split(';'):
                for result in regex.finditer(self._dd, rest, overlapped=True):
                    if int(result.group(2)) - int(result.group(1)) == 1:
                        chunk = regex.sub(result.group(), f'{result.group(1)}-{result.group(2)}', chunk)
                ch = 0
                for bit in chunk.split(','):
                    if ch:
                        link, ch = process_verses(f"{ch}:{bit}", bk_num, last>1)
                        # output += ', '
                    else:
                        link, ch = process_verses(bit, bk_num, last>1)
                        # output += '; '
                    output += ', '
                    if tr_name and rest:
                        tr_name += ' '
                    for result in self._d_d.finditer(bit):
                        end = result.group(2)
                        start = result.group(1)
                        if int(end) - int(start) == 1:
                            bit = regex.sub(result.group(), f"{start}, {end}", bit)
                    output += f'{prefix}{link}{suffix}{tr_name}{bit.strip()}</a>'
                    tr_name = ''
            return output.strip(' ;,')

        text = self._locate_scriptures(text)
        return regex.sub(self._tagged, r, text)

    def rewrite_scriptures(self, text):

        def r(match):
            _, tr_name, rest, _, _ = match.group(1).strip('}{').split('|')
            if rest:
                return tr_name+' '+rest.replace(',', ', ')
            else:
                return tr_name

        text = self._locate_scriptures(text)
        return regex.sub(self._tagged, r, text)


def _main(args):

    def switchboard(text):
        if args['l'] is not None:
            prefix = ''
            suffix = ''
            if len(args['l']) > 1:
                suffix = args['l'][1]
            if len(args['l']) > 0:
                prefix = args['l'][0] #or 'https://my.website.com/'
            return s.link_scriptures(text, '<a href="'+prefix, suffix+'>')
        elif args['c']:
            return s.code_scriptures(text)
        elif args['d']:
            return s.decode_scriptures(literal_eval(text))
        elif args['x']:
            return s.list_scriptures(text)
        elif args['t']:
            return s.tag_scriptures(text)
        else:
            return s.rewrite_scriptures(text)

    form = None
    if args['standard']:
        form = 'standard'
    elif args['official']:
        form = 'official'
    elif args['full']:
        form = 'full'

    s = Scriptures(args['language'], args['translate'], form, args['u'], not args['q'])

    if args['f']:
        if args['o'] and (args['o'] == args['f']):
            print('Make sure in-file and out-file are different!\n')
            exit()
        with open(args['f'], 'r', encoding='UTF-8') as f:
            txt = f.read()
    else:
        txt = args['r']

    txt = switchboard(txt)

    if args['o']:
        with open(args['o'], 'w', encoding='UTF-8') as f:
            f.write(str(txt))
    else:
        print(txt)

if __name__ == "__main__":
    PROJECT_PATH = Path(__file__).resolve().parent
    APP = Path(__file__).stem
    parser = argparse.ArgumentParser(description="parse and process (tag, translate, link, encode/decode) Bible scripture references; see README for more information")

    parser.add_argument('-v', action='version', version=f"{APP} {VERSION}", help='show version and exit')
    parser.add_argument('-q', action='store_true', help="don't show errors")

    function_group = parser.add_argument_group('data source (one required)', 'choose between terminal or file input:')
    mode = function_group.add_mutually_exclusive_group(required=True)
    mode.add_argument('-f', metavar='in-file', help='get input from file (UTF-8)')
    mode.add_argument('-r', metavar='reference', help='process "reference; reference; etc."')
    parser.add_argument('-o', metavar='out-file', help='output file (terminal output if not provided)')

    parser.add_argument('--language', default='English', choices=available_languages, help='indicate source language for book names (English if unspecified)')
    parser.add_argument('--translate', choices=available_languages, help='indicate output language for book names (same as source if unspecified)')
    parser.add_argument('-u', action='store_true', help='capitalize (upper-case) book names')
    format_group = parser.add_argument_group('output format (optional)', 'if provided, book names will be rewritten accordingly:')
    formats = format_group.add_mutually_exclusive_group(required=False)
    formats.add_argument('--full', action='store_true', help='output as full name - default (eg., "Genesis")')
    formats.add_argument('--official', action='store_true', help='output as official abbreviation (eg., "Ge")')
    formats.add_argument('--standard', action='store_true', help='output as standard abbreviation (eg., "Gen.")')

    type_group = parser.add_argument_group('type of conversion', 'if not specified, references are simply rewritten according to chosen (or default) output format:')
    tpe = type_group.add_mutually_exclusive_group(required=False)
    tpe.add_argument('-c', action='store_true', help='encode as BCV-notation ranges')
    tpe.add_argument('-d', action='store_true', help='decode list of BCV-notation ranges')
    tpe.add_argument('-l', nargs='*', metavar=('prefix', 'suffix'), help='create <a></a> links; provide a "prefix" and a "suffix" (or neither for testing)')
    tpe.add_argument('-t', action='store_true', help='tag scriptures with {{ }}')
    tpe.add_argument('-x', action='store_true', help='extract list of scripture references')

    args = parser.parse_args()

    _main(vars(args))
