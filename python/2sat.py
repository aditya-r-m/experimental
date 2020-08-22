#uses python3

import sys
import threading

# This code is used to avoid stack overflow issues
sys.setrecursionlimit(10**6) # max depth of recursion
threading.stack_size(2**26)  # new thread will get stack of such size

n, m = map(int, input().split())
# element in the list clauses of the form [i, j] represents a 2SAT CNF clause ..AND(xi OR xj)AND..
# +i represents xi. -i represents ¬xi.
clauses = [ list(map(int, input().split())) for i in range(m) ]

def dfs(graph, visited, current, order):
    visited[current] = True
    for nxt in graph[current]:
        if not visited[nxt]:
            dfs(graph, visited, nxt, order)
    order.append(current)
    return order

def toposort(graph):
    r = []
    visited = [False] * len(graph)
    for v in range(-n, 1 + n):
        if v and not visited[v]:
            r += dfs(graph, visited, v, [])
    return r

def isSatisfiable():
    result = [True] * n
    graph = [[] for _ in range(2 * n + 1)]
    rev_graph = [[] for _ in range(2 * n + 1)]
    for a, b in clauses:
        graph[-a].append(b)
        rev_graph[b].append(-a)
        graph[-b].append(a)
        rev_graph[a].append(-b)
    order = toposort(rev_graph)[::-1]
    visited = [False] * len(graph)
    assigned = [False] * len(graph)
    for u in order:
        if not visited[u]:
            reachable = set(dfs(graph, visited, u, []))
            for x in reachable:
                if -x in reachable:
                    return None
                if not assigned[x]:
                    assigned[x] = assigned[-x] = True
                    if x < 0: result[(-x) - 1] = False
    return result


def main():
    result = isSatisfiable()
    if result is None:
        print("UNSATISFIABLE")
    else:
        print("SATISFIABLE");
        print(" ".join(str(-i-1 if not result[i] else i+1) for i in range(n)))

# This is to avoid stack overflow issues
threading.Thread(target=main).start()
