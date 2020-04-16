from fractions import Fraction

from bulkfoods.bulkfoods import Order, print_bulkfoods
from bulkfoods.examples.bundles import bundles


if __name__ == "__main__":
    orders = [
        Order('A', Fraction('15'), Fraction('12')),
        Order('B', Fraction('20'), Fraction('12')),
    ]

    print_bulkfoods(bundles, orders)
