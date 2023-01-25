#!/usr/bin/env python3

"""
File:           linkture (module)

Description:    Process and link/code Bible scripture references

MIT License     Copyright (c) 2023 Eryk J.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Softwaregex.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWAregex.
"""

VERSION = '1.5.0'


import argparse, json, regex
import pandas as pd

from pathlib import Path
from unidecode import unidecode


class Scriptures():

    def __init__(self, language='English', form=0, rewrite=False):
        if language not in ('Chinese', 'Danish', 'Dutch', 'English', 'French', 'German', 'Greek', 'Italian', 'Japanese', 'Korean', 'Norwegian', 'Polish', 'Portuguese', 'Russian', 'Spanish'):
            return
        self.bn = {}
        self.rewrite = rewrite
        path = Path(__file__).resolve().parent

        self.books = ['Bible']
        with open(path / 'res/books.json', 'r', encoding='UTF-8') as json_file:
            b = json.load(json_file)
        for row in b[language]:
            names = row[1].split(', ')
            self.books.insert(row[0], names[form])
            for item in names:
                normalized = unidecode(item.replace(' ', '').replace('.', '').replace('-', '').upper())
                self.bn[normalized] = row[0]
        with open(path / 'res/custom.json', 'r', encoding='UTF-8') as json_file:
            b = json.load(json_file)
        for row in b[language]:
            names = row[1].split(', ')
            for item in names:
                normalized = unidecode(item.replace(' ', '').replace('.', '').replace('-', '').upper())
                self.bn[normalized] = row[0]

        self.br = pd.read_csv(path / 'res/ranges.csv', delimiter='\t')

        self.bk_ref = regex.compile(r'(\d?(?:\s?[\p{L}\.-]+)+)\s?(.*)') # CHECK: not tested with non-Latin characters
        self.ch_v_ch_v = regex.compile(r'(\d+)\s*:\s*(\d+)\s*[-\u2013\u2014]\s*(\d+)\s*:\s*(\d+)')
        self.ch_v_v = regex.compile(r'(\d+)\s*:\s*(\d+)\s*[-\u2013\u2014]\s*(\d+)')
        self.ch_v = regex.compile(r'(\d+)\s*:\s*(\d+)')
        self.ch_ch = regex.compile(r'(\d+)\s*[-\u2013\u2014]\s*(\d+)')
        self.ch_ = regex.compile(r'(\d+)')
        self.v_v = regex.compile(r'(?=(\d+\s*),(\s*\d+))')
        self.vv = regex.compile(r'(?<!:)(\d+)\s*-\s*(\d+)')
        self.dd = regex.compile(r'(\d+)\s*-\s*(\d+)\s*(?!:)')

    def _check_book(self, book):
        bk = unidecode(book).upper().replace(' ', '').replace('.', '').replace('-', '')
        if bk not in self.bn:
            return None, 0
        else:
            book = self.bn[bk]
        return self.br.loc[(self.br.Book == book) & (self.br.Chapter.isnull()), ['Book', 'Last']].values[0]

    def _process_scripture(self, scripture):
        result = self.bk_ref.search(scripture)
        if result:
            bk, rest = result.group(1), result.group(2).lstrip()
            bn, last = self._check_book(bk)
            if not bn:
                return '', '', None, -1
            if rest == "":
                vss = self.br.loc[(self.br.Book == bn) & (self.br.Chapter == last), ['Last']].values[0][0]
                rest = f"1:1-{last}:{vss}"
            for result in self.v_v.findall(rest):
                if int(result[1]) - int(result[0]) == 1:
                    rest = rest.replace(f"{result[0]},{result[1]}", f"{result[0].rstrip()}-{result[1].lstrip()}")
            if bn:
                if self.rewrite:
                    bk = self.books[bn]
                return f"{bk} ", rest, bn, last
        return '', '', None, 0

    def link_scripture(self, scripture):

        def process_verses(chunk, book, multi):
            b = str(book)

            result = self.ch_v_ch_v.search(chunk)
            if result:
                ch1 = result.group(1)
                v1 = result.group(2)
                ch2 = result.group(3)
                v2 = result.group(4)
                return f"{b}:{ch1}:{v1}-{b}:{ch2}:{v2}", 0

            result = self.ch_v_v.search(chunk)
            if result:
                ch1 = result.group(1)
                v1 = result.group(2)
                ch2 = ch1
                v2 = result.group(3)
                return f"{b}:{ch1}:{v1}-{b}:{ch2}:{v2}", ch1

            result = self.ch_v.search(chunk)
            if result:
                ch1 = result.group(1)
                v1 = result.group(2)
                return f"{b}:{ch1}:{v1}", ch1

            result = self.ch_ch.search(chunk)
            if result:
                if multi:
                    ch1 = result.group(1)
                    v1 = '1'
                    ch2 = result.group(2)
                    v2 = str(self.br.loc[(self.br.Book == book) & (self.br.Chapter == int(ch2)), ['Last']].values[0][0])
                else:
                    ch1 = '1'
                    v1 = result.group(1)
                    ch2 = ch1
                    v2 = result.group(2)
                return f"{b}:{ch1}:{v1}-{b}:{ch2}:{v2}", 0

            result = self.ch_.search(chunk)
            if result:
                if multi:
                    ch1 = result.group(1)
                    v1 = '1'
                    ch2 = ch1
                    v2 = str(self.br.loc[(self.br.Book == book) & (self.br.Chapter == int(ch2)), ['Last']].values[0][0])
                    return f"{b}:{ch1}:{v1}-{b}:{ch2}:{v2}", 0
                else:
                    ch1 = '1'
                    v1 = result.group(1)
                return f"{b}:{ch1}:{v1}", 0

            return None, 0

        def undo_series(txt):
            txt = txt.replace(' ', '')
            for result in self.ch_v_ch_v.findall(txt):
                if result[0] == result[2]:
                    txt = txt.replace(f"{result[0]}:{result[1]}-{result[2]}:{result[3]}", f"{result[0]}:{result[1]}-{result[3]}")
            for result in self.dd.findall(txt):
                if int(result[1]) - int(result[0]) == 1:
                    txt = txt.replace(f"{result[0]}-{result[1]}", f"{result[0]}, {result[1]}")
            return txt

        url = ''
        book = ''
        for chunk in scripture.split(';'):
            try:
                bk, rest, bn, last = self._process_scripture(chunk)
                if last == -1:
                    url = url + '; ' + '{{' + chunk.strip() + '}}'
                    continue
                if not bn:
                    bk, rest, bn, last = self._process_scripture(book + chunk)
                if bk.strip() != book.strip():
                    book = bk
                else:
                    bk = ''
                chap = 0
                for bit in rest.split(','):
                    if chap:
                        link, chap = process_verses(f"{chap}:{bit}", bn, last-1)
                        url += ', '
                    else:
                        link, chap = process_verses(bit, bn, last-1)
                        url += '; '
                    processed_chunk = f"{bk}{undo_series(bit).lstrip()}"
                    url += f'<a href="jwpub://b/NWTR/{link}" class="b">{processed_chunk.strip()}</a>'
                    bk = ''
            except:
                url += "{{" + chunk + "}}"
        return url.strip(' ;,')

    def code_scripture(self, scripture):

        def code_verses(chunk, book, multi):
            b = str(book).zfill(2)

            result = self.ch_v_ch_v.search(chunk)
            if result:
                ch1 = result.group(1).zfill(3)
                v1 = result.group(2).zfill(3)
                ch2 = result.group(3).zfill(3)
                v2 = result.group(4).zfill(3)
                return (b+ch1+v1, b+ch2+v2), 0

            result = self.ch_v_v.search(chunk)
            if result:
                ch1 = result.group(1).zfill(3)
                v1 = result.group(2).zfill(3)
                ch2 = ch1
                v2 = result.group(3).zfill(3)
                return (b+ch1+v1, b+ch2+v2), ch1

            result = self.ch_v.search(chunk)
            if result:
                ch1 = result.group(1).zfill(3)
                v1 = result.group(2).zfill(3)
                return (b+ch1+v1, b+ch1+v1), ch1

            result = self.ch_ch.search(chunk)
            if result:
                if multi:
                    ch1 = result.group(1).zfill(3)
                    v1 = '001'
                    ch2 = result.group(2).zfill(3)
                    v2 = str(self.br.loc[(self.br.Book == book) & (self.br.Chapter == int(ch2)), ['Last']].values[0][0]).zfill(3)
                else:
                    ch1 = '001'
                    v1 = result.group(1).zfill(3)
                    ch2 = ch1
                    v2 = result.group(2).zfill(3)
                return (b+ch1+v1, b+ch2+v2), 0

            result = self.ch_.search(chunk)
            if result:
                if multi:
                    ch1 = result.group(1).zfill(3)
                    v1 = '001'
                    ch2 = ch1
                    v2 = str(self.br.loc[(self.br.Book == book) & (self.br.Chapter == int(ch2)), ['Last']].values[0][0]).zfill(3)
                    return (b+ch1+v1, b+ch2+v2), 0
                else:
                    ch1 = '001'
                    v1 = result.group(1).zfill(3)
                return (b+ch1+v1, b+ch1+v1), 0

            return None, 0

        series = []
        book = ''
        for chunk in scripture.split(';'):
            try:
                bk, rest, bn, last = self._process_scripture(chunk)
                if last == -1:
                    continue
                if not bn:
                    bk, rest, bn, last = self._process_scripture(book + chunk)
                    bk = ''
                else:
                    book = bk
                chap = 0
                for bit in rest.split(','):
                    if chap:
                        link, chap = code_verses(f"{chap}:{bit}", bn, last-1)
                    else:
                        link, chap = code_verses(bit, bn, last-1)
                    series.append(link)
                    bk = ''
            except:
                pass
        return series

    def decode_scripture(self, reference=[]):
        scriptures = ''
        for item in reference:
            if not item:
                continue
            start, end = item
            sb = int(start[:2])
            sc = int(start[2:5])
            sv = int(start[5:])
            eb = int(end[:2])
            ec = int(end[2:5])
            ev = int(end[5:])
            if not ((0 < sb <= 66) & (sb == eb)): # book out of range
                continue
            if not (0 < sc <= ec <= self.br.loc[(self.br.Book == sb) & (self.br.Chapter.isnull()), ['Last']].values[0]): # chapter(s) out of range
                continue
            if not ((0 < sv <= self.br.loc[(self.br.Book == sb) & (self.br.Chapter == sc), ['Last']].values[0]) & (0 < ev <= self.br.loc[(self.br.Book == sb) & (self.br.Chapter == ec), ['Last']].values[0])): # verse(s) out of range
                continue
            bk = self.books[sb]
            if self.br.loc[(self.br.Book == sb) & (self.br.Chapter.isnull()), ['Last']].values[0] == 1:
                ch = ' '
            else:
                ch = f" {sc}:"
            if start == end:
                scripture = f"{bk}{ch}{sv}"
            else:
                if sc == ec:
                    if ev - sv == 1:
                        scripture = f"{bk}{ch}{sv}, {ev}"
                    else:
                        scripture = f"{bk}{ch}{sv}-{ev}"
                else:
                    scripture = f"{bk}{ch}{sv}-{ec}:{ev}"
            scriptures += f"; {scripture}"
        return scriptures.lstrip(" ;")

    def rewrite_scripture(self, scripture):
        return self.decode_scripture(self.code_scripture(scripture))

