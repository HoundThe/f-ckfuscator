#!/usr/bin/env python3

"""
TODO list
    - implement cache
"""

import lexer
import random
import os
import os.path

header_cache = {}
extern_symbols = set()
# Maps every identifier to a unique swear word
word_map = {}


def get_standard_path(hdr_name: str):
    xxx = '/usr/lib64/clang/10.0.1/include:/usr/include/:/usr/local/include/'
    x = xxx.split(':')
    for path in x:
        if os.path.exists(os.path.join(path, hdr_name)):
            return os.path.join(path, hdr_name)


# Now only works for <> headers and linux
def follow_includes(header_name: str):
    symbols = set()
    path = get_standard_path(header_name)
    # print(f'{path} - {header_name}')
    with open(os.path.join(path)) as file:
        tokens = list(lexer.tokenize(file.read()))
        headers = get_headers(tokens)
        for hdr in headers:
            symbols.update(follow_includes(hdr))
        symbols.update(get_header_symbols(tokens))
    # print(f'Symbols of {header_name}\n{symbols}')
    return symbols


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

for filename in c_files:
    with open(filename) as file:
        tokens = list(lexer.tokenize(file.read(), False))

        headers = get_headers(tokens)
        for hdr in headers:
            extern_symbols.update(follow_includes(hdr))

        identifiers = get_identifiers(tokens)

        map_identifiers_to_swear_words(identifiers)

        result = create_new_file(tokens)
        print(result, end='')
