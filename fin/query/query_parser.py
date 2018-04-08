from collections import namedtuple
from ..exceptions import QueryParseError
from .query import Binary
from .query import Unary
from .query import Atom

QueryToken = namedtuple('QueryToken', ('type', 'value'))

def parse_query(text):
    return QueryParser().run(text)


class QueryParser:
    PRECEDENCE = {
        "or": 2,
        "and": 3,
        "<": 7, ">": 7, "<=": 7, ">=": 7,
        "=": 7, "!=": 7, "$=": 7, "^=": 7, "*=": 7
    }

    def run(self, text):
        self.text = text
        self.tokens = QueryLexer().run(text)
        return self.maybe_binary(self.parse_atom(), 0)

    def pick(self):
        return self.tokens[0]

    def pop(self):
        return self.tokens.pop(0)

    def is_eof(self):
        return not self.tokens

    def is_operator(self):
        if self.is_eof():
            return False
        token = self.pick()
        if (token.type == 'operator'):
            return token
        return False

    def is_not(self):
        token = self.pick()
        return token.type == 'operator' and token.value == 'not'

    def is_atom(self):
        return self.pick().type in set([
            'tag', 'keyword', 'string'
        ])

    def is_open(self):
        token = self.pick()
        return token.type == 'punctuation' and token.value == '('

    def is_close(self):
        if self.is_eof():
            return False
        token = self.pick()
        return token.type == 'punctuation' and token.value == ')'

    def maybe_binary(self, left, precedence):
        token = self.is_operator()
        if (token):
            try:
                token_precedence = QueryParser.PRECEDENCE[token.value]
            except KeyError:
                raise_parse(self.text, "invalid operator '{}'".format(token.value))
            if token_precedence > precedence:
                self.pop()
                right = self.maybe_binary(self.parse_atom(), token_precedence)
                binary = Binary(token, left, right)
                return self.maybe_binary(binary, precedence)
        return left

    def parse_atom(self):
        if self.is_eof():
            raise_parse(self.text, 'unexpected end of query')
        if self.is_not():
            return Unary(self.pop(), self.parse_atom())
        elif self.is_atom():
            return Atom(self.pop())
        elif self.is_open():
            return self.parse_parenthesises()
        elif self.is_close():
            raise_parse(self.text, 'unbalanced parenthesis')
        raise_parse(self.text, 'missing expression')

    def parse_parenthesises(self):
        self.pop()
        result = self.maybe_binary(self.parse_atom(), 0)
        self.pop_close()
        return result

    def pop_close(self):
        if not self.is_close():
            raise_parse(self.text, 'unbalanced parenthesis')
        self.pop()



def raise_parse(text, message):
    raise QueryParseError(
        "can't parse '{}': {}".format(text, message)
    )

class QueryLexer:
    def run(self, text):
        self.chars = list(text)
        self.tokens = []
        while not self.is_eof():
            c = self.pick()
            if self.is_whitespace(c):
                self.pop()
                continue
            if self.is_punctuation(c):
                self.push(self.read_punctuation())
            elif self.is_string_start(c):
                self.push(self.read_string())
            elif self.is_operator_start(c):
                self.push(self.read_operator())
            else:
                self.push(self.read_identifier())
        return list(self.clean_up(self.tokens))

    def pick(self):
        return self.chars[0]

    def pop(self):
        return self.chars.pop(0)

    def is_eof(self):
        return not self.chars

    def push(self, token):
        self.tokens.append(token)

    def is_keyword(self, text):
        return text in set([
            'date', 'money', 'currency'
        ])

    def is_operator(self, text):
        return text in set([
            '<', '<=', '=', '!=', '=>', '>', '^=', '$=', '*='
        ])

    def is_whitespace_operator(self, text):
        return text in set([
            'and', 'or', 'not',
        ])

    def is_operator_start(self, text):
        return text in '><=!^$*'

    def is_operator_continuation(self, text):
        return text in '=>'

    def is_punctuation(self, text):
        return text in '()'

    def is_whitespace(self, text):
        return text in ' \t\n'

    def is_string_start(self, text):
        return text in '"\''

    def read_punctuation(self):
        return QueryToken('punctuation', self.pop())

    def read_operator(self):
        first = self.pop()
        if not self.is_eof() and self.is_operator_continuation(self.pick()):
            second = self.pop()
        else:
            second = ''
        return QueryToken('operator', first + second)

    def read_identifier(self):
        word = ''
        c = self.pick()
        word = self.read_while(
            lambda c: (
                self.is_eof() or
                self.is_operator_start(c) or
                self.is_whitespace(c) or
                self.is_punctuation(c)
            )
        )
        if self.is_keyword(word):
            return QueryToken('keyword', word)
        elif self.is_whitespace_operator(word):
            return QueryToken('operator', word)
        return QueryToken('tag', word)

    def read_string(self):
        how_opened = self.pop()
        word = self.read_while(lambda c: c == how_opened)
        if self.is_eof():
            raise QueryParseError(
                "can't parse query: " + 'unexpected end of query'
            )
        self.pop()
        return QueryToken('string', word)

    def read_while(self, f):
        word = ''
        if self.is_eof():
            return word
        c = self.pick()
        while not f(c):
            word += self.pop()
            if self.is_eof():
                return word
            c = self.pick()
        return word

    def clean_up(self, tokens):
        previous = None
        for token in tokens:
            if previous and previous.type == 'tag' and token.type == 'tag':
                yield QueryToken('operator', 'and')
            yield token
            previous = token
