# Optimizing bulk foods orders

Scenario: a group of people want to order cheap food (from bulkfoods.com, or
similar). Bulkfoods offers food in different bundle sizes (say 1lbs, 5lbs,
25lbs), where larger quantities come at cheaper unit cost. We want cheap food,
but don't want to store a huge supply of it.

bulkfoods.py takes as input people's requests (in the form of "I'll spend up to
<pmax> USD at any unit price up to <umax> USD/lbs") and the available bundles
and computes the purchase that minimizes the maximum unit price paid by any
individual. It then outputs the order that should be placed, the quantity that
each person should receive, and the amount they should pay for it.

For example, suppose cinnamon is available in bundles of 1 lbs for $11.49 or 5
lbs for $41.49. People A and B allocate budgets of $15 and $20 respectively, at
a maximum unit price of $12/lbs. The most efficient purchase is 3 units of 1
lbs of cinnamon, distributed as follows:

(python3 bulkfoods/examples/ab_no_c.py)

> a p=15.00 q=1.31 u=11.49
> b p=19.47 q=1.69 u=11.49

But what if C also wants to buy cinnamon, and allocates $10 at a maximum unit
price of $7.5/lbs? The new optimal solution is to buy a 5 lbs unit of cinnamon,
distributed as follows:

(python3 bulkfoods/examples/abc.py)

> a p=15.00 q=1.77 u=8.49
> b p=20.00 q=2.36 u=8.49
> c p= 6.59 q=0.88 u=7.5

Note that C is paying less than A and B per unit pound (notably at C's maximum
unit price per pound). Additionally, Even more surprising, C's unit price is
actually less than price for the 5 lbs purchase! But dispite this unfairness, A
and B pay a lower price than they would in the scenario  without C
participating in the purchase. Everyone wins.

Tl;dr: optimizing this sort of thing can be counter-intuitive, but that's what
algorithms are for. Buy cheap bulk foods with your friends!
