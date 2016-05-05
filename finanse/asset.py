from .money import Money
from .money import CategorizedMoney


class Assets:
    def __init__(self, assets):
        if isinstance(assets, str):
            assets = self._parse(assets)
        self._assets = assets

    def _parse(self, text):
        result = {}
        split = text.split('#')[1:]
        for subcategory in split:
            lines = subcategory.splitlines()
            title = lines[0].strip()
            result[title] = CategorizedMoney('\n'.join(lines[1:]).strip())
        return result

    def __getitem__(self, category):
        return self._assets[category]

    def __str__(self):
        return '\n\n'.join(
            '# {}\n{}'.format(k, v) for k, v in self._assets.items()
        )

    def sum(self):
        return sum((c.sum() for c in self.subcategories()), Money())

    def subcategories(self):
        return self._assets.values()
