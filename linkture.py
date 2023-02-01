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

        self.bk_ref = regex.compile(r'(\d?(?:\s?[\p{L}\.-]+)+)\s?(.*)') # CHECK: not tested with non-Latin characters
        # self.bk_ref = regex.compile(r'((?:\d{0,1}|[Ii]{0,3})[\.\-\s]?\p{Lu}[\p{L}.\-]+)(\d.*)') # CHECK: not tested with non-Latin characters
        # self.bk_ref = regex.compile(r'((?:\d{0,1}|[Ii]{0,3})[\.\-\s]?\p{Lu}[\p{L}.\-]+)')
        self.ch_v_ch_v = regex.compile(r'(\d+)\s*:\s*(\d+)[-\u2013\u2014\s]+(\d+)\s*:\s*(\d+)')
        self.ch_v_v = regex.compile(r'(\d+)\s*:\s*(\d+)\s*[-\u2013\u2014]\s*(\d+)')
        self.ch_v = regex.compile(r'(\d+)\s*:\s*(\d+)')
        self.ch_ch = regex.compile(r'(\d+)\s*[-\u2013\u2014]\s*(\d+)')
        self.ch_ = regex.compile(r'(\d+)')
        self.v_v = regex.compile(r'(?=(\d+\s*),(\s*\d+))') # NOTE: what if it's like 2:3,4,5? Should be reduced to 2:3-5
        self.d_d_d = regex.compile(r'(\d+)[\s\,]+(\d+)[\s\,]+(\d+)')
        self.d_d = regex.compile(r'(\d+)[-\u2013\u2014\s]+(\d+)')
        self.vv = regex.compile(r'(?<!:)(\d+)\s*-\s*(\d+)')
        self.dd = regex.compile(r'(\d+)\s*-\s*(\d+)\s*(?!:)')
        self.scrpt = regex.compile(r'((?:\d{0,1}|[Ii]{0,3})[\.\-\s]?\p{Lu}[\p{L}.\-]+[:​\.\-\u2013\u2014\d,\s;]*(?<!;\s)\d)')

    def _check_book(self, bk_name):
        bk_name = unidecode(bk_name).upper().replace(' ', '').replace('.', '').replace('-', '')
        if bk_name not in self.src_book_names:
            return None, 0
        else:
            bk_num = self.src_book_names[bk_name]
        return self.ranges.loc[(self.ranges.Book == bk_num) & (self.ranges.Chapter.isnull()), ['Book', 'Last']].values[0]

    # def _process_scripture(self, scripture): # TODO: returns rewritten name, not original

    #     def check_book(bk_name):
    #         bk_name = unidecode(bk_name).upper().replace(' ', '').replace('.', '').replace('-', '')
    #         if bk_name not in self.src_book_names:
    #             return None, 0
    #         else:
    #             bk_num = self.src_book_names[bk_name]
    #         return self.ranges.loc[(self.ranges.Book == bk_num) & (self.ranges.Chapter.isnull()), ['Book', 'Last']].values[0]

    #     result = self.bk_ref.search(scripture)
    #     if result:
    #         bk_name, rest = result.group(1), result.group(2).lstrip()
    #         bk_num, last = check_book(bk_name)
    #         if not bk_num:
    #             return '', '', None, -1
    #         if rest == "":
    #             vss = self.ranges.loc[(self.ranges.Book == bk_num) & (self.ranges.Chapter == last), ['Last']].values[0][0]
    #             rest = f"1:1-{last}:{vss}"
    #         for result in self.v_v.findall(rest):
    #             if int(result[1]) - int(result[0]) == 1:
    #                 rest = rest.replace(f"{result[0]},{result[1]}", f"{result[0].rstrip()}-{result[1].lstrip()}")
    #         if bk_num:
    #             return bk_name, rest, bk_num, last
    #     return '', '', None, 0

    def list_scriptures(self, text):
        return regex.findall(self.scrpt, text)

    def tag_scriptures(self, text):
        def r(match):
            return "{{" + match.group(1) + "}}"
        return regex.sub(self.scrpt, r, text)

    def link_scripture(self, scripture, prefix='<a href="http://', suffix='" >'):

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
                    v2 = str(self.ranges.loc[(self.ranges.Book == book) & (self.ranges.Chapter == int(ch2)), ['Last']].values[0][0])
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
                    v2 = str(self.ranges.loc[(self.ranges.Book == book) & (self.ranges.Chapter == int(ch2)), ['Last']].values[0][0])
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

        output = ''
        book = ''
        for chunk in scripture.split(';'):
            try:
                bk_name, rest, bk_num, last = self._process_scripture(chunk)
                # if last == -1:
                #     output = output + '; ' + '{{' + chunk.strip() + '}}'
                #     continue
                if not bk_num:
                    bk_name, rest, bk_num, last = self._process_scripture(book + chunk)
                if bk_name.strip() != book.strip():
                    book = bk_name
                else:
                    bk_name = ''
                ch = 0
                for bit in rest.split(','):
                    if ch:
                        link, ch = process_verses(f"{ch}:{bit}", bk_num, last-1)
                        output += ', '
                    else:
                        link, ch = process_verses(bit, bk_num, last-1)
                        output += '; '
                    processed_chunk = f"{bk_name}{undo_series(bit).lstrip()}"
                    output += f'{prefix}{link}{suffix}{processed_chunk.strip()}</a>'
                    bk_name = ''
            except:
                output += "{{" + chunk + "}}"
        return output.strip(' ;,')



    # def _process_scripture(self, scripture):

    #     def check_book(bk_name):
    #         bk_name = unidecode(bk_name).upper().replace(' ', '').replace('.', '').replace('-', '')
    #         if bk_name not in self.src_book_names:
    #             return None, 0
    #         else:
    #             bk_num = self.src_book_names[bk_name]
    #         return self.ranges.loc[(self.ranges.Book == bk_num) & (self.ranges.Chapter.isnull()), ['Book', 'Last']].values[0]

    #     result = self.bk_ref.search(scripture)
    #     if result:
    #         bk_name = result.group(1).strip()
    #         rest = scripture[len(bk_name):]
    #         bk_num, last = check_book(bk_name)
    #     else:
    #         bk_name = None
    #         rest = scripture
    #         bk_num = None
    #         last = None
    #     while True:
    #         result = self.d_d_d.search(rest)
    #         if not result:
    #             break
    #         end = result.group(3)
    #         start = result.group(1)
    #         if int(end) - int(start) == 2:
    #             rest = regex.sub(start+r'[\s\d\,]+'+end, f"{start.rstrip()}-{end.lstrip()}", rest)
    #     if not bk_num:
    #         return '', '', None, -1

    #     if bk_num:
    #         return bk_name, rest, bk_num, last
    #     return '', '', None, 0

    def _scripture_parts(self, scripture):
        result = self.bk_ref.search(scripture) # get book name
        if result:
            bk_name, rest = result.group(1).strip(), result.group(2).strip()
            bk_num, last = self._check_book(bk_name) # NOTE: need last??
            if self.rewrite and bk_name and bk_num: # NOTE: necessary to even ask?
                bk_name = self.tr_book_names[bk_num]
            return bk_name, bk_num, rest, last
        else:
            return scripture, None, None, 0

    def rewrite_scripture(self, scripture):

        def reform_series(txt): # rewrite comma-separated consecutive sequences as (1, 2, 3) as ranges (1-3) and consecutive ranges (1-2) as comma-separated sequences (1, 2)
            vv_v = regex.compile(r'(\d+)[\s\,]+(\d+)[-\u2013\u2014\s]+(\d+)')
            v_vv = regex.compile(r'(\d+)[-\u2013\u2014\s]+(\d+)[\s\,]+(\d+)')
            found = True
            while found:
                found = False
                for result in self.d_d_d.finditer(txt):
                    end = result.group(3)
                    start = result.group(1)
                    if int(end) - int(start) == 2:
                        found = True
                        txt = regex.sub(result.group(), f"{start}-{end}", txt)
                for result in v_vv.finditer(txt):
                    end = result.group(3)
                    mid = result.group(2)
                    start = result.group(1)
                    if int(end) - int(mid) == 1:
                        found = True
                        txt = regex.sub(result.group(), f"{start}-{end}", txt)
                for result in vv_v.finditer(txt):
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
                for result in self.ch_v_ch_v.finditer(txt):
                    sc = result.group(1)
                    sv = result.group(2)
                    ec = result.group(3)
                    ev = result.group(4)
                    if int(sc) == int(ec):
                        found = True
                        txt = regex.sub(result.group(), f"{sc}:{sv}-{ev}", txt)
            return txt

        # result = self.bk_ref.search(scripture) # get book name
        # if result:
        #     bk_name, rest = result.group(1).strip(), result.group(2).strip()
        #     bk_num, last = self._check_book(bk_name) # NOTE: need last??
        # else:
        #     return scripture
        bk_name, bk_num, rest, _ = self._scripture_parts(scripture)
        if not bk_num or not rest:
            return scripture
        else:
            output = bk_name+' '
        for chunk in rest.replace(' ', '').split(';'): # process the rest
            chunk = reform_series(chunk)
            output += chunk.lstrip()+'; '
        return output.replace(',', ', ').strip(' ;,')


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
                    v2 = str(self.ranges.loc[(self.ranges.Book == book) & (self.ranges.Chapter == int(ch2)), ['Last']].values[0][0]).zfill(3)
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
                    v2 = str(self.ranges.loc[(self.ranges.Book == book) & (self.ranges.Chapter == int(ch2)), ['Last']].values[0][0]).zfill(3)
                    return (b+ch1+v1, b+ch2+v2), 0
                else:
                    ch1 = '001'
                    v1 = result.group(1).zfill(3)
                return (b+ch1+v1, b+ch1+v1), 0

            return None, 0

        scripture = self.rewrite_scripture(scripture)
        _, bk_num, rest, last = self._scripture_parts(scripture)
        print(bk_num, rest, last)
        if not bk_num or not rest or last < 1:
            return []
        else:
            series = []
        for chunk in rest.replace(' ', '').split(';'): # process the rest
            ch = 0
            for bit in chunk.split(','):
                if ch:
                    tup, ch = code_verses(f"{ch}:{bit}", bk_num, last-1)
                else:
                    tup, ch = code_verses(bit, bk_num, last-1)
                series.append(tup)
        return series

    def code_scriptures(self, text):
        lst = []
        for i in self.list_scriptures(text):
            for c in self.code_scripture(i):
                lst.append(c)
        return lst

    def decode_scriptures(self, reference=[]):
        scriptures = []
        for item in reference:
            start, end = item
            sb = int(start[:2])
            sc = int(start[2:5])
            sv = int(start[5:])
            eb = int(end[:2])
            ec = int(end[2:5])
            ev = int(end[5:])
            if not ((0 < sb <= 66) & (sb == eb)): # book out of range
                continue
            if not (0 < sc <= ec <= self.ranges.loc[(self.ranges.Book == sb) & (self.ranges.Chapter.isnull()), ['Last']].values[0]): # chapter(s) out of range
                continue
            if not ((0 < sv <= self.ranges.loc[(self.ranges.Book == sb) & (self.ranges.Chapter == sc), ['Last']].values[0]) & (0 < ev <= self.ranges.loc[(self.ranges.Book == sb) & (self.ranges.Chapter == ec), ['Last']].values[0])): # verse(s) out of range
                continue
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
            scriptures.append(scripture)
        return scriptures

