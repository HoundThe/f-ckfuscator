import re
import lexer
import os

header_to_symbol_cache = {}


def get_standard_path(hdr_name: str):
    xxx = '/usr/lib64/clang/10.0.1/include:/usr/include/:/usr/local/include/'
    x = xxx.split(':')
    for path in x:
        if os.path.exists(os.path.join(path, hdr_name)):
            return os.path.join(path, hdr_name)


# Now only works for <> headers and linux
def follow_includes(header_name: str) -> set:
    path = get_standard_path(header_name)
    if path is None:
        return set()

    if path not in header_to_symbol_cache:
        print(header_name, path)
        header_to_symbol_cache[path] = set()
        with open(os.path.join(path)) as file:
            tokens = list(lexer.tokenize(file.read()))
            headers = get_headers(tokens)
            for hdr in headers:
                header_to_symbol_cache[path].update(follow_includes(hdr))
    print(header_to_symbol_cache[path])
    return header_to_symbol_cache[path]


def get_headers(tokens: list):
    """
    Processes every #include and gets the header name
    """
    headers = []
    for tok in tokens:
        match = re.match(r"(?:\s)*#(?:\s)*include", tok)
        if match:
            # headers are either inside <> or ""
            x = re.search(r'(?:<[^>]*>)|(?:"[^"]*")', tok)
            if x:
                start, end = x.span()
                hdr_name = tok[start+1:end-1]
                headers.append(hdr_name)
    return headers


def get_header_symbols(tokens: list):
    """
    Gets all symbols from tokenized C header 

    It's very naive, doesn't understand the syntax
    so it ignores all ifdef and ifndefs etc.
    """

    # We don't want duplicates
    symbols = set()

    # We want #define <identifier> symbols (macros and constants)
    for idx, tok in enumerate(tokens):
        match = re.match(r"(?:\s)*#(?:\s)*define", tok)
        if match:  # preprocessor token
            start, end = match.span()
            # tokenize the single line
            tmp = lexer.tokenize(tok[end:])
            for kkk in tmp:
                if lexer.is_identifier(kkk):
                    symbols.add(kkk)
        if tok == '(':  # function definition
            i = 1
            while idx - i != 0:
                if lexer.is_identifier(tokens[idx-i]):
                    symbols.add(tokens[idx-i])
                    break
                i += 1
        if tok == 'typedef':
            i = 1
            while idx + i != len(tokens):
                if lexer.is_identifier(tokens[idx+i]) and \
                        lexer.is_identifier(tokens[idx+i+1]):
                    symbols.add(tokens[idx+i+1])
                    break
                i += 1
    return symbols
