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

import argparse
from .linkture import _available_languages, __app__, __version__, Scriptures
from ast import literal_eval


def main(args):

    def switchboard(text):
        if args['l'] is not None:
            prefix = '<a href="'
            suffix = '">'
            if len(args['l']) > 1 and args['l'][1] != '':
                suffix = args['l'][1]
            if len(args['l']) > 0 and args['l'][0] != '':
                prefix = args['l'][0]
            return s.link_scriptures(text, prefix, suffix)
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

    s = Scriptures(language=args['language'], translate=args['translate'], form=form, separator=args['s'], upper=args['u'], verbose=(not args['q']))

    if args['f']:
        if args['o'] and (args['o'] == args['f']):
            print('Make sure in-file and out-file are different!\n')
            exit()
        with open(args['f'], 'r', encoding='UTF-8') as f:
            txt = f.read()
    else:
        txt = args['r']

    if args['cc']:
        txt = s.code_chapter(args['cc'])
    elif args['cv']:
        txt = s.code_verse(args['cv'])
    elif args['sv']:
        txt = s.serial_verse_number(args['sv'])
    elif args['sc']:
        txt = s.serial_chapter_number(args['sc'])
    elif args['bn']:
        txt = s.book_name(args['bn'])
    elif txt:
        txt = switchboard(txt)
    else:
        print(parser.format_help())
        exit()

    if args['o']:
        with open(args['o'], 'w', encoding='UTF-8') as f:
            f.write(str(txt))
    else:
        print(txt)


parser = argparse.ArgumentParser(description="PARSE and PROCESS BIBLE SCRIPTURE REFERENCES: extract, tag, link, rewrite, translate, BCV-encode and decode. See README for more information")

parser.add_argument('-v', action='version', version=f"{__app__} {__version__}", help='show version and exit')
parser.add_argument('-q', action='store_true', help="don't show errors")

function_group = parser.add_argument_group('data source (one required - except for auxiliary functions, which only take command-line arguments)', 'choose between terminal or file input:')
mode = function_group.add_mutually_exclusive_group()
mode.add_argument('-f', metavar='in-file', help='get input from file (UTF-8)')
mode.add_argument('-r', metavar='reference', help='process "reference; reference; etc."')
parser.add_argument('-o', metavar='out-file', help='output file (terminal output if not provided)')

parser.add_argument('--language', default='English', choices=_available_languages, help='indicate source language for book names (English if unspecified)')
parser.add_argument('--translate', choices=_available_languages, help='indicate output language for book names (same as source if unspecified)')
parser.add_argument('-s', metavar='separator', default=' ', help='segment separator (space by default)')
parser.add_argument('-u', action='store_true', help='capitalize (upper-case) book names')
format_group = parser.add_argument_group('output format (optional)', 'if provided, book names will be rewritten accordingly:')
formats = format_group.add_mutually_exclusive_group()
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

aux_group = parser.add_argument_group('auxiliary functions')
aux = aux_group.add_mutually_exclusive_group(required=False)
aux.add_argument('-sc', metavar=('BCV'), help='return the serial number (1-1189) of the chapter with code "BCV" ("bbcccvvv")')
aux.add_argument('-sv', metavar=('BCV'), help='return the serial number (1-31194) of the verse with code "BCV" ("bbcccvvv")')
aux.add_argument('-cv', metavar=('verse'), help='return the BCV code for serial verse number "verse" (integer value)')
aux.add_argument('-cc', metavar=('chapter'), help='return the BCV range for serial chapter number "chapter" (integer value)')
aux.add_argument('-bn', metavar=('book'), help='return the name of book number "book" (integer value)')

args = parser.parse_args()
main(vars(args))
