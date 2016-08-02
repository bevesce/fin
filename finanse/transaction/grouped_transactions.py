from ..money import GroupedMoney
from ..grouped import Grouped, GroupedMonoid


class GroupedTransactions(Grouped, GroupedMonoid):
    @staticmethod
    def zero():
        from .transactions import Transactions
        return Transactions()

    def __str__(self, indent=0):
        lines = []
        indent_style = '  '
        for key in self.groups():
            lines.append(indent * indent_style + str(key) + ':')
            value = self[key]
            if isinstance(value, GroupedTransactions):
                lines.append(value.__str__(indent + 1))
            else:
                for t in value:
                    lines.append((indent + 1) * indent_style + str(t))
        return '\n'.join(lines)

    def __repr__(self):
        return str(self)

    def map(self, f):
        return GroupedTransactions({
            k: v.map(f) for k, v in self._groups.items()
        })

    def filter(self, f):
        return GroupedTransactions({
            k: v.filter(f) for k, v in self._groups.items()
        })

    def sum(self):
        return GroupedMoney({
            k: v.sum() for k, v in self._groups.items()
        })

    def group(self, key):
        return GroupedTransactions({
            k: v.group(key) for k, v in self._groups.items()
        })

    def transactions(self):
        return self.values()
