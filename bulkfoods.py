from collections import namedtuple
from functools import reduce
from fractions import Fraction

Order = namedtuple('Order', ['label', 'pmax', 'umax']);
OrderGroup = namedtuple('OrderGroup', ['labels', 'p', 'u'])
Bundle = namedtuple('Bundle', ['label', 'p', 'q'])
PersonalResult = namedtuple('PersonalResult', ['label', 'p', 'q', 'u'])
BundleResult = namedtuple('BundleResult', ['label', 'n', 'ptotal', 'qtotal'])


def bulkfoods(bundles, orders):
    # recursively try all affordable bundles
    pmax = sum([o.pmax for o in orders])
    bundle_counts, order_groups, _ = _try_all_larger_bundles(bundles, orders, [0 for _ in bundles], pmax)

    label_to_order = {}
    for o in orders:
        label_to_order[o.label] = o

    personal_results = []
    for g in order_groups:
        labels = sorted(g.labels, key=lambda l: label_to_order[l].pmax)
        p_remaining = g.p
        for i in range(len(labels)):
            labels_remaining = len(labels) - i
            label = labels[i]
            order = label_to_order[label]
            p_current = min(order.pmax, p_remaining / labels_remaining)
            p_remaining -= p_current
            personal_results.append(PersonalResult(label, p_current, p_current / g.u, g.u))
        assert abs(p_remaining) < 1e-2, p_remaining

    bundle_results = []
    for i in range(len(bundle_counts)):
        b = bundles[i]
        c = bundle_counts[i]
        if c > 0:
            bundle_results.append(BundleResult(b.label, c, b.p * c, b.q * c))

    return bundle_results, personal_results


def _try_all_larger_bundles(bundles, orders, bundle_counts, pmax):
    # test the current bundle counts
    cost = sum([b.p * c for (b, c) in zip(bundles, bundle_counts)])
    if cost > pmax:
        return None, None, 0
    best_quantity = sum([b.q * c for (b, c) in zip(bundles, bundle_counts)])
    best_groups = _bulkfoods(cost, best_quantity, orders)
    best_counts = None if best_groups is None else bundle_counts

    # test each count 1 larger, recursively
    # to avoid duplicate tests in subtrees, only increment indices starting with the last non-zero
    first_index = len(bundle_counts) - 1
    while first_index > 0 and bundle_counts[first_index] == 0:
        first_index -= 1
    for i in range(first_index, len(bundle_counts)):
        new_counts = bundle_counts[:]
        new_counts[i] += 1
        new_counts, new_groups, new_quantity = _try_all_larger_bundles(bundles, orders, new_counts, pmax)
        if new_groups and (
            best_groups is None or 
            best_groups[-1].u > new_groups[-1].u or 
            (best_groups[-1].u == new_groups[-1].u and new_quantity > best_quantity)
        ):
            best_groups = new_groups
            best_counts = new_counts
            best_quantity = new_quantity

    return best_counts, best_groups, best_quantity


# helper function used when a set of bundles has been selected, determining p_total and q_total
# produces the allocation of P and Q to (groups of) people
def _bulkfoods(p_total, q_total, orders):
    if q_total <= 0:
        return None

    # sort orders by max unit price
    orders = sorted(orders, key=lambda o: o.umax)

    # convert from orders to order groups so we can combine orders that are at the same unit price
    merge_groups = lambda g1, g2: g1._replace(labels=g1.labels + g2.labels, p=g1.p + g2.p, u=min(g1.u, g2.u))
    groups = []
    for o in orders:
        g = OrderGroup(labels=[o.label], p=o.pmax, u=o.umax)
        if groups and groups[-1].u == g.u:
            groups[-1] = merge_groups(groups[-1], g)
        else:
            groups.append(g)

    # Perform first sweep, to determine which groups are in on the purchase
    p_purchase = 0
    min_group = len(groups)
    for i in range(len(groups) -1, -1, -1):
        if p_purchase < p_total:
            min_group = i
        group_p = min(groups[i].p, p_total - p_purchase)
        groups[i] = groups[i]._replace(p=group_p)
        p_purchase += group_p
    if p_purchase < p_total:
        return None
    groups = groups[min_group:]

    # Perform second sweep, to determine the unit price paid by each group
    q_remaining = q_total
    p_remaining = p_total
    for i in range(len(groups)):
        u_group = min(p_remaining / q_remaining, groups[i].u)
        groups[i] = groups[i]._replace(u=u_group)
        p_remaining -= groups[i].p
        q_remaining -= groups[i].p / u_group
        if q_remaining < -1e-2:
            return None

    # Done!
    return groups


orders = [
    Order('a', Fraction('15'), Fraction('10')),
    Order('b', Fraction('20'), Fraction('10')),
    Order('mini_a', Fraction('10'), Fraction('7.4')),
#    Order('mini_b', 10, 9),
]

bundles = [
    Bundle('1lbs', Fraction('11.49'), Fraction('1')),
    Bundle('5lbs', Fraction('41.59'), Fraction('5')),
    Bundle('25lbs', Fraction('184.95'), Fraction('25')),
]

bundle_results, personal_results = bulkfoods(bundles, orders)
print("Bundles")
for br in bundle_results:
    print("\t{}\tn={}\tptotal={}\tqtotal={}".format(br.label, br.n, round(float(br.ptotal), 2), round(float(br.qtotal), 2)))
print()

print("Personal Results")
for pr in personal_results:
    print("\t{}\tp={}\tq={}\tu={}".format(pr.label, round(float(pr.p),2), round(float(pr.q), 2), round(float(pr.u),2)))
