from ..money import Money
from ..exceptions import TransactionParseError
from ..exceptions import MoneyParseError
import datetime



DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT_LENGTH = len('2016-01-01')


def parse_transaction(text):
    def parse_date_from_prefix(date_and_rest):
        try:
            date_string = date_and_rest[:DATE_FORMAT_LENGTH]
            date = datetime.datetime.strptime(date_string, DATE_FORMAT)
        except ValueError:
            raise_transaction_parse('date', date_string)
        return date, date_and_rest[DATE_FORMAT_LENGTH:]

    def parse_money_from_postfix(rest_and_money):
        split = rest_and_money.split(' ')
        try:
            return Money(split[-1]), ' '.join(split[:-1]).strip()
        except:
            try:
                money_string = split[-2] + ' ' + split[-1]
                return Money(money_string), ' '.join(split[:-2]).strip()
            except:
                raise_transaction_parse('money', money_string + ' or ' + split[-1])

    def raise_transaction_parse(name, what, message=None):
        raise TransactionParseError(
            "can't parse '{}' as {} from '{}'".format(
                what, name, text
            )
        )

    def parse_tags(text):
        return TagsParser().run(text)

    date, rest = parse_date_from_prefix(text)
    money, rest = parse_money_from_postfix(rest)
    tags = parse_tags(rest)
    return date, tags, money


class TagsLexer:
    def run(self, text):
        self._text = text
        self._tokens = ['']
        self._parenthesis_counter = 0

        for c in self._text:
            if c == ' ' or c == '\t':
                self._tokenize_whitespace(c)
            elif c == '(':
                self._tokenize_left_parenthesis(c)
            elif c == ')':
                self._tokenize_right_parenthesis(c)
            else:
                self._tokenize_character(c)
        return [t for t in self._tokens if t]

    def add_token(self, token):
        self._tokens.append(token)

    def is_top_level(self):
        return self._parenthesis_counter == 0

    def _tokenize_whitespace(self, c):
        if self.is_top_level():
            self.add_token('')
        else:
            self._tokenize_character(c)

    def _tokenize_left_parenthesis(self, c):
        if self.is_top_level():
            self.add_token('(')
            self.add_token('')
        else:
            self._tokenize_character(c)
        self._parenthesis_counter += 1

    def _tokenize_right_parenthesis(self, c):
        self._parenthesis_counter -= 1
        if self.is_top_level():
            self.add_token(')')
            self.add_token('')
        else:
            self._tokenize_character(c)

    def _tokenize_character(self, c):
        self._tokens[-1] += c


class TagsParser:
    def run(self, text):
        self.tokens = TagsLexer().run(text)
        self.tags = {}
        self.parse_tags()
        return self.tags

    def pick(self):
        return self.tokens[0]

    def pop(self):
        return self.tokens.pop(0)

    def is_eof(self):
        return not self.tokens

    def is_word(self):
        return self.pick() != '(' and self.pick() != ')'

    def parse_tags(self):
        if not self.is_eof():
            self.parse_tag()
            self.parse_tags()

    def parse_tag(self):
        tag = self.pop_word()
        parameter = None
        if not self.is_eof() and self.pick() == '(':
            parameter = self.pop_parameter()
        self.tags[tag] = parameter

    def pop_word(self):
        if self.is_word():
            return self.pop()
        raise Exception(text)

    def pop_parameter(self):
        self.pop()
        word = self.pop_word()
        self.pop_close()
        return word

    def pop_close(self):
        if self.pick() == ')':
            return self.pop()
        raise Exception(text)
