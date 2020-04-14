# All quantities in oz, all prices in USD. Quantities are restricted to being integer multiples of 1 oz to make this a linear program.

# Details aside, this program maximizes the quantity purchased, and secondarily
# minimizes the highest unit price anyone pays, while respecting everyone's
# budget and unit price constraints.

set bundles;
set people;

###############################################################################
# Parameters from bulkfoods.com:
#   For each bundle, i:
#     q_i = quantity, for one order of bundle i
#     p_i = price, for one order of bundle i
param q{i in bundles};
param p{i in bundles};
#   Minimum budle cost = min_i(p_i/q_i)
param u_min_bundle;


###############################################################################
# Parameters from individuals:
#   For each person j:
#     bj = budget j has allocated
#     uj = max unit price j is willing to pay
param b{j in people};
param u{j in people};


###############################################################################
# Variables
#   For each bundle, i:
#      The number of bundle i to purchase
var N{i in bundles}, integer, >= 0;
#   For each person j:
#     Qj = quantity purchased by j
#     Pj = total price paid by j
var Q{j in people}, integer, >= 0;
var P{j in people}, >= 0, <= b[j];
#     Breakdowns of the above, to make this problem linear:
#       Qozjk = integer; 1 if j purchases at least k oz; 0 if not
#       Pozjk = price paid for oz k
set oz_nums := {1 .. 80};
var Qoz{j in people, k in oz_nums}, binary;
var Poz{j in people, k in oz_nums}, >= 0, <= u[j];
#     U_max_person = max(Pozjk), the most money per unit paid by any person
var U_max_person, >= 0;


###############################################################################
# Maximize quantity purchased; secondarily minimize max unit price paid, then minimize the maximum quantity that a single person has
maximize obj: sum{j in people} Q[j] - 1e-2 * U_max_person - 1e-5 * sum{j in people, k in oz_nums} Qoz[j,k] * k;


###############################################################################
# Subject To:
#   Personal quantity and price are the same expressed in parts and in total:
s.t. quantity{j in people}: sum{k in oz_nums} Qoz[j,k] = Q[j];
s.t. price{j in people}:    sum{k in oz_nums} Poz[j,k] = P[j];

#   Unit price for oz k is 0 if quantity k is 0
s.t. qzero{j in people, k in oz_nums}: Poz[j,k] * 1e-3 <= Qoz[j,k];

#   Unimportant ordering on Q_oz_j_k to make the solution more stable:
s.t. oz_ordering {j in people, k in oz_nums diff {1}}: Qoz[j,k-1] >= Qoz[j,k];

#   Purchase quantity = sum(quantity distributed to all people)
s.t. purchase_quantity: sum{j in people} Q[j] = sum{i in bundles} N[i] * q[i];

#   Purchase price = sum(price for all people)
s.t. purchase_price:    sum{j in people} P[j] = sum{i in bundles} N[i] * p[i];

#   Max unit price paid by anyone >= unit price paid by any one person
s.t. unit_max{j in people, k in oz_nums}: U_max_person >= Poz[j,k];



###############################################################################
# Solve and print!
solve;

printf "Order bundles:\n";
for {i in bundles} {
  printf "\tBundle %10s\tNumber %2d\tTotal Quantity %1.2f (lbs)\tTotal Cost %3.2f\n", i, N[i], N[i]*q[i]/16, N[i]*p[i];
}
printf "\n";

printf "Personal breakdown:\n";
for {j in people} {
  printf "\tPerson %10s\tQuantity (oz) %2d\tQuantity (lbs) %1.2f\tCost %.2f\tCost/lbs %.2f\n", j, Q[j], Q[j]/16, P[j], P[j]/Q[j]*16;
}

end;
