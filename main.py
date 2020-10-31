#!/usr/bin/env python3

"""
TODO list
    - implement cache
"""

import lexer
import random
import symbol_parser as sym
import os
import os.path

header_cache = {}
extern_symbols = set()
# Maps every identifier to a unique swear word
word_map = {}
header_symbol_cache = {}


def is_c_file(filename: str) -> bool:
    return filename.endswith('.h') or filename.endswith('.c')


def get_swear_word() -> str:
    bad_words = open('bad-words.txt').read().splitlines()
    random.shuffle(bad_words)
    for word in bad_words:
        yield word


def get_c_files() -> list:
    c_files = []
    for path, subdirs, files in os.walk('.'):
        for name in files:
            if is_c_file(name):
                c_files.append(os.path.join(path, name))
    return c_files


def get_identifiers(tokens: list) -> list:
    identifiers = []
    for tok in tokens:
        if lexer.is_identifier(tok) and tok not in extern_symbols:
            identifiers.append(tok)
    return identifiers


def map_identifiers_to_swear_words(identifiers: list):
    swear_word_gen = get_swear_word()
    for idr in identifiers:
        if idr not in word_map:
            word_map[idr] = next(swear_word_gen)


def create_new_file(tokens: list):
    for idx, tok in enumerate(tokens):
        if lexer.is_identifier(tok) and tok not in extern_symbols:
            tokens[idx] = word_map[tok]
    return ''.join(tokens)


c_files = get_c_files()
print(len(c_files))

for filename in c_files:
    with open(filename) as file:
        tokens = list(lexer.tokenize(file.read(), False))

        headers = sym.get_headers(tokens)
        for hdr in headers:
            extern_symbols.update(sym.follow_includes(hdr))

        print(extern_symbols)
        identifiers = get_identifiers(tokens)

        map_identifiers_to_swear_words(identifiers)

        result = create_new_file(tokens)
        # print(result, end='')
