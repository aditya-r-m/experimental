class AVLTree():
    total_nodes = 0

    def __init__(self, value, left=None, right=None):
        self.value = value
        self.id = AVLTree.total_nodes
        AVLTree.total_nodes += 1
        self._left = self._right = self._parent = None
        self._height = 1
        self._size = 1
        self._annotation = False
        self._subtree_annotation = False
        self._link_left(left)
        self._link_right(right)

    @staticmethod
    def height(tree):
        return 0 if tree is None else tree._height

    @staticmethod
    def size(tree):
        return 0 if tree is None else tree._size

    @staticmethod
    def subtree_annotation(tree):
        return False if tree is None else tree._subtree_annotation

    def _update_subtree_annotation(self):
        self._subtree_annotation = self._annotation or\
            any(map(AVLTree.subtree_annotation, [self._left, self._right]))
        return self

    def set_annotation(self, flag):
        if self._annotation == flag: return
        self._annotation = flag
        cur_node = self
        while cur_node is not None:
            cur_node._update_subtree_annotation()
            cur_node = cur_node._parent

    def annotated_nodes(self, result=None):
        if result is None: result = []
        if AVLTree.subtree_annotation(self._left): self._left.annotated_nodes(result)
        if self._annotation: result.append(self)
        if AVLTree.subtree_annotation(self._right): self._right.annotated_nodes(result)
        return result

    def _update_stats(self):
        self._height = 1 + max(map(AVLTree.height, [self._left, self._right]))
        self._size = 1 + sum(map(AVLTree.size, [self._left, self._right]))
        return self._update_subtree_annotation()

    @staticmethod
    def balance_factor(tree):
        if tree is None: return 0
        return AVLTree.height(tree._left) - AVLTree.height(tree._right)

    def _link_left(self, new_left):
        if self._left != new_left:
            AVLTree._cut_parent(self._left)
            AVLTree._cut_parent(new_left)
            self._left = new_left
            if new_left is not None: new_left._parent = self
        self._update_stats()
        return self

    def _link_right(self, new_right):
        if self._right != new_right:
            AVLTree._cut_parent(self._right)
            AVLTree._cut_parent(new_right)
            self._right = new_right
            if new_right is not None: new_right._parent = self
        self._update_stats()
        return self

    @staticmethod
    def _cut_parent(node):
        if node is not None and node._parent is not None:
            if node._parent._left == node:
                node._parent._left = None
                node._parent._update_stats()
            if node._parent._right == node:
                node._parent._right = None
                node._parent._update_stats()
            node._parent = None
        return node

    def _rotateR(self):
        child = self._left
        self._link_left(child._right)
        child._link_right(self)
        self._update_stats()
        child._update_stats()
        return child

    def _rotateL(self):
        child = self._right
        self._link_right(child._left)
        child._link_left(self)
        self._update_stats()
        child._update_stats()
        return child

    @staticmethod
    def _merge_left(left, mid, right):
        if AVLTree.height(left) > AVLTree.height(right) + 1:
            left._link_right(AVLTree._merge_left(left._right, mid, right))
            if AVLTree.balance_factor(left) < -1:
                if AVLTree.balance_factor(left._right) < 0: return left._rotateL()
                return left._link_right(left._right._rotateR())._rotateL()
            return left
        return mid._link_left(left)._link_right(right)

    @staticmethod
    def _merge_right(left, mid, right):
        if AVLTree.height(right) > AVLTree.height(left) + 1:
            right._link_left(AVLTree._merge_right(left, mid, right._left))
            if AVLTree.balance_factor(right) > 1:
                if AVLTree.balance_factor(right._left) > 0: return right._rotateR()
                return right._link_left(right._left._rotateL())._rotateR()
            return right
        return mid._link_left(left)._link_right(right)

    @staticmethod
    def merge(left, mid, right):
        mid._link_left(None)._link_right(None)
        if AVLTree.height(left) > AVLTree.height(right) + 1:
            return AVLTree._cut_parent(AVLTree._merge_left(left, mid, right))
        if AVLTree.height(right) > AVLTree.height(left) + 1:
            return AVLTree._cut_parent(AVLTree._merge_right(left, mid, right))
        return mid._link_left(left)._link_right(right)

    @staticmethod
    def push_front(node, tree):
        return AVLTree.merge(None, node, tree)

    @staticmethod
    def push_back(tree, node):
        return AVLTree.merge(tree, node, None)

    @staticmethod
    def split(mid):
        if mid is None: return None, None, None
        cur_mid, ancestor_splits = mid, []
        while cur_mid._parent is not None:
            cur_mid, cut_left = cur_mid._parent, (cur_mid != cur_mid._parent._left)
            ancestor_splits.append((cur_mid, cut_left))
        [node, left, right] = map(AVLTree._cut_parent, [mid, mid._left, mid._right])
        for (cur_mid, cut_left) in ancestor_splits:
            AVLTree._cut_parent(cur_mid)
            if cut_left: left = AVLTree.merge(AVLTree._cut_parent(cur_mid._left), cur_mid, left)
            else: right = AVLTree.merge(right, cur_mid, AVLTree._cut_parent(cur_mid._right))
        return left, node, right

    @staticmethod
    def pop_front(tree):
        assert tree is not None
        leftmost = tree
        while leftmost._left is not None: leftmost = leftmost._left
        return AVLTree.split(leftmost)[1:]

    @staticmethod
    def pop_back(tree):
        assert tree is not None
        rightmost = tree
        while rightmost._right is not None: rightmost = rightmost._right
        return AVLTree.split(rightmost)[:2]

    @staticmethod
    def get(tree, index):
        if tree is None or index < 0: return None
        lsize = AVLTree.size(tree._left)
        if lsize > index: return AVLTree.get(tree._left, index)
        if lsize == index: return tree
        return AVLTree.get(tree._right, index - (1+lsize))

    @staticmethod
    def inorder(tree, traversal=None):
        if traversal is None: traversal = []
        if tree is not None:
            AVLTree.inorder(tree._left, traversal)
            traversal.append(tree.value)
            AVLTree.inorder(tree._right, traversal)
        return traversal

    @staticmethod
    def render(node, offset=None):
        if offset is None: offset = ''
        if node is None:
            print(offset, 'Empty')
            return
        print(offset, 'node id', node.id)
        print(offset, 'node value', node.value)
        print(offset, 'node annotation', node._annotation)
        print(offset, 'tree annotation', node._subtree_annotation)
        print(offset, 'tree height', node._height)
        print(offset, 'tree size', node._size)
        print(offset, 'tree balance', AVLTree.balance_factor(node))
        if node._parent is not None:
            print(offset, 'parent id', node._parent.id)
        if node._left is not None:
            print(offset, 'left subtree')
            AVLTree.render(node._left, offset + '  ')
        if node._right is not None:
            print(offset, 'right subtree')
            AVLTree.render(node._right, offset + '  ')

