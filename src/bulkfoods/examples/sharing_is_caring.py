from fractions import Fraction

from bulkfoods.bulkfoods import Order, print_bulkfoods
from bulkfoods.examples.bundles import bundles


if __name__ == "__main__":
    # In this example, it is optimal for 5lbs to be purchased and for the
    # maximum unit price paid to be the order unit price. But within those
    # constraints there are multiple posibilities -- A could get all of the
    # food, or A and B could share the order. Sharing is caring!
    orders = [
        Order('A', Fraction('42'), Fraction('12')),
        Order('B', Fraction('20'), Fraction('11')),
        Order('C', Fraction('10'), Fraction('7.5')),
    ]

    print_bulkfoods(bundles, orders)
