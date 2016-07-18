from collections import defaultdict


class Grouped:
    def __init__(self, groups):
        self._groups = groups

    def __len__(self):
        return len(self._groups)

    def __getitem__(self, key):
        return self._groups[key]

    def __iter__(self):
        for group in self.groups():
            yield group

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if set(self._groups.keys()) != set(self._groups.keys()):
            return False
        for k in self._groups.keys():
            if self[k] != other[k]:
                return False
        return True

    def __str__(self):
        return '\n'.join(
            '{}: {}'.format(k, v) for k, v in self.items()
        )

    def get(self, key, value=None):
        try:
            return self[key]
        except KeyError:
            if value:
                return value
            if hasattr(self, 'zero'):
                return self.zero()
            return None

    def groups(self):
        return sorted(self._groups.keys())

    def items(self):
        for group in self.groups():
            yield group, self[group]

    def values(self):
        for group in self.groups():
            yield self[group]


class GroupedFunctor:
    def map(self, f):
        return self.__class__({
            k: f(v) for k, v in self._groups.items()
        })


class GroupedMonoid:
    def __add__(self, other):
        result = defaultdict(self.zero)
        for group, amount in self.items():
            result[group] += amount
        for group, amount in other.items():
            result[group] += amount
        return self.__class__(dict(result))


class GroupedCommutativeMonoid(GroupedMonoid):
    def __sub__(self, other):
        result = defaultdict(self.zero)
        for group, amount in self.items():
            result[group] += amount
        for group, amount in other.items():
            result[group] -= amount
        return self.__class__(dict(result))
