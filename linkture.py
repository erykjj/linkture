#!/usr/bin/env python3

"""
  File:           linkture

  Description:    Parse and process Bible scripture references

  MIT License     Copyright (c) 2023 Eryk J.

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

VERSION = '2.0.0'

import argparse, json, regex, sqlite3
import pandas as pd

from ast import literal_eval
from pathlib import Path
from unidecode import unidecode

available_languages = ('Chinese', 'Danish', 'Dutch', 'English', 'French', 'German', 'Greek', 'Italian', 'Japanese', 'Korean', 'Norwegian', 'Polish', 'Portuguese', 'Russian', 'Spanish')

class Scriptures():

    def __init__(self, language='English', translate=None, form=None):
        if language not in available_languages:
            raise ValueError("Indicated source language is not an option!")
        if translate:
            if translate not in available_languages:
                raise ValueError("Indicated translation language is not an option!")
        else:
            translate = language
        self.rewrite = bool((language != translate) or form)
        if form == "full":
            form = 3
        elif form == "standard":
            form = 4
        elif form == "official":
            form = 5
        else:
            form = 3
        self.src_book_names = {}
        path = Path(__file__).resolve().parent

        self.tr_book_names = ['Bible']
        con = sqlite3.connect(path / 'res/resources.db')
        cur = con.cursor()
        for rec in cur.execute(f"SELECT * FROM Books WHERE Language = '{translate}';").fetchall():
            self.tr_book_names.insert(rec[2], rec[form])
        for rec in cur.execute(f"SELECT * FROM Books WHERE Language = '{language}';").fetchall():
            for i in range(3,6):
                normalized = unidecode(rec[i].replace(' ', '').replace('.', '').replace('-', '').upper())
                self.src_book_names[normalized] = rec[2]
        with open(path / 'res/custom.json', 'r', encoding='UTF-8') as json_file:
            b = json.load(json_file)
        if language in b.keys():
            for row in b[language]:
                names = row[1].split(', ')
                for item in names:
                    normalized = unidecode(item.replace(' ', '').replace('.', '').replace('-', '').upper())
                    self.src_book_names[normalized] = row[0]
        self.ranges = pd.read_sql_query("SELECT * FROM Ranges;", con)
        cur.close()
        con.close()

        self.first_pass = regex.compile(r'((?:(?:(?:[1-5]\p{L}{0,2}|[iIvV]{1,3})[—–\-\.   ]*)?\p{Lu}[\p{L}\.—–\-]+(?![,—–\-])[:\.—–\-\d,   ;]*(?<!;\s)\d)|(?:(?:[1-5]\p{L}{0,2}|[iIvV]{1,3})[\.—–\-   ]*\p{Lu}[\p{L}\.—–\-]+))')
        self.second_pass = regex.compile(r'(?![^{]*})(\p{Lu}[\p{L}\.—–\-]+(?![,—–\-])[:\.—–\-\d,   ;]*(?<!;\s)\d)')
        self.bk_ref = regex.compile(r'((?:[1-5]\p{L}{0,2}|[iIvV]{1,3})?[\-\.]?[\p{L}\-\.]{2,})(.*)') # CHECK: not tested with non-Latin characters
        self.tagged = regex.compile(r'({{.*?}})')

        self.cv_cv = regex.compile(r'(\d+):(\d+)-(\d+):(\d+)')
        self.cv_v = regex.compile(r'(\d+):(\d+)-(\d+)')
        self.cv = regex.compile(r'(\d+):(\d+)')
        self.ddd = regex.compile(r'(\d+),(\d+),(\d+)')
        self.dd_d = regex.compile(r'(\d+),(\d+)-(\d+)')
        self.d_dd = regex.compile(r'(\d+)-(\d+),(\d+)')
        self.d_d = regex.compile(r'(\d+)-(\d+)(?!:)')
        self.dd = regex.compile(r'(\d+),(\d+)')
        self.d = regex.compile(r'(\d+)')


    def _scripture_parts(self, scripture):

        def check_book(bk_name):
            bk_name = regex.sub(r'[\-\.]', '', bk_name.upper())
            bk_name = unidecode(bk_name) # NOTE: this converts Génesis to Genesis and English recognizes it !! Feature :-)
            if bk_name not in self.src_book_names:
                return None, 0
            else:
                bk_num = self.src_book_names[bk_name]
            return self.ranges.loc[(self.ranges.Book == bk_num) & (self.ranges.Chapter.isnull()), ['Book', 'Last']].values[0]

        reduced = regex.sub(r'[   ]', '', scripture)
        reduced = regex.sub(r'[—–]', '-', reduced)
        result = self.bk_ref.search(reduced)
        if result:
            bk_name, rest = result.group(1).strip(), result.group(2).strip()
            bk_num, last = check_book(bk_name)
            return bk_name, bk_num, rest.replace('.', ':'), last
        else:
            return scripture, None, None, 0

    def _validate(self, b, ch, vs):
        c = int(ch)
        v = int(vs)
        if not (0 < b <= 66): # book out of range
            return None
        if not (0 < c <= self.ranges.loc[(self.ranges.Book == b) & (self.ranges.Chapter.isnull()), ['Last']].values[0]): # chapter out of range
            return None
        if not (0 < v <= self.ranges.loc[(self.ranges.Book == b) & (self.ranges.Chapter == c), ['Last']].values[0]): # verse out of range
            return None
        return True

    def _rewrite_scripture(self, scripture):

        def reform_series(txt): # rewrite comma-separated consecutive sequences as (1, 2, 3) as ranges (1-3) and consecutive ranges (1-2) as comma-separated sequences (1, 2)
            found = True
            while found:
                found = False
                for result in self.ddd.finditer(txt):
                    end = result.group(3)
                    start = result.group(1)
                    if int(end) - int(start) == 2:
                        found = True
                        txt = regex.sub(result.group(), f"{start}-{end}", txt)
                for result in self.d_dd.finditer(txt):
                    end = result.group(3)
                    mid = result.group(2)
                    start = result.group(1)
                    if int(end) - int(mid) == 1:
                        found = True
                        txt = regex.sub(result.group(), f"{start}-{end}", txt)
                for result in self.dd_d.finditer(txt):
                    end = result.group(3)
                    mid = result.group(2)
                    start = result.group(1)
                    if int(mid) - int(start) == 1:
                        found = True
                        txt = regex.sub(result.group(), f"{start}-{end}", txt)
                for result in self.d_d.finditer(txt):
                    end = result.group(2)
                    start = result.group(1)
                    if int(end) - int(start) == 1:
                        found = True
                        txt = regex.sub(result.group(), f"{start},{end}", txt)
                for result in self.cv_cv.finditer(txt):
                    sc = result.group(1)
                    sv = result.group(2)
                    ec = result.group(3)
                    ev = result.group(4)
                    if int(sc) == int(ec):
                        found = True
                        txt = regex.sub(result.group(), f"{sc}:{sv}-{ev}", txt)
            return txt

        bk_name, bk_num, rest, _ = self._scripture_parts(scripture)
        rest = rest or ''
        if not bk_num:
            return scripture
        else:
            if self.rewrite:
                bk_name = self.tr_book_names[bk_num]
            output = bk_name+' '
        for chunk in rest.split(';'):
            chunk = reform_series(chunk)
            output += chunk.strip()+'; '
        return output.replace(',', ', ').strip(' ;,')


    def list_scriptures(self, text):
        lst = []
        text = self.tag_scriptures(text)
        for i in regex.findall(self.tagged, text):
            lst.append(i.strip('{}'))
        return lst

    def tag_scriptures(self, text): # TODO: verify via decode(code(scripture))

        def r(match):
            i = match.group(1)
            _, bk_num, _, _ = self._scripture_parts(i)
            if bk_num:
                if self.rewrite:
                    script = self._rewrite_scripture(i)
                else:
                    script = i
                if self._decode_scripture(self._code_scripture(script)):
                    return '{{'+script+'}}'
            return i

        text = regex.sub(self.first_pass, r, text)
        return regex.sub(self.second_pass, r, text)

    def _code_scripture(self, scripture):

        def code_verses(chunk, book, multi):
            b = str(book).zfill(2)

            result = self.cv_cv.search(chunk)
            if result:
                c = result.group(1)
                v = result.group(2)
                if not self._validate(book, c, v):
                    return None, 0
                ch1 = c.zfill(3)
                v1 = v.zfill(3)

                c = result.group(3)
                v = result.group(4)
                if not self._validate(book, c, v):
                    return None, 0
                ch2 = c.zfill(3)
                v2 = v.zfill(3)
                return (b+ch1+v1, b+ch2+v2), 0

            result = self.cv_v.search(chunk)
            if result:
                c = result.group(1)
                v = result.group(2)
                if not self._validate(book, c, v):
                    return None, 0
                ch1 = c.zfill(3)
                v1 = v.zfill(3)

                v = result.group(3)
                if not self._validate(book, c, v):
                    return None, 0
                v2 = v.zfill(3)
                return (b+ch1+v1, b+ch1+v2), ch1

            result = self.cv.search(chunk)
            if result:
                c = result.group(1)
                v = result.group(2)
                if not self._validate(book, c, v):
                    return None, 0
                ch1 = c.zfill(3)
                v1 = v.zfill(3)
                return (b+ch1+v1, b+ch1+v1), ch1

            result = self.d_d.search(chunk)
            if result:
                if multi:
                    c = result.group(1)
                    v = 1
                    if not self._validate(book, c, v):
                        return None, 0
                    ch1 = c.zfill(3)
                    v1 = '001'

                    c = result.group(2)
                    if not self._validate(book, c, v):
                        return None, 0
                    ch2 = c.zfill(3)
                    v2 = str(self.ranges.loc[(self.ranges.Book == book) & (self.ranges.Chapter == int(ch2)), ['Last']].values[0][0]).zfill(3)
                else:
                    c = 1
                    v = result.group(1)
                    if not self._validate(book, c, v):
                        return None, 0
                    ch1 = '001'
                    v1 = v.zfill(3)

                    v = result.group(2)
                    if not self._validate(book, c, v):
                        return None, 0
                    v2 = v.zfill(3)
                return (b+ch1+v1, b+ch1+v2), 0

            result = self.d.search(chunk)
            if result:
                if multi:
                    c = result.group(1)
                    v = 1
                    if not self._validate(book, c, v):
                        return None, 0
                    ch1 = c.zfill(3)
                    v1 = '001'
                    v2 = str(self.ranges.loc[(self.ranges.Book == book) & (self.ranges.Chapter == int(ch1)), ['Last']].values[0][0]).zfill(3)
                    return (b+ch1+v1, b+ch1+v2), 0
                else:
                    c = 1
                    v = result.group(1)
                    if not self._validate(book, c, v):
                        return None, 0
                    ch1 = '001'
                    v1 = v.zfill(3)
                return (b+ch1+v1, b+ch1+v1), 0

            return None, 0

        lst = []
        _, bk_num, rest, last = self._scripture_parts(scripture)
        rest = rest or ''
        if not bk_num:
            return None
        if rest == '': # whole book
            v = self.ranges.loc[(self.ranges.Book == bk_num) & (self.ranges.Chapter == last), ['Last']].values[0][0]
            if last == 1:
                rest = f'1-{v}'
            else:
                rest = f'1:1-{last}:{v}'
        for result in regex.finditer(self.dd, rest, overlapped=True):
            if int(result.group(2)) - int(result.group(1)) == 1:
                rest = regex.sub(result.group(), f'{result.group(1)}-{result.group(2)}', rest)
        for chunk in rest.split(';'):
            ch = 0
            for bit in chunk.split(','):
                # try:
                if ch:
                    tup, ch = code_verses(f"{ch}:{bit}", bk_num, last>1)
                else:
                    tup, ch = code_verses(bit, bk_num, last>1)
                # except:
                #     return None
                if not tup:
                    return None
                lst.append(tup)
        return lst


    def code_scriptures(self, text):

        lst = []
        text = self.tag_scriptures(text)
        for scripture in regex.findall(self.tagged, text):
            bcv_ranges = self._code_scripture(scripture.strip('{}'))
            if bcv_ranges:
                for bcv_range in bcv_ranges:
                    lst.append(bcv_range)
        return lst

    def _decode_scripture(self, bcv_range):
        if not bcv_range:
            return None
        start, end = bcv_range[0]
        sb = int(start[:2])
        sc = int(start[2:5])
        sv = int(start[5:])
        eb = int(end[:2])
        ec = int(end[2:5])
        ev = int(end[5:])
        if not ((0 < sb <= 66) & (sb == eb)): # book out of range
            return None
        if not (0 < sc <= ec <= self.ranges.loc[(self.ranges.Book == sb) & (self.ranges.Chapter.isnull()), ['Last']].values[0]): # chapter(s) out of range
            return None
        if not ((0 < sv <= self.ranges.loc[(self.ranges.Book == sb) & (self.ranges.Chapter == sc), ['Last']].values[0]) & (0 < ev <= self.ranges.loc[(self.ranges.Book == sb) & (self.ranges.Chapter == ec), ['Last']].values[0])): # verse(s) out of range
            return None
        bk_name = self.tr_book_names[sb]
        if self.ranges.loc[(self.ranges.Book == sb) & (self.ranges.Chapter.isnull()), ['Last']].values[0] == 1:
            ch = ' '
        else:
            ch = f" {sc}:"
        if start == end:
            scripture = f"{bk_name}{ch}{sv}"
        else:
            if sc == ec:
                if ev - sv == 1:
                    scripture = f"{bk_name}{ch}{sv}, {ev}"
                else:
                    scripture = f"{bk_name}{ch}{sv}-{ev}"
            else:
                scripture = f"{bk_name}{ch}{sv}-{ec}:{ev}"
        return scripture

    def decode_scriptures(self, reference=[]):
        scriptures = []
        for bcv_range in reference:
            scripture = self._decode_scripture(bcv_range)
            if scripture:
                scriptures.append(scripture)
        return scriptures


    def link_scriptures(self, text, prefix='<a href="http://', suffix='" >'):

        def process_verses(chunk, book, multi):
            b = str(book)

            result = self.cv_cv.search(chunk)
            if result:
                ch1 = result.group(1)
                v1 = result.group(2)
                ch2 = result.group(3)
                v2 = result.group(4)
                return f"{b}:{ch1}:{v1}-{b}:{ch2}:{v2}", 0

            result = self.cv_v.search(chunk)
            if result:
                ch1 = result.group(1)
                v1 = result.group(2)
                ch2 = ch1
                v2 = result.group(3)
                return f"{b}:{ch1}:{v1}-{b}:{ch2}:{v2}", ch1

            result = self.cv.search(chunk)
            if result:
                ch1 = result.group(1)
                v1 = result.group(2)
                return f"{b}:{ch1}:{v1}", ch1

            result = self.d_d.search(chunk)
            if result:
                if multi:
                    ch1 = result.group(1)
                    v1 = '1'
                    ch2 = result.group(2)
                    v2 = str(self.ranges.loc[(self.ranges.Book == book) & (self.ranges.Chapter == int(ch2)), ['Last']].values[0][0])
                else:
                    ch1 = '1'
                    v1 = result.group(1)
                    ch2 = ch1
                    v2 = result.group(2)
                return f"{b}:{ch1}:{v1}-{b}:{ch2}:{v2}", 0

            result = self.d.search(chunk)
            if result:
                if multi:
                    ch1 = result.group(1)
                    v1 = '1'
                    ch2 = ch1
                    v2 = str(self.ranges.loc[(self.ranges.Book == book) & (self.ranges.Chapter == int(ch2)), ['Last']].values[0][0])
                    return f"{b}:{ch1}:{v1}-{b}:{ch2}:{v2}", 0
                else:
                    ch1 = '1'
                    v1 = result.group(1)
                return f"{b}:{ch1}:{v1}", 0

            return None, 0

        def r(match):
            scripture = match.group(1).strip('}{')
            bk_name, bk_num, rest, last = self._scripture_parts(scripture)
            output = ''
            if rest == '': # whole book
                v = self.ranges.loc[(self.ranges.Book == bk_num) & (self.ranges.Chapter == last), ['Last']].values[0][0]
                if last == 1:
                    rest = f'1-{v}'
                else:
                    rest = f'1:1-{last}:{v}'
            rest = rest or ''
            for chunk in rest.split(';'):
                ch = 0
                for bit in chunk.split(','):
                    try: # CHECK: any way to ensure it never fails??
                        if ch:
                            link, ch = process_verses(f"{ch}:{bit}", bk_num, last>1)
                            output += ', '
                        else:
                            link, ch = process_verses(bit, bk_num, last>1)
                            output += '; '
                    except:
                        continue
                    if not link:
                        continue
                    if bk_name:
                        bk_name += ' '
                    output += f'{prefix}{link}{suffix}{bk_name}{bit.strip()}</a>'
                    bk_name = ''
                return output.strip(' ;,')

        text = self.tag_scriptures(text)
        return regex.sub(self.tagged, r, text)

    def rewrite_scriptures(self, text):

        def r(match):
            return match.group(1).strip('}{')

        text = self.tag_scriptures(text)
        return regex.sub(self.tagged, r, text)


def _main(args):

    def switchboard(text):
        if args['l']:
            prefix = args['l'][0] #or 'https://my.website.org/'
            suffix = args['l'][1] or '">'
            return s.link_scriptures(text, '<a href="'+prefix, suffix)
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

    form = 'full' # default is rewrite
    if args['standard']:
        form = 'standard'
    elif args['official']:
        form = 'official'
    elif args['full']:
        form = 'full'
    s = Scriptures(args['language'], args['translate'], form)

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

    parser.add_argument('-v', '--version', action='version', version=f"{APP} {VERSION}", help='show version and exit')

    function_group = parser.add_argument_group('data source (one required)', 'choose between terminal or file input:')
    mode = function_group.add_mutually_exclusive_group(required=True)
    mode.add_argument('-f', metavar='in-file', help='get input from file (UTF-8)')
    mode.add_argument('-r', metavar='reference', help='process "reference; reference; etc."')
    parser.add_argument('-o', metavar='out-file', help='output file (terminal output if not provided)')

    parser.add_argument('--language', default='English', choices=available_languages, help='indicate source language for book names (English if unspecified)')
    parser.add_argument('--translate', choices=available_languages, help='indicate output language for book names (same as source if unspecified)')
    format_group = parser.add_argument_group('output format (optional)', 'if provided, book names will be rewritten accordingly:')
    formats = format_group.add_mutually_exclusive_group(required=False)
    formats.add_argument('--full', action='store_true', help='output as full name - default (eg., "Genesis")')
    formats.add_argument('--official', action='store_true', help='output as official abbreviation (eg., "Ge")')
    formats.add_argument('--standard', action='store_true', help='output as standard abbreviation (eg., "Gen.")')

    type_group = parser.add_argument_group('type of conversion', 'if not specified, references are simply rewritten according to chosen (or default) output format:')
    tpe = type_group.add_mutually_exclusive_group(required=False)
    tpe.add_argument('-c', action='store_true', help='encode as BCV-notation ranges')
    tpe.add_argument('-d', action='store_true', help='decode list of BCV-notation ranges')
    tpe.add_argument('-l', nargs=2, metavar=('prefix', 'suffix'), help='create <a href></a> links')
    tpe.add_argument('-t', action='store_true', help='tag scriptures with {{ }}')
    tpe.add_argument('-x', action='store_true', help='extract list of scripture references')

    args = parser.parse_args()

    _main(vars(args))
