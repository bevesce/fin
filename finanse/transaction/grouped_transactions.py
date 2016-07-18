from ..money import GroupedMoney
from ..grouped import Grouped, GroupedMonoid


class GroupedTransactions(Grouped, GroupedMonoid):
    @staticmethod
    def zero():
        from .transactions import Transactions
        return Transactions()

    def __str__(self):
        return '\n\n'.join(
            str(k) + ':\n' + str(self[k])
            for k in self.groups()
        )

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
