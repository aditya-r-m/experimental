from queue import Queue

# bi_graph = [
#     [7,4,3,],
#     [3,1,2,],
#     [3,0,0,],
# ]
bi_graph = [
    [4,88,70,68,],
    [57,59,43,11],
    [33,79,41,73],
    [46,16,66,39]
]
n, mm = len(bi_graph), 0
lx, ly = [max(bi_graph[x]) for x in range(n)], [0] * n
xy, yx = [None] * n, [None] * n
slack, slackx = [0] * n, [-1] * n
s, t = set(), set()
prev = [None] * n

def print_state(i):
    print('id', i)
    print('lx', lx)
    print('ly', ly)
    print('xy', xy)
    print('yx', yx)
    print('s', s)
    print('t', t)
    print('slack', slack)
    print('slackx', slackx)
    print('-----')

def update_labels():
    global mm, lx, ly, xy, yx, slack, slackx, s, t, prev
    delta = min(slack[y] for y in set(range(n)).difference(t))
    for y in t: ly[y] += delta
    for y in set(range(n)).difference(t): slack[y] -= delta

def add_to_tree(x, prevx):
    global mm, lx, ly, xy, yx, slack, slackx, s, t, prev
    s.add(x)
    prev[x] = prevx
    for y in range(n):
        new_slack = lx[x] + ly[y] - bi_graph[x][y]
        if new_slack < slack[y]: slack[y], slackx[y] = new_slack, x

def augment():
    global mm, lx, ly, xy, yx, slack, slackx, s, t, prev
    if mm == n: return
    prev, q = [None] * n, Queue()
    s, t = set(), set()
    for x in range(n):
        if xy[x] is None:
            root, prev[x] = x, None
            q.put(root)
            break
    for y in range(n): slack[y], slackx[y] = lx[root] + ly[y] - bi_graph[root][y], root
    ax, ay = None, None
    while True:
        while not q.empty():
            x = q.get()
            for y in range(n):
                if bi_graph[x][y] == lx[x] + ly[y] and y not in t:
                    if yx[y] is None:
                        ax, ay = x, y
                        break
                    t.add(y)
                    q.put(yx[y])
                    add_to_tree(yx[y], x)
            if ay is not None: break
        if ay is not None: break
        update_labels()
        for y in range(n):
            if y not in t and not slack[y]:
                if yx[y] is None:
                    ax, ay = slackx[y], y
                    break
                t.add(y)
                if yx[y] not in s:
                    q.put(yx[y])
                    add_to_tree(yx[y], slackx[y])
        if ay is not None: break
    if ay is not None:
        mm += 1
        while ax is not None:
            ty = xy[ax]
            xy[ax], yx[ay] = ay, ax
            ax, ay = prev[ax], ty
        augment()


augment()
sol = 0
for x, y in enumerate(xy):
    print(x, '->', y)
    sol += bi_graph[x][y]
print('total value', sol)