def run_avl_tree_tests():
    from random import randint, choice

    def validate_structure(tree):
        if tree is None: return
        validate_structure(tree._left)
        validate_structure(tree._right)
        assert tree._subtree_annotation == tree._annotation or\
            any(map(AVLTree.subtree_annotation, [tree._left, tree._right]))
        assert tree._height == 1 + max(map(AVLTree.height, [tree._left, tree._right]))
        assert tree._size == 1 + sum(map(AVLTree.size, [tree._left, tree._right]))
        assert tree._parent is None or tree._parent._left == tree or tree._parent._right == tree
        assert AVLTree.balance_factor(tree) in [-1,0,1]

    l = 1<<10

    tree = None
    for j in range(l):
        tree = AVLTree.push_back(tree, AVLTree(j))
        validate_structure(tree)
    assert AVLTree.inorder(tree) == list(range(l))

    values = []
    while tree is not None:
        tree, node = AVLTree.pop_back(tree)
        validate_structure(tree)
        values.append(node.value)
    assert values == list(range(l-1, -1, -1))

    tree = None
    for j in range(l-1, -1, -1): tree = AVLTree.push_front(AVLTree(j), tree)
    validate_structure(tree)
    assert AVLTree.inorder(tree) == list(range(l))

    values = []
    while tree is not None:
        node, tree = AVLTree.pop_front(tree)
        validate_structure(tree)
        values.append(node.value)
    assert values == list(range(l))

    tree_list = list(map(lambda v: AVLTree(v), range(l)))

    for tree in tree_list[::1<<4]: tree.set_annotation(True)

    while len(tree_list) > 1:
        m = randint(0, len(tree_list)-2)
        tree = AVLTree.merge(tree_list[m], AVLTree(-1), tree_list[m+1])
        validate_structure(tree)
        tree_list = tree_list[:m] + [tree] + tree_list[m+2:]
    assert list(filter(lambda x: x >= 0, AVLTree.inorder(tree))) == list(range(l))

    assert list(map(lambda x: x.value, tree.annotated_nodes())) == list(range(0, l, 1<<4))

    for node in tree.annotated_nodes(): node.set_annotation(False)

    assert list(map(lambda x: x.value, tree.annotated_nodes())) == []

    while True:
        try: i = \
        choice(list(map(lambda p: p[0], filter(lambda p: p[1].value == -1, enumerate(tree_list)))))
        except: break
        left, _, right = AVLTree.split(tree_list[i])
        validate_structure(left)
        validate_structure(right)
        tree_list = tree_list[:i] + [left, right] + tree_list[i+1:]
    assert list(map(lambda t: t.value, tree_list)) == list(range(l))

    print('AVL Tree tests finished!')


