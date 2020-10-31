#!/usr/share/env python3

import re

# http://www.open-std.org/jtc1/sc22/wg14/www/docs/n1256.pdf 6.4.1
keywords = [
    'auto', 'break', 'case', 'char',
    'const', 'continue', 'default',
    'do', 'double', 'else', 'enum',
    'extern', 'float', 'for', 'goto',
    'if', 'inline', 'int', 'long',
    'register', 'restrict', 'return',
    'short', 'signed', 'sizeof',
    'static', 'struct', 'switch',
    'typedef', 'union', 'unsigned',
    'void', 'volatile', 'while',
    '_Alignas', '_Atomic', '_Bool',
    '_Complex', '_Generic', '_Imaginary',
    '_Noreturn', '_Static_assert', '_Thread_local',
    'size_t'
]

# punctuators are pretty much delimiters in C,
# sorted, include by some preprocessor ones
punctuators = [
    '%:%:', '>>=', '<<=', '...', '||', '|=', '^=', '>>', '>=', '==',
    '<=', '<<', '<:', '<%', ':>', '/=', '->', '-=', '--', '+=', '++',
    '*=', '&=', '&&', '%>', '%=', '%:', '##', '!=', '~', '}', '|', '{',
    '^', ']', '[', '?', '>', '=', '<', ';', ':', '/', '.', '-', ',',
    '+', '*', ')', '(', '&', '%', '#', '!', '\\'
]


def group(*choices): return '(' + '|'.join(choices) + ')'
def maybe(*choices): return group(*choices) + '?'


IntNumberSuffix = r'(?:(?:LL)|(?:ll)|[uUlL])?'
Hexnumber = r'0[xX](?:[0-9a-fA-F])+' + IntNumberSuffix
Binnumber = r'0[bB](?:[01])+' + IntNumberSuffix
Octnumber = r'0(?:[0-7])+' + IntNumberSuffix
Decnumber = r'0|[1-9](?:[0-9])*' + IntNumberSuffix

IntConstant = group(Hexnumber, Binnumber, Octnumber, Decnumber)

Exponent = r'[eE][-+]?[0-9](?:_?[0-9])*'
Pointfloat = group(r'[0-9](?:_?[0-9])*\.(?:[0-9](?:_?[0-9])*)?',
                   r'\.[0-9](?:_?[0-9])*') + maybe(Exponent)
Expfloat = r'[0-9](?:_?[0-9])*' + Exponent
Floatnumber = group(Pointfloat, Expfloat)


token_regexes = {
    'Whitespace':  r'([ \f\t\r\n]+)',
    'Extra': r'(\\\r?\n|\Z)',
    'Comment1': r'(//[^\r\n]*)',
    'Comment2': r"(/\*[^*]*\*+(?:[^/*][^*]*\*+)*/)",
    'Preprocessor': r'(#[^\r\n]*)',
    'String': group(r'"[^\n"\\]*(?:\\.[^\n"\\]*)*"',
                    r"'[^\n'\\]*(?:\\.[^\n'\\]*)*'"),
    'Number': group(Floatnumber, IntConstant),
    'Identifier': r'([_a-zA-Z]\w*)',
    'Punctuator': group(*[re.escape(pun) for pun in punctuators]),
}

# Join all regexes into single one
Tokens = group(*list(token_regexes.values()))


def tokenize(code: str, ignore_whitespace=True) -> str:
    """
    Basic tokenizes for purposes of the f-ckfusactor
    It splits the code into substrings of unidentified
    tokens, to deal with preprocessor, every line starting
    with # is a separate token

    TODO: understand digraphs and trigraphs aswell
    """
    pos = 0
    max = len(code)
    while pos != max:
        match = re.compile(Tokens).match(code, pos)
        if match:
            if ignore_whitespace and match.group(2):
                start, end = match.span(2)
                pos = end
                continue
            start, end = match.span(1)
            pos = end
            yield code[start:end]
        else:
            print(code)
            raise Exception('Unexpected token:')


def is_identifier(string: str) -> bool:
    return string not in keywords and re.match(token_regexes['Identifier'], string)
