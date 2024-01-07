# [ Reference ]
#  Publication : A New Approach to the Maximum Flow Problem
#              - Goldberg & Tarjan
#  Streamlined : Push–relabel maximum flow algorithm
#              - Wikipedia
#  Streamlined : A New Approach to the Maximum Flow Problem
#              - Topcoder

from math import inf
from queue import Queue
from collections import defaultdict

def preflow_push(capacity):
    n = len(capacity)
    preflow = [[0] * n for _ in range(n)]
    label, excess, cur_arc = [0] * n, [0] * n, [0] * n

    def residual_capacity(i, j):
        return capacity[i][j] - preflow[i][j]

    def admissible_capacity(i, j):
        if label[i] != label[j] + 1: return 0
        return residual_capacity(i, j)

    def push(i, j):
        f = min(excess[i], admissible_capacity(i, j))
        if f:
            preflow[i][j] += f
            preflow[j][i] -= f
            excess[i] -= f
            excess[j] += f
        return f

    def relabel(i):
        nxt_label = inf
        for j in range(n):
            if residual_capacity(i, j):
                nxt_label = min(nxt_label, label[j])
        if nxt_label < inf: label[i] = 1 + nxt_label

    q = Queue()

    label[0], excess[0] = 1, inf
    for j in range(1, n):
        if push(0, j) and j < n-1: q.put(j)
    label[0] = n

    def discharge(i):
        while excess[i]:
            if push(i, cur_arc[i]) and cur_arc[i] > 0 and cur_arc[i] < n-1: q.put(cur_arc[i])
            cur_arc[i] += 1
            if cur_arc[i] == n:
                cur_arc[i] = 0
                relabel(i)

    while not q.empty(): discharge(q.get())

    return excess[-1], preflow

print(preflow_push([
    defaultdict(lambda: 0, { 1: 16, 2: 13 }),
    defaultdict(lambda: 0, { 3: 12 }),
    defaultdict(lambda: 0, { 1: 4, 4: 14 }),
    defaultdict(lambda: 0, { 2: 9, 5: 20 }),
    defaultdict(lambda: 0, { 3: 7, 5: 4 }),
    defaultdict(lambda: 0),
]))