class EulerTourForest():
    def __init__(self):
        self._edge_map = dict()

    def _insert_node(self, v):
        if (v, v) not in self._edge_map:
            self._edge_map[v, v] = AVLTree((v, v))

    def _get_avl_root(self, u, v):
        if (u, v) not in self._edge_map: return None
        current_node = self._edge_map[u, v]
        while current_node._parent is not None: current_node = current_node._parent
        return current_node

    def _get_root(self, u, v):
        if (u, v) not in self._edge_map: return None
        current_node = self._get_avl_root(u, v)
        while current_node._left is not None: current_node = current_node._left
        return current_node

    def set_annotation(self, u, flag):
        self._insert_node(u)
        self._edge_map[u, u].set_annotation(flag)

    def annotated_nodes(self, u):
        self._insert_node(u)
        return list(map(lambda n: n.value[0], self._get_avl_root(u, u).annotated_nodes()))

    def size(self, u):
        self._insert_node(u)
        avl_size = AVLTree.size(self._get_avl_root(u, u))
        return (avl_size + 1) >> 1

    def get_root(self, u):
        return None if self._get_root(u, u) is None else self._get_root(u, u).value[0]

    def linked(self, u, v):
        return (u, v) in self._edge_map

    def connected(self, u, v):
        self._insert_node(u)
        self._insert_node(v)
        return self._get_root(u, u) is not None and self._get_root(u, u) == self._get_root(v, v)

    def make_root(self, v):
        self._insert_node(v)
        if self._get_root(v, v).value == (v, v): return
        root_node, _ = AVLTree.pop_front(self._get_avl_root(v, v))
        left, new_root_node, right = AVLTree.split(self._edge_map[v, v])
        AVLTree.push_front(new_root_node, AVLTree.merge(right, root_node, left))

    def link(self, u, v):
        self._insert_node(u)
        self._insert_node(v)
        if (u, v) in self._edge_map: return
        assert not self.connected(u, v)
        self.make_root(u)
        self.make_root(v)
        self._edge_map[u, v] = AVLTree((u, v))
        self._edge_map[v, u] = AVLTree((v, u))
        AVLTree.push_back(\
            AVLTree.merge(\
                self._get_avl_root(u, u), self._edge_map[u, v], self._get_avl_root(v, v)),\
            self._get_avl_root(v, u))

    def cut(self, u, v):
        self._insert_node(u)
        self._insert_node(v)
        if (u, v) not in self._edge_map: return
        assert u != v
        self.make_root(u)
        left, down_link, _ = AVLTree.split(self._edge_map[u, v])
        _, up_link, right = AVLTree.split(self._edge_map[v, u])
        left, mid = AVLTree.pop_back(left)
        AVLTree.merge(left, mid, right)
        del self._edge_map[down_link.value]
        del self._edge_map[up_link.value]

    def repr(self):
        result = []
        visited = set()
        for node in self._edge_map.values():
            if node.value in visited: continue
            result.append(AVLTree.inorder(self._get_avl_root(*node.value)))
            visited = visited.union(result[-1])
        return result

    def render(self):
        for tour in self.repr():
            print(tour)