def _main(args):

    def r(match):
        group = match.group(1).strip('{}')
        if not args['quiet']:
            print(f'...Processing "{group}"')
        if args['link']:
            return s.link_scripture(group, '<a href="jwpub://b/NWTR/', '" class="b">')
        elif args['range']:
            return str(s.code_scripture(group))
        else:
            return s.rewrite_scripture(group)

    form = None
    if args['standard']:
        form = 'standard'
    elif args['official']:
        form = 'official'
    elif args['full']:
        form = 'full'
    s = Scriptures(args['language'], args['translate'], form)
    m = regex.compile(r'({{.*?}})')

    # print(s.decode_scriptures([('40006033', '40006033'), ('40007001', '40007003'), ('40007005', '40007007'), ('40008001', '40008010'), ('40008014', '40008018'), ('40009002', '40009005'), ('40009007', '40009010'), ('62002003', '62002007'), ('62003001', '62005021')]))

    if args['f']:
        if args['f'][0] == args['f'][1]:
            print('Make sure in-file and out-file are different!\n')
            exit()
        with open(args['f'][0], 'r', encoding='UTF-8') as f:
            txt = f.read()
    else:
        txt = args['s']

    txt = s.tag_scriptures(txt)
    txt = regex.sub(m, r, txt)

    if args['f']:
        with open(args['f'][1], 'w', encoding='UTF-8') as f:
            f.write(txt)
    else:
        print(txt)

