from fractions import Fraction

from bulkfoods.bulkfoods import Order, print_bulkfoods
from bulkfoods.examples.bundles import bundles


if __name__ == "__main__":
    orders = [
        Order('a', Fraction('15'), Fraction('12')),
        Order('b', Fraction('20'), Fraction('12')),
        Order('c', Fraction('10'), Fraction('7.5')),
    ]

    print_bulkfoods(bundles, orders)
