from . import Money
from . import currency

from config import notes_path

currency.setup_cache(notes_path + '/currency.json')


class AppliedTagsHierarchy:
    def __init__(self, tag, transactions, children, is_exclusive):
        self.parent = None
        self.tag = tag
        self.transactions = transactions
        self.children = children
        self.is_exclusive = is_exclusive
        for c in self.children:
            c.parent = self

    def __iter__(self):
        yield self
        for c in self.children:
            for sc in c:
                yield sc

    def __str__(self):
        parts = []
        for c in self:
            parts.append(' ' * c.get_level() + c.tag if c.tag else '')
        return '\n'.join(parts)

    def get_level(self):
        level = 0
        node = self
        while node.parent:
            if node.parent.tag:
                level += 1
            node = node.parent
        return level

    def format_tag(self):
        if self.is_exclusive:
            return self.tag
        return '*{}*'.format(self.tag)


class TagsHierarchy:
    @staticmethod
    def parse(description):
        return TagsHierarchyParser(description).run()

    def __init__(self, description=None, tag=None, children=None):
        if description:
            tag, children = TagsHierarchy.parse(description)
        self.tag = tag.strip() if tag else tag
        if self.tag and self.tag.startswith('- '):
            self.tag = self.tag[2:]
        if self.tag and self.tag.startswith('*') and self.tag.endswith('*'):
            self.tag = self.tag[1:-1]
            self.is_exclusive = False
        else:
            self.is_exclusive = True
        self._children = children or []
        self.parent = None
        for c in self._children:
            c.parent = self

    def __str__(self):
        level = self.get_level()
        tag_str = self.tag if self.is_exclusive else '*{}*'.format(self.tag)
        return '\n'.join(
            ([level * '    ' + '- ' + tag_str] if self.tag else [])
            + [str(c) for c in self._children]
        )

    def get_level(self):
        level = 0
        node = self
        while node.parent:
            if node.parent.tag:
                level += 1
            node = node.parent
        return level

    def append_child(self, child):
        child.parent = self
        self._children.append(child)

    def get_exclusive_tags(self):
        exclusive_tags = set()
        if self.is_exclusive and self.tag:
            exclusive_tags.add(self.tag)
        for child in self._children:
            for tag in child.get_exclusive_tags():
                exclusive_tags.add(tag)
        return exclusive_tags

    def get_tags(self):
        tags = set()
        if self.tag:
            tags.add(self.tag)
        for child in self._children:
            for tag in child.get_tags():
                tags.add(tag)
        return tags

    def apply(self, transactions):
        children = [
                c.apply(transactions.filter(self.get_sub_qeury(c))) for c in self._children
        ]
        not_query = 'not ({})'.format(self.get_children_query())
        not_sum = transactions.filter(not_query).sum()
        # if not_sum > Money():
        children.append(AppliedTagsHierarchy('?', transactions.filter(not_query), [], is_exclusive=True))
        return AppliedTagsHierarchy(
            tag=self.tag,
            transactions=transactions.filter(self.get_query()) if self.tag else transactions,
            children=children,
            is_exclusive=self.is_exclusive
        )

    def format_transactions(self, transactions, currency=None):
        parts = []
        for c in self.apply(transactions):
            if not c.tag:
                continue
            total = c.transactions.sum()
            if currency:
                total = total.convert(currency)
            if c.tag == '?' and total == Money():
                continue
            parts.append('    ' * c.get_level() + '- {}: {}'.format(
                c.format_tag(), total
            ))
        return '\n'.join(parts)

    def format_tag(self):
        if self.is_exclusive:
            return self.tag
        return '*{}*'.format(self.tag)

    def get_sub_qeury(self, child):
        if not self.tag:
            return child.get_query()
        query = ''
        exclusive_tags = child.get_exclusive_tags()
        if exclusive_tags:
            query += ' or '.join(exclusive_tags)
        tags = child.get_tags()
        if tags:
            if query:
                query += ' or '
            query += '({} and ({}))'.format(self.tag, ' or '.join(tags))
        return query

    def get_query(self):
        tags = self.get_exclusive_tags()
        if self.tag:
            tags.add(self.tag)
        query = ' or '.join(tags)
        return query

    def get_children_query(self):
        if not self.tag:
            return ' or '.join(c.get_query() for c in self._children)
        if not self._children:
            return self.tag
        query = ''
        exclusive_tags = set()
        for c in self._children:
            for tag in c.get_exclusive_tags():
                exclusive_tags.add(tag)
        if exclusive_tags:
            query = '({})'.format(' or '.join(exclusive_tags))
        tags = set()
        for c in self._children:
            for tag in c.get_tags():
                tags.add(tag)
        if tags:
            if query:
                query += ' or '
            query += '({} and ({}))'.format(self.tag, ' or '.join(tags))
        return query


class TagsHierarchyParser:
    class Tag:
        def __init__(self, line):
            self.tag = line.lstrip()

    class Indent:
        pass

    class Dedent:
        pass


    def __init__(self, description):
        self.description = description
        self.tokenize()

    def tokenize(self):
        self.lines = [l for l in self.description.splitlines() if l and not l.startswith('//')]
        self.tokens = []
        self.indent_levels = [0]
        for line in self.lines:
            self._handle_indentation(line)
            self.tokens.append(TagsHierarchyParser.Tag(line))

    def _handle_indentation(self, line):
        indent_levels = self.indent_levels
        current_level = self.get_line_level(line)
        if current_level > indent_levels[-1]:
            indent_levels.append(current_level)
            self.tokens.append(TagsHierarchyParser.Indent())
        elif current_level < indent_levels[-1]:
            while current_level < indent_levels[-1]:
                indent_levels.pop()
                self.tokens.append(TagsHierarchyParser.Dedent())


    def run(self):
        self.collected = []
        self.items_in_parsing = []
        self.levels = [0]
        new_item = None
        for token in self.tokens:
            if isinstance(token, TagsHierarchyParser.Indent):
                self.items_in_parsing.append(new_item)
            elif isinstance(token, TagsHierarchyParser.Dedent):
                self.items_in_parsing.pop()
            else:
                new_item = TagsHierarchy(tag=token.tag)
                if self.items_in_parsing:
                    self.items_in_parsing[-1].append_child(new_item)
                else:
                    self.collected.append(new_item)
        return None, self.collected

    def get_line_level(self, line):
        return len(line) - len(line.lstrip())