def run_euler_tour_forest_tests():
    from random import choice

    def validate_structure(euler_tour_forest, forest):
        tours = euler_tour_forest.repr()
        for tour in tours:
            for i in range(-1, len(tour)-1):
                assert tour[i][1] == tour[i+1][0]
        edges = set()
        for i in forest:
            edges.add((i,i)); edges.add((forest[i],forest[i]))
            edges.add((i,forest[i])); edges.add((forest[i],i))
        for tour in tours:
            for edge in tour:
                assert edge in edges
                edges.remove(edge)
        assert len(edges) == 0

    l = 1<<10

    euler_tour_forest, forest = EulerTourForest(), dict()
    for i in range(l):
        p = choice(list(range(i+1)))
        forest[i] = p
        euler_tour_forest.link(i, p)
        validate_structure(euler_tour_forest, forest)

    longest_tree_tour = max(map(lambda l: (len(l), l), euler_tour_forest.repr()))[1]
    tree_nodes = list(set(map(lambda e: e[0], longest_tree_tour)))

    for node in tree_nodes: euler_tour_forest.set_annotation(node, True)
    assert sorted(euler_tour_forest.annotated_nodes(tree_nodes[0])) == sorted(tree_nodes)

    for node in tree_nodes[::2]: euler_tour_forest.set_annotation(node, False)
    assert sorted(euler_tour_forest.annotated_nodes(tree_nodes[0])) == sorted(tree_nodes[1::2])

    for node in tree_nodes: euler_tour_forest.set_annotation(node, False)
    assert sorted(euler_tour_forest.annotated_nodes(tree_nodes[0])) == []

    get_root = lambda u: u if u == forest[u] else get_root(forest[u])
    for i in range(l):
        euler_tour_forest.make_root(i)
        assert euler_tour_forest.get_root(i) == i
        for j in range(l):
            assert euler_tour_forest.connected(i, j) == (get_root(i) == get_root(j))

    while True:
        try: i = choice(filter(lambda i: i != forest[i], list(forest.keys())))
        except: break
        euler_tour_forest.cut(i, forest[i])
        forest[i] = i
        validate_structure(euler_tour_forest, forest)

    print('Euler Tour Forest tests finished!')

