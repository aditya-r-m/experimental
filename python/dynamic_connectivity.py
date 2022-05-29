class AVLTree():
    total_nodes = 0

    def __init__(self, value, left=None, right=None):
        self.value = value
        self.id = AVLTree.total_nodes
        AVLTree.total_nodes += 1
        self._left = self._right = self._parent = None
        self._height = 1
        self._size = 1
        self._link_left(left)
        self._link_right(right)

    @staticmethod
    def height(node):
        return 0 if node is None else node._height

    @staticmethod
    def size(node):
        return 0 if node is None else node._size

    def _update_stats(self):
        self._height = 1 + max(map(AVLTree.height, [self._left, self._right]))
        self._size = 1 + sum(map(AVLTree.size, [self._left, self._right]))
        return self

    @staticmethod
    def balance_factor(node):
        if node is None: return 0
        return AVLTree.height(node._left) - AVLTree.height(node._right)

    def _link_left(self, new_left):
        self._left = new_left
        if new_left is not None: new_left._parent = self
        self._update_stats()
        return self

    def _link_right(self, new_right):
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
    def _merge_left(left, midv, right):
        if AVLTree.height(left) > AVLTree.height(right) + 1:
            left._link_right(AVLTree._merge_left(left._right, midv, right))
            if AVLTree.balance_factor(left) < -1:
                if AVLTree.balance_factor(left._right) < 0: return left._rotateL()
                return left._link_right(left._right._rotateR())._rotateL()
            return left
        return AVLTree(midv, left, right)

    @staticmethod
    def _merge_right(left, midv, right):
        if AVLTree.height(right) > AVLTree.height(left) + 1:
            right._link_left(AVLTree._merge_right(left, midv, right._left))
            if AVLTree.balance_factor(right) > 1:
                if AVLTree.balance_factor(right._left) > 0: return right._rotateR()
                return right._link_left(right._left._rotateL())._rotateR()
            return right
        return AVLTree(midv, left, right)

    @staticmethod
    def merge(left, midv, right):
        if AVLTree.height(left) > AVLTree.height(right) + 1:
            return AVLTree._cut_parent(AVLTree._merge_left(left, midv, right))
        if AVLTree.height(right) > AVLTree.height(left) + 1:
            return AVLTree._cut_parent(AVLTree._merge_right(left, midv, right))
        return AVLTree(midv, left, right)

    @staticmethod
    def push_front(node, value):
        return AVLTree.merge(None, value, node)

    @staticmethod
    def push_back(node, value):
        return AVLTree.merge(node, value, None)

    @staticmethod
    def split(mid):
        if mid is None: return None, None, None
        midv, [left, right] = mid.value, map(AVLTree._cut_parent, [mid._left, mid._right])
        while mid._parent is not None:
            nxt_cut_left, mid = (mid != mid._parent._left), mid._parent
            if nxt_cut_left: left = AVLTree.merge(AVLTree._cut_parent(mid._left), mid.value, left)
            else: right = AVLTree.merge(right, mid.value, AVLTree._cut_parent(mid._right))
        return left, midv, right

    @staticmethod
    def pop_front(node):
        leftmost = node
        while leftmost._left is not None: leftmost = leftmost._left
        return AVLTree.split(leftmost)[1:]

    @staticmethod
    def pop_back(node):
        rightmost = node
        while rightmost._right is not None: rightmost = rightmost._right
        return AVLTree.split(rightmost)[:2]

    @staticmethod
    def get(node, index):
        if node is None or index < 0: return None
        lsize = AVLTree.size(node._left)
        if lsize > index: return AVLTree.get(node._left, index)
        if lsize == index: return node
        return AVLTree.get(node._right, index - (1+lsize))

    @staticmethod
    def inorder(node, traversal=None):
        if traversal is None: traversal = []
        if node is not None:
            AVLTree.inorder(node._left, traversal)
            traversal.append(node.value)
            AVLTree.inorder(node._right, traversal)
        return traversal

    @staticmethod
    def render(node, offset=None):
        if node is None: print(offset, 'Empty')
        if offset is None: offset = ''
        print(offset, 'node id', node.id)
        print(offset, 'node value', node.value)
        print(offset, 'node height', node._height)
        print(offset, 'node size', node._size)
        print(offset, 'node balance', AVLTree.balance_factor(node))
        if node._parent is not None:
            print(offset, 'node parent id', node._parent.id)
        if node._left is not None:
            print(offset, 'left subtree')
            AVLTree.render(node._left, offset + '  ')
        if node._right is not None:
            print(offset, 'right subtree')
            AVLTree.render(node._right, offset + '  ')

    @staticmethod
    def validate_structure(node):
        if node is None: return
        AVLTree.validate_structure(node._left)
        AVLTree.validate_structure(node._right)
        assert node._height == 1 + max(map(AVLTree.height, [node._left, node._right]))
        assert node._size == 1 + sum(map(AVLTree.size, [node._left, node._right]))
        assert node._parent is None or node._parent._left == node or node._parent._right == node
        assert AVLTree.balance_factor(node) in [-1,0,1]

def run_tests():
    from random import randint, choice

    l = 1<<10

    tree = None
    for j in range(l): tree = AVLTree.push_back(tree, j)
    AVLTree.validate_structure(tree)
    assert AVLTree.inorder(tree) == list(range(l))

    values = []
    while tree is not None:
        tree, v = AVLTree.pop_back(tree)
        AVLTree.validate_structure(tree)
        values.append(v)
    assert values == list(range(l-1, -1, -1))

    tree = None
    for j in range(l-1, -1, -1): tree = AVLTree.push_front(tree, j)
    AVLTree.validate_structure(tree)
    assert AVLTree.inorder(tree) == list(range(l))

    values = []
    while tree is not None:
        v, tree = AVLTree.pop_front(tree)
        AVLTree.validate_structure(tree)
        values.append(v)
    assert values == list(range(l))

    tree_list = list(map(lambda v: AVLTree(v), range(l)))
    while len(tree_list) > 1:
        m = randint(0, len(tree_list)-2)
        tree = AVLTree.merge(tree_list[m], -1, tree_list[m+1])
        AVLTree.validate_structure(tree)
        tree_list = tree_list[:m] + [tree] + tree_list[m+2:]
    assert list(filter(lambda x: x >= 0, AVLTree.inorder(tree))) == list(range(l))

    while True:
        try: i = \
        choice(list(map(lambda p: p[0], filter(lambda p: p[1].value == -1, enumerate(tree_list)))))
        except: break
        left, _, right = AVLTree.split(tree_list[i])
        AVLTree.validate_structure(left)
        AVLTree.validate_structure(right)
        tree_list = tree_list[:i] + [left, right] + tree_list[i+1:]
    assert list(map(lambda t: t.value, tree_list)) == list(range(l))

if __name__ == "__main__":
    run_tests()

