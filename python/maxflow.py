# python3

from queue import Queue
from math import inf

'''
The function takes an NxN adjacency matrix representing the capacity of edges in the graph.
Vertex 0 is assumed to be the source & Vertex -1 is assumed to be the sink.
If there is no edge from 'i' to 'j', capacity[i][j] == 0.
'''
def preflow_push(capacity):
    n = len(capacity)
    preflow = [[0] * n for _ in range(n)]
    label, excess = [0] * n, [0] * n

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
        j = 0
        while excess[i]:
            if push(i, j) and j > 0 and j < n-1: q.put(j)
            j += 1
            if j == n:
                j = 0
                relabel(i)

    while not q.empty(): discharge(q.get())

    return excess[-1], preflow