def _main(args):

    def replacement(match):
        group = match.group(1).strip('{}')
        if not args['quiet']:
            print(f'...Processing "{group}"')
        if args['link']:
            return s.link_scripture(group)
        elif args['range']:
            return str(s.code_scripture(group))
        else:
            return s.rewrite_scripture(group)

    rewrite = False
    form = 0
    if args['standard']:
        form = 1
        rewrite = True
    elif args['official']:
        form = 2
        rewrite = True
    elif args['full']:
        form = 0
        rewrite = True
    s = Scriptures(args['language'], form, rewrite)
    m = regex.compile(r'({{.*?}})')

    if args['f']:
        if args['f'][0] == args['f'][1]:
            print('Make sure in-file and out-file are different!\n')
            exit()
        with open(args['f'][0], 'r', encoding='UTF-8') as f:
            txt = f.read()
    else:
        txt = "{{" + args['s'] + "}}"

    txt2 = regex.sub(m, replacement, txt)

    if args['f']:
        with open(args['f'][1], 'w', encoding='UTF-8') as f:
            f.write(txt2)
    else:
        print(txt2)


if __name__ == "__main__":
    PROJECT_PATH = Path(__file__).resolve().parent
    APP = Path(__file__).stem
    parser = argparse.ArgumentParser(description="process and link/encode Bible scripture references; see README for more information")

    parser.add_argument('-v', '--version', action='version', version=f"{APP} {VERSION}", help='show version and exit')

    function_group = parser.add_argument_group('operational method', 'choose between terminal or files input/output:')
    mode = function_group.add_mutually_exclusive_group(required=True)
    mode.add_argument('-f', metavar=('in-file', 'out-file'), nargs=2, help='work with files (UTF-8)')
    mode.add_argument('-s', metavar='reference', help='process "reference; reference; etc."')

    parser.add_argument('--language', default='English', choices=['Chinese', 'Danish', 'Dutch', 'English', 'French', 'German', 'Greek', 'Italian', 'Japanese', 'Korean', 'Norwegian', 'Polish', 'Portuguese', 'Russian', 'Spanish'], help='indicate language of book names (English if unspecified)')

    format_group = parser.add_argument_group('output format (optional)', 'if provided, book names will be rewritten accordingly:')
    form = format_group.add_mutually_exclusive_group(required=False)
    form.add_argument('--full', action='store_true', help='output as full name - default (eg., "Genesis")')
    form.add_argument('--official', action='store_true', help='output as official abbreviation (eg., "Ge")')
    form.add_argument('--standard', action='store_true', help='output as standard abbreviation (eg., "Gen.")')

    type_group = parser.add_argument_group('type of conversion', 'if not specified, references are simply rewritten according to chosen output format:')
    tpe = type_group.add_mutually_exclusive_group(required=False)
    tpe.add_argument('-l', '--link', action='store_true', help='create jwpub link(s)')
    tpe.add_argument('-r', '--range', action='store_true', help='create range list')

    parser.add_argument('-q', '--quiet', action='store_true', help="don't show processing status")
    args = parser.parse_args()

    _main(vars(args))
