from collections import namedtuple
from functools import reduce

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
def _bulkfoods(p_total, q_total, orders):
    # print('_bulkfoods {:.2f} {}'.format(p_total, q_total))
    DEBUG=False

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
    if (DEBUG): print("initial: ", groups)

    while True:
        # distribute excess quantity, if any
        extra_q = q_total - sum([g.p / g.u for g in groups])
        while extra_q > 0:
            g_last = groups[-1]
            q_last = g_last.p / g_last.u
            if len(groups) == 1:
                new_q_last = q_last + extra_q
                groups[-1] = g_last._replace(u=g_last.p / new_q_last)
                extra_q = 0
                if (DEBUG): print("q redistribute, add to only", groups)
            else:
                q_to_next_group = g_last.p / groups[-2].u - q_last
                if q_to_next_group <= extra_q:
                    extra_q -= q_to_next_group
                    new_q_last = q_to_next_group + q_last
                    groups[-1] = g_last._replace(u=g_last.p / new_q_last)
                    groups[-2] = merge_groups(groups[-2], groups[-1])
                    groups = groups[:-1]
                    if (DEBUG): print("q redistribute, merge", groups)
                else:
                    new_q_last = q_last + extra_q
                    groups[-1] = g_last._replace(u=g_last.p / new_q_last)
                    extra_q = 0
                    if (DEBUG): print("q redistribute, add to last", groups)

        # If there is excess payment...
        extra_p = sum([g.p for g in groups]) - p_total
        if extra_p > 1e-2:
            if p_total / q_total <= groups[0].u:
                labels = reduce(lambda a, b: a + b, [g.labels for g in groups], [])
                return [OrderGroup(labels, p_total, p_total/q_total)]
            elif len(groups) == 1:
                # This probably can't happen because of other checks in place, but just in case:
                # If there is only one group and the condition above doesn't trigger then no purchase can be made
                return None
            else:
                # If multiple groups then scale down p,q allocated to the lowest u group (holding u constant)
                # Reduce the price by min(extra_p, g.p, u * amount of price for amount of q to merge groups again)
                g_last = groups[-1]
                q_last = g_last.p / g_last.u
                q_to_next_merge = g_last.p / groups[-2].u - q_last
                p_to_next_merge = groups[0].u * q_to_next_merge
                dp = min(extra_p, groups[0].p, p_to_next_merge)
                extra_p -= dp
                groups[0] = groups[0]._replace(p=groups[0].p - dp)
                if dp >= groups[0].p:
                    groups = groups[1:]
                    if (DEBUG): print("p redistribute, destroy min u", groups)
                elif dp >= p_to_next_merge:
                    groups[-1] = g_last._replace(u=groups[-1].u)
                    groups[-2] = merge_groups(groups[-2], groups[-1])
                    groups = groups[:-1]
                    if (DEBUG): print("p redistribute, merge biggest groups", groups)
                else:
                    if (DEBUG): print("p redistribute, no structural change", groups)
        else:
            # no extra p --> if lacking p then return fail; if not then return groups
            if extra_p < -1e-2:
                return None
            else:
                return groups

orders = [
    Order('a', 15, 10),
    Order('b', 20, 10),
    Order('mini_a', 10, 7.4),
#    Order('mini_b', 10, 9),
]

bundles = [
    Bundle('1lbs', 11.49, 1),
    Bundle('5lbs', 41.59, 5),
    Bundle('25lbs', 184.95, 25),
]

bundle_results, personal_results = bulkfoods(bundles, orders)
print("Bundles")
for br in bundle_results:
    print("\t{}".format(br))
print()

print("Personal Results")
for pr in personal_results:
    print("\t{}".format(pr))

