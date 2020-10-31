import re
import lexer


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