if __name__ == "__main__":
    PROJECT_PATH = Path(__file__).resolve().parent
    APP = Path(__file__).stem
    parser = argparse.ArgumentParser(description="process, translate, link/encode Bible scripture references; see README for more information")

    parser.add_argument('-v', '--version', action='version', version=f"{APP} {VERSION}", help='show version and exit')

    function_group = parser.add_argument_group('operational method', 'choose between terminal or files input/output:')
    mode = function_group.add_mutually_exclusive_group(required=True)
    mode.add_argument('-f', metavar=('in-file', 'out-file'), nargs=2, help='work with files (UTF-8)')
    mode.add_argument('-s', metavar='reference', help='process "reference; reference; etc."')

    parser.add_argument('--language', default='English', choices=available_languages, help='indicate source language for book names (English if unspecified)')
    parser.add_argument('--translate', choices=available_languages, help='indicate output language for book names (same as source if unspecified)')
    format_group = parser.add_argument_group('output format (optional)', 'if provided, book names will be rewritten accordingly:')
    formats = format_group.add_mutually_exclusive_group(required=False)
    formats.add_argument('--full', action='store_true', help='output as full name - default (eg., "Genesis")')
    formats.add_argument('--official', action='store_true', help='output as official abbreviation (eg., "Ge")')
    formats.add_argument('--standard', action='store_true', help='output as standard abbreviation (eg., "Gen.")')

    type_group = parser.add_argument_group('type of conversion', 'if not specified, references are simply rewritten according to chosen (or default) output format:')
    tpe = type_group.add_mutually_exclusive_group(required=False)
    tpe.add_argument('-l', '--link', action='store_true', help='create jwpub link(s)')
    tpe.add_argument('-r', '--range', action='store_true', help='create range list')

    parser.add_argument('-q', '--quiet', action='store_true', help="don't show processing status")
    args = parser.parse_args()

    _main(vars(args))
