from .money import Money
from ..grouped import Grouped, GroupedFunctor, GroupedCommutativeMonoid


class GroupedMoney(Grouped, GroupedFunctor, GroupedCommutativeMonoid):
    @staticmethod
    def zero():
        return Money()

    def money(self):
        return self.values()

    def sum(self):
        return sum(self.money(), Money())