class LevelStructure():
    def __init__(self):
        from collections import defaultdict

        self._euler_tour_forests = defaultdict(lambda: EulerTourForest())
        self._spanning_edges = defaultdict(lambda: defaultdict(lambda: set()))
        self._auxiliary_edges = defaultdict(lambda: defaultdict(lambda: set()))
        self._edge_level = dict()

    def connected(self, i, j):
        return self._euler_tour_forests[0].connected(i, j)

    def _linked(self, i, j):
        return (i, j) in self._edge_level

    def _is_auxiliary_edge(self, i, j):
        return j in self._auxiliary_edges[self._edge_level[i, j]][i]

    def _update_link_metadata(self, l, i, j):
        self._euler_tour_forests[l].set_annotation(i, True)
        self._euler_tour_forests[l].set_annotation(j, True)
        self._edge_level[i, j] = self._edge_level[j, i] = l

    def _link_auxiliary_edge(self, l, i, j):
        self._update_link_metadata(l, i, j)
        self._auxiliary_edges[l][i].add(j)
        self._auxiliary_edges[l][j].add(i)

    def _link_spanning_edge(self, l, i, j):
        self._update_link_metadata(l, i, j)
        self._spanning_edges[l][i].add(j)
        self._spanning_edges[l][j].add(i)

    def _update_cut_metadata(self, l, i, j):
        if (not len(self._spanning_edges[l][i])) and (not len(self._auxiliary_edges[l][i])):
            self._euler_tour_forests[l].set_annotation(i, False)
        if (not len(self._spanning_edges[l][j])) and (not len(self._auxiliary_edges[l][j])):
            self._euler_tour_forests[l].set_annotation(j, False)
        del self._edge_level[i, j]
        del self._edge_level[j, i]

    def _cut_auxiliary_edge(self, i, j):
        l = self._edge_level[i, j]
        self._auxiliary_edges[l][i].remove(j)
        self._auxiliary_edges[l][j].remove(i)
        self._update_cut_metadata(l, i, j)

    def _cut_spanning_edge(self, i, j):
        l = self._edge_level[i, j]
        self._spanning_edges[l][i].remove(j)
        self._spanning_edges[l][j].remove(i)
        self._update_cut_metadata(l, i, j)

    def link(self, i, j):
        if (i, j) in self._edge_level: return self
        if self._euler_tour_forests[0].connected(i, j): self._link_auxiliary_edge(0, i, j)
        else:
            self._link_spanning_edge(0, i, j)
            self._euler_tour_forests[0].link(i, j)
        return self

    def cut(self, i, j):
        if (i, j) not in self._edge_level: return self
        if self._is_auxiliary_edge(i, j): self._cut_auxiliary_edge(i, j)
        else:
            level = self._edge_level[i, j]
            self._cut_spanning_edge(i, j)
            for l in range(level, -1, -1): self._euler_tour_forests[l].cut(i, j)
            for l in range(level, -1, -1):
                forest = self._euler_tour_forests[l]
                (x, y) = (i, j) if forest.size(i) < forest.size(j) else (j, i)
                for u in forest.annotated_nodes(x):
                    for v in list(self._spanning_edges[l][u]):
                        self._cut_spanning_edge(u, v)
                        self._link_spanning_edge(1+l, u, v)
                        self._euler_tour_forests[1+l].link(u, v)
                for u in forest.annotated_nodes(x):
                    for v in list(self._auxiliary_edges[l][u]):
                        self._cut_auxiliary_edge(u, v)
                        if forest.connected(v, y):
                            self._link_spanning_edge(l, u, v)
                            for f in range(1+l): self._euler_tour_forests[f].link(u, v)
                            return self
                        self._link_auxiliary_edge(1+l, u, v)
        return self

    def render(self):
        print('edge levels')
        print(self._edge_level)
        for l in self._euler_tour_forests:
            print('level', l)
            print('euler tour forest')
            self._euler_tour_forests[l].render()
            print('spanning edges')
            print(dict(self._spanning_edges[l]))
            print('auxiliary edges')
            print(dict(self._auxiliary_edges[l]))
            print()

def run_level_structure_tests():
    from random import choice

    n = 1<<5

    level_structure = LevelStructure()
    graph = [set() for _ in range(n)]

    def connected(u, v, visited=None):
        if visited is None: visited = set()
        if u == v: return True
        visited.add(u)
        for i in graph[u]:
            if i in visited: continue
            if connected(i, v, visited): return True
        return False

    def validate():
        for u in range(n):
            for v in range(u):
                assert level_structure.connected(u, v) == connected(u, v)

    unlinked_edges = [(i, j) for i in range(n) for j in range(i)]
    linked_edges = []

    def link_and_validate():
        e = unlinked_edges.pop(choice(range(len(unlinked_edges))))
        linked_edges.append(e)
        level_structure.link(*e)
        graph[e[0]].add(e[1])
        graph[e[1]].add(e[0])
        validate()

    def cut_and_validate():
        e = linked_edges.pop(choice(range(len(linked_edges))))
        unlinked_edges.append(e)
        level_structure.cut(*e)
        graph[e[0]].remove(e[1])
        graph[e[1]].remove(e[0])
        validate()

    ne = len(unlinked_edges)
    while len(unlinked_edges) > (ne>>1): link_and_validate()
    while len(linked_edges) > (ne>>2): cut_and_validate()
    while len(unlinked_edges) > (ne>>2): link_and_validate()
    while len(linked_edges) > (ne>>1): cut_and_validate()
    while len(unlinked_edges) > 0: link_and_validate()
    while len(linked_edges) > 0: cut_and_validate()

    print('Level Structure tests finished!')

if __name__ == "__main__":
    run_avl_tree_tests()
    run_euler_tour_forest_tests()
    run_level_structure_tests()

