#!/usr/bin/env python3

"""
File:           linkture module

Description:    Process Bible references and convert them into jwpub links

MIT License     Copyright (c) 2022 Eryk J.

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

VERSION = '1.1.0'


from pathlib import Path
import argparse, re, sqlite3
import pandas as pd


def main(args):

    def replacement(match):
        group = match.group(1).strip('{}')
        if args['verbose']:
            print(f'\n...processing: "{group}"')
        # return str(s.code_scripture(group))
        return s.link_scripture(group)

    with open(args['infile'], 'r') as f:
        txt = f.read()
    s = Scriptures()
    txt2 = re.sub(m, replacement, txt)
    with open(args['outfile'], 'w', encoding='UTF-8') as f:
        f.write(txt2)


class Scriptures():

    def __init__(self):
        self.bn = {}
        path = Path(__file__).resolve().parent
        con = sqlite3.connect(path / 'res/bbooks.db')
        cur = con.cursor()
        for row in cur.execute("SELECT * FROM Books;").fetchall():
            for item in row[1].split(','):
                self.bn[item.replace(' ', '').replace('.', '').upper()] = row[0]
        self.br = pd.read_sql("SELECT Book, Chapter, Last FROM Ranges;", con)
        cur.close()
        con.close()
        self.bk_ref = re.compile(r'(\d?\s*[a-zA-Z]+\.?)(.*)', re.IGNORECASE)
        self.ch_v_ch_v = re.compile(r'(\d+)\s*:\s*(\d+)\s*[-\u2013\u2014]\s*(\d+)\s*:\s*(\d+)')
        self.ch_v_v = re.compile(r'(\d+)\s*:\s*(\d+)\s*[-\u2013\u2014]\s*(\d+)')
        self.ch_v = re.compile(r'(\d+)\s*:\s*(\d+)')
        self.ch_ch = re.compile(r'(\d+)\s*[-\u2013\u2014]\s*(\d+)')
        self.ch_ = re.compile(r'(\d+)')
        self.v_v = re.compile(r'(?=(\d+\s*),(\s*\d+))')
        self.vv = re.compile(r'(?<!:)(\d+)\s*-\s*(\d+)')

    def check_book(self, book):
        bk = book.upper().replace(' ', '').replace('.', '')
        if bk not in self.bn:
            return None, None
        else:
            book = self.bn[bk]
        return self.br.loc[(self.br.Book == book) & (self.br.Chapter.isnull()), ['Book', 'Last']].values[0]

    def process_scripture(self, scripture):
        result = self.bk_ref.search(scripture)
        if result:
            bk, rest = result.group(1), result.group(2).lstrip()
            bn, last = self.check_book(bk)
            if not bn:
                return None, None, None, -1
            if rest == "":
                vss = self.br.loc[(self.br.Book == bn) & (self.br.Chapter == last), ['Last']].values[0][0]
                rest = f"1:1-{last}:{vss}"
            for result in self.v_v.findall(rest):
                if int(result[1]) - int(result[0]) == 1:
                    rest = rest.replace(f"{result[0]},{result[1]}", f"{result[0].rstrip()}-{result[1].lstrip()}")
            if bn:
                return f"{bk} ", rest, bn, last
        return None, None, None, None

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
            for result in self.ch_v_ch_v.findall(txt):
                if result[0] == result[2]:
                    txt = txt.replace(f"{result[0]}:{result[1]}-{result[2]}:{result[3]}", f"{result[0]}:{result[1]}-{result[3]}")
            for result in self.vv.findall(txt):
                if int(result[1]) - int(result[0]) == 1:
                    txt = txt.replace(f"{result[0]}-{result[1]}", f"{result[0]}, {result[1]}")
            return txt

        url = ''
        book = ''
        for chunk in scripture.split(';'):
            bk, rest, bn, last = self.process_scripture(chunk)
            if last == -1:
                url = url + '; ' + '{{' + chunk.strip() + '}}'
                continue
            if not bn:
                bk, rest, bn, last = self.process_scripture(book + chunk)
                bk = ''
            chap = 0
            book = bk
            for bit in rest.split(','):
                if chap:
                    link, chap = process_verses(f"{chap}:{bit}", bn, last-1)
                    url += ', '
                else:
                    link, chap = process_verses(bit, bn, last-1)
                    url += '; '
                processed_chunk = f"{bk}{undo_series(bit).lstrip()}"
                if len(chunk) < (len(bk) + len(bit)):
                    url += f'<a href="jwpub://b/NWTR/{link}" class="b">{chunk.strip()}</a>'
                else:
                    url += f'<a href="jwpub://b/NWTR/{link}" class="b">{processed_chunk}</a>'
                bk = ''
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
            bk, rest, bn, last = self.process_scripture(chunk)
            if last == -1:
                continue
            if not bn:
                bk, rest, bn, last = self.process_scripture(book + chunk)
                bk = ''
            chap = 0
            book = bk
            for bit in rest.split(','):
                if chap:
                    link, chap = code_verses(f"{chap}:{bit}", bn, last-1)
                else:
                    link, chap = code_verses(bit, bn, last-1)
                series.append(link)
                bk = ''
        return series


if __name__ == "__main__":
    PROJECT_PATH = Path(__file__).resolve().parent
    APP = Path(__file__).stem
    parser = argparse.ArgumentParser(description="Convert scriptures marked wih {{scripture}} to jwpub links.")
    parser.add_argument('-v', '--version', action='version', version=f"{APP} {VERSION}")
    parser.add_argument('--verbose', action='store_true', help='show scriptures being processed')
    parser.add_argument("infile", help='file to process')
    parser.add_argument("outfile", help='output file')
    args = parser.parse_args()
    if vars(args)['infile'] == vars(args)['outfile']:
        print('Make sure the outfile is different from the infile!\n')
        exit()
    m = re.compile(r'({{.*?}})')
    main(vars(args))
