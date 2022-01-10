#!/usr/bin/env python3

import argparse
import os
import roman
import regex
from typing import Tuple
from enum import Enum
from pathlib import Path

class NumFormat(Enum):
    NONE = 0
    ROMAN = 1
    ARABIC = 2
    TEXT = 3

class Options:
    source = NumFormat.NONE
    destination = NumFormat.NONE
    pattern = "{NUMBER}"
    regex_str = r"(\d+)"
    backup = False
    increment_value = 0  # 1 for increment, -1 for decrement, 0 for no change
    file_increment = False
    counter = 1

integers = []
ordinals = []


def prepareStringCompares():
    '''
    Prepares two large arrays with possible text values of numbers, 
    both integer (eg FIFTY-SIX) and ordinal (FIFTY-SIXTH).

    Note that this only covers numbers up to 99.

    We only need to call this if either the .source or .destination is TEXT.
    '''
    global integers
    global ordinals
    integers = ["","one","two","three","four","five","six","seven","eight","nine",
                    "ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen",
                    "eighteen","nineteen"]
    ordinals = ["","first","second","third","fourth","fifth","sixth","seventh","eighth","nineth",
                    "tenth","eleventh","twelfth","thirteenth","fourteenth","fifteenth","sixteenth","seventeenth",
                    "eighteenth","nineteenth"]
    decades = ["twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]
    orddecades = ["twentieth","thirtieth","fortieth","fiftieth","sixtieth","seventieth","eightieth","ninetieth"]
    for decade in decades: 
        integers.append(decade)
        ordinals.append(decade)
        for i in range(1, 10):
            integers.append(decade + "-" + integers[i])
            ordinals.append(decade + "-" + ordinals[i])
    
    # now have to fix up ordinals for exact decades
    for i in range(2, 10):
        ordinals[i * 10] = orddecades[i - 2]


def process_file(filename: Path, opts: Options):
    global file_increment_counter
    text_file = open(filename, "r")
    text_lines = text_file.readlines()
    if opts.backup:
        make_backup(filename, text_lines)
    new_lines = []
    pattern = regex.compile(opts.regex_str)
    for text_line in text_lines:
        for match in pattern.finditer(text_line):
            stringval = match.group(1)
            if opts.source == NumFormat.ARABIC:
                found_value = int(stringval) # should only be found if it WAS an integer
                text_line = transform_integer(opts, found_value, text_line, stringval)
            elif opts.source == NumFormat.ROMAN:
                # stringval may or may not be a valid roman numeral
                found_value, ok = get_roman(stringval)               
                if ok:
                    text_line = transform_integer(opts, found_value, text_line, stringval)
            elif opts.source == NumFormat.TEXT:
                found_value, ok = convert_text(stringval.lower())
                if ok:
                    text_line = transform_integer(opts, found_value, text_line, stringval)
        new_lines.append(text_line)
    # write out altered file
    text_file = open(filename, "w")
    text_file.writelines(new_lines)
    text_file.flush()
    text_file.close()

def make_backup(filename, text_lines):
    backname = Path(filename.parent, filename.stem + ".bak")
    back_file = open(backname, "w")
    back_file.writelines(text_lines)
    back_file.flush()
    back_file.close()
    back_file.close()

def convert_text(numstr: str) -> Tuple[int, bool]:
    numstr = numstr.replace(" ", "-")
    if numstr in integers:
        return integers.index(numstr), True
    elif numstr in ordinals:
        return ordinals.index(numstr), True
    else:
        return -1, False

def get_roman(romstr: str) -> Tuple[int, bool]:
    try:
        intval = roman.fromRoman(romstr)
        return intval, True
    except roman.InvalidRomanNumeralError:
        return "", False


def is_integer(found_str) -> bool:
    try:
        num = int(found_str)
        return True
    except ValueError:
        return False


def transform_integer(opts: Options, num: int, text_line: str, textnum: str = "") -> str:
    if opts.file_increment:
        num = opts.counter
        opts.counter += opts.increment_value  # may be zero, -1 or +1
    else:  # ordinary increment/decrement
        num += opts.increment_value  # may be zero, -1 or +1
    if opts.destination == NumFormat.ROMAN:
        romstr = roman.toRoman(num)
        text_line = text_line.replace(textnum, romstr, 1)
    elif opts.destination == NumFormat.ARABIC:
        text_line = text_line.replace(textnum, str(num), 1)
    elif opts.destination == NumFormat.TEXT:
        if num < len(integers):
            strval = integers[num].upper()
            text_line = text_line.replace(textnum, strval, 1)
    return text_line


def main():
    parser = argparse.ArgumentParser(description="Find numeric information in text files and apply transformation.")
    parser.add_argument('-f', '--from', dest='from_format', type=str, default='roman', help='source format (roman, arabic, text)')
    parser.add_argument('-t', '--to', dest='to_format', type=str, default='arabic', help='destination format (roman, arabic, text)')
    parser.add_argument('-b', '--backup', action='store_true', help='create a backup file')
    parser.add_argument('-i', '--increment', action='store_true', help='increment the value found by 1')
    parser.add_argument('-g', '--increment_global', action='store_true', help='increment the found value for each file')
    parser.add_argument('-d', '--decrement', action='store_true', help='decrement the value found by 1')
    parser.add_argument('-p', "--pattern", dest='pattern', type=str, default='<h2>CHAPTER {NUMBER}</h2>',
                        help='pattern for where to find the number. angle brackets and quotes must be escaped')
    parser.add_argument("directory", metavar="DIRECTORY", help="source directory to process")
 
    # directory = "/Users/david/OneDrive/Standard Ebooks/TEMP/author-name_title-of-book"

    args = parser.parse_args()
    
    options = Options()
    if args.from_format[0] in ['R','r']:
        options.source = NumFormat.ROMAN
    elif args.from_format[0] in ['A','a']:
        options.source = NumFormat.ARABIC
    elif args.from_format[0] in ['T','t']:
        options.source = NumFormat.TEXT

    if args.to_format[0] in ['R','r']:
        options.destination = NumFormat.ROMAN
    elif args.to_format[0] in ['A','a']:
        options.destination = NumFormat.ARABIC
    elif args.to_format[0] in ['T','t']:
        options.destination = NumFormat.TEXT

    if args.backup:
        options.backup = True
    
    if args.increment:
        options.increment_value = 1
    if args.decrement:
        options.increment_value = -1

    if args.increment_global:
        options.file_increment = True
        if args.decrement:
            options.increment_value = -1
        else:
            options.increment_value = 1


    if options.destination == options.source and options.increment_value == 0:
        # nothing to do
        print("Destination format is the same as source format, and no increment requested, so there's nothing to do")
        return  

    options.pattern = args.pattern

    if options.source == NumFormat.ARABIC:
        options.regex_str = options.pattern.replace('{NUMBER}', r'(\d+)')
    elif options.source == NumFormat.ROMAN:
        options.regex_str = options.pattern.replace('{NUMBER}', r'([IVXLCM]+)')
    elif options.source == NumFormat.TEXT:
        options.regex_str = options.pattern.replace('{NUMBER}', r'([A-Za-z\- ]+)')

    if args.directory:
        directory = args.directory

    if options.source == NumFormat.TEXT or options.destination == NumFormat.TEXT:
        prepareStringCompares()

    file_list = []

    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = Path(root,filename)
            if ".git" not in root:
                print(filepath)
                if filepath.suffix in [".txt", ".html", ".xhtml", ".md"]:
                    file_list.append(filepath)

    file_list.sort()
    for f in file_list:
        process_file(f, options)

if __name__ == '__main__':
    main()
