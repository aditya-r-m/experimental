# [ Reference ]
#  Publication : The Hungarian Method for the assignment problem (& follow-ups)
#              - Kuhn, Munkres, Edmonds, Karp, Tomizawa
#  Streamlined : Assignment Problem and Hungarian Algorithm
#              - Topcoder

from math import inf
from queue import Queue

# The function expects a square matrix of integers
# The value at row 'x' & column 'y' is the cost of matching
# -> node 'x' in left partition 'X'
# -> node 'y' in right partition 'y'
# The function returns total cost in a minimum-cost-matching, assignments, & labels
def hungarian(cost_matrix):
    n = len(cost_matrix)
    lx, ly = [0] * n, [0] * n
    xy, yx = [None] * n, [None] * n

    # Every iteration of the following loop constructs an alternating tree.
    # -> The root is some arbitrary unmatched node in 'X'.
    # -> The tree alternates between nodes in 'X' & 'Y'.
    # -> The tree alternates between "matched" & "unmatched" edges.
    # Every iteration ends with flipping of some augmenting path to add root to the matching.
    while True:
        root = None

        # check if matching complete
        for x in range(n):
            if xy[x] is None:
                root = x
                break
        if root is None: break

        # exposed vertex in 'Y' which connects to 'root' via alternating path of 'tight' edges
        ay = None

        # queue for BFS & sets for storing visited alternating tree nodes
        q, zxs, zys = Queue(), set(), set()
        zxs.add(root)
        q.put(root)

        # grandchild->grandparent mapping among nodes in 'X' contained in the alternating tree
        prevx = [None] * n

        # slack measures the smallest difference between cost & label-sums for a given node in 'Y'
        yslack = [inf] * n
        yslackx = [None] * n # alternating tree node 'x' in 'X' for which 'y' has smallest slack

        while ay is None:

            # BFS to contruct alternating tree of 'tight' edges
            while not q.empty():
                x = q.get()

                # Check if the new 'x' in alternating tree provides the minimum slack for some 'y'
                for y in range(n):
                    new_slack = cost_matrix[x][y] - (lx[x] + ly[y])
                    if new_slack < yslack[y]:
                        yslack[y] = new_slack
                        yslackx[y] = x

                for y in range(n):
                    # Traverse all the 'tight' edges extending from the new 'x'
                    if lx[x] + ly[y] == cost_matrix[x][y]:
                        if yx[y] is None:
                            # augmenting leaf found in 'Y'
                            ay = y
                            break
                        if y not in zys:
                            # extend the alternating tree
                            zys.add(y)
                            zxs.add(yx[y])
                            q.put(yx[y])
                            prevx[yx[y]] = x

                if ay is not None: break
            if ay is not None: break

            # No augmenting path has been found, so we update the labels with min slack
            # This new labeling (finds an augmenting path OR extends the BFS) with new tight edges
            delta = inf
            for y in range(n):
                if y not in zys: delta = min(delta, yslack[y])
            for x in zxs: lx[x] += delta
            for y in zys: ly[y] -= delta
            for y in range(n):
                if y not in zys:
                    # update the slack according to the label change
                    yslack[y] -= delta
                    if yslack[y] == 0:
                        if yx[y] is None:
                            # augmenting leaf found in 'Y'
                            ay = y
                            break
                        # add newly reached 'matched' edge to the alternating tree
                        zys.add(y)
                        zxs.add(yx[y])
                        q.put(yx[y])
                        prevx[yx[y]] = yslackx[y]

        # Augmenting path found, flip the alternating matched/unmatched edges
        # starting at 'ay', going up to the root
        ax = yslackx[ay]
        while ax is not None:
            axn, ayn = prevx[ax], xy[ax]
            xy[ax], yx[ay] = ay, ax
            ax, ay = axn, ayn
    return sum(lx) + sum(ly), xy, lx, ly


print(hungarian([[4, 2, 5], [5, 3, 4], [6, 0, 7]]))


