class AVLNode():
    total_nodes = 0

    def __init__(self, value):
        self.value = value
        self.left = self.right = self.parent = None
        self.height = 1
        self.id = AVLNode.total_nodes
        AVLNode.total_nodes += 1

    def _left_height(self):
        return 0 if self.left is None else self.left.height

    def _right_height(self):
        return 0 if self.right is None else self.right.height

    def _update_height(self):
        self.height = 1 + max(self._left_height(), self._right_height())

    def _balance_factor(self):
        return self._left_height() - self._right_height()

    def _link_left(self, new_left):
        self.left = new_left
        if new_left is not None: new_left.parent = self

    def _link_right(self, new_right):
        self.right = new_right
        if new_right is not None: new_right.parent = self

    def _rotateR(self):
        child = self.left
        self._link_left(child.right)
        child._link_right(self)
        self._update_height()
        child._update_height()
        return child

    def _rotateL(self):
        child = self.right
        self._link_right(child.left)
        child._link_left(self)
        self._update_height()
        child._update_height()
        return child

    def _rotateLR(self):
        self._link_left(self.left._rotateL())
        return self._rotateR()

    def _rotateRL(self):
        self._link_right(self.right._rotateR())
        return self._rotateL()

    def _rebalance(self):
        if self._balance_factor() == 2 and self.left._balance_factor() == 1:
            return True, self._rotateR()
        elif self._balance_factor() == -2 and self.right._balance_factor() == -1:
            return True, self._rotateL()
        elif self._balance_factor() == 2 and self.left._balance_factor() == -1:
            return True, self._rotateLR()
        elif self._balance_factor() == -2 and self.right._balance_factor() == 1:
            return True, self._rotateRL()
        self._update_height()
        return False, self

    def insert(self, value):
        if value < self.value:
            if self.left is None: updated, new_left = True, AVLNode(value)
            else: updated, new_left = self.left.insert(value)
            if updated: self._link_left(new_left)
        else:
            if self.right is None: updated, new_right = True, AVLNode(value)
            else: updated, new_right = self.right.insert(value)
            if updated: self._link_right(new_right)
        return self._rebalance()

    def pop_left(self):
        if self.left is None:
            return self.value, True, self.right
        value, updated, new_left = self.left.pop_left()
        if updated: self._link_left(new_left)
        return (value,) + self._rebalance()

    def remove(self, value):
        if value < self.value:
            if self.left is None: return False, self
            updated, new_left = self.left.remove(value)
            if updated: self._link_left(new_left)
        elif value > self.value:
            if self.right is None: return False, self
            updated, new_right = self.right.remove(value)
            if updated: self._link_right(new_right)
        else:
            if self.right is None: return True, self.left
            self.value, updated, new_right = self.right.pop_left()
            if updated: self._link_right(new_right)
        return self._rebalance()

    def render(self, offset=''):
        print(offset, 'node id', self.id)
        print(offset, 'node value', self.value)
        print(offset, 'node height', self.height)
        if self.parent is not None:
            print(offset, 'node parent id', self.parent.id)
        if self.left is not None:
            print(offset, 'left subtree')
            self.left.render(offset + '  ')
        if self.right is not None:
            print(offset, 'right subtree')
            self.right.render(offset + '  ')


class AVLTree():
    def __init__(self):
        self.root = None

    def insert(self, value):
        if self.root is None: updated, self.root = False, AVLNode(value)
        else: updated, self.root = self.root.insert(value)
        if updated: self.root.parent = None

    def remove(self, value):
        print(value, self.root.value)
        if self.root is None: return
        else: updated, self.root = self.root.remove(value)
        if updated: self.root.parent = None

    def reset(self):
        self.root = None

    def render(self):
        if self.root is None: print('Empty Tree')
        else: self.root.render()
        print('---------------')

def run_tests():
    tree = AVLTree()
    insert, remove, render = tree.insert, tree.remove, tree.render
    basic_l_insert = [(insert, 3), (insert, 2), (insert, 1)]
    basic_r_insert = [(insert, 1), (insert, 2), (insert, 3)]
    basic_lr_insert = [(insert, 3), (insert, 1), (insert, 2)]
    basic_rl_insert = [(insert, 1), (insert, 3), (insert, 2)]
    basic_l_remove = [(insert, 2), (insert, 1), (insert, 3), (insert, 4), (remove, 1)]
    basic_m_remove = [(insert, 2), (insert, 1), (insert, 4), (insert, 3), (remove, 2)]

    tests = [basic_l_insert, basic_r_insert, basic_lr_insert, basic_rl_insert, basic_l_remove, basic_m_remove]
    for test in tests:
        print(list(map(lambda p: (p[0].__name__, p[1]), test)))
        tree.reset()
        for op in test: op[0](op[1])
        tree.render()

if __name__ == "__main__":
    run_tests()

