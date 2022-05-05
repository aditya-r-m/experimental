class AVLNode():
    total_nodes = 0

    def __init__(self, value, parent=None):
        self.value = value
        self.parent = parent
        self.left = self.right = None
        self.height = 1
        self.id = AVLNode.total_nodes
        AVLNode.total_nodes += 1

    def _insert_left(self, value):
        if self.left == None: self.left = AVLNode(value, self)
        else: self.left.insert(value)

    def _insert_right(self, value):
        if self.right == None: self.right = AVLNode(value, self)
        else: self.right.insert(value)

    def _left_height(self):
        return 0 if self.left is None else self.left.height

    def _right_height(self):
        return 0 if self.right is None else self.right.height

    def _update_height(self):
        self.height = 1 + max(self._left_height(), self._right_height())

    def _balance_factor(self):
        return self._left_height() - self._right_height()

    def _rotateR(self):
        parent = self.parent
        child = self.left

        if parent is not None:
            if parent.left == self: parent.left = child
            else: parent.right = child
        child.parent = parent

        self.left = child.right
        if child.right is not None: child.right.parent = self

        child.right = self
        self.parent = child

        self._update_height()
        child._update_height()

    def _rotateL(self):
        parent = self.parent
        child = self.right

        if parent is not None:
            if parent.left == self: parent.left = child
            else: parent.right = child
        child.parent = parent

        self.right = child.left
        if child.left is not None: child.left.parent = self

        child.left = self
        self.parent = child

        self._update_height()
        child._update_height()

    def _rotateLR(self):
        self.left._rotateL()
        self._rotateR()

    def _rotateRL(self):
        self.right._rotateR()
        self._rotateL()

    def _rebalance(self):
        if self._balance_factor() == 2 and self.left._balance_factor() == 1: self._rotateR()
        elif self._balance_factor() == -2 and self.right._balance_factor() == -1: self._rotateL()
        elif self._balance_factor() == 2 and self.left._balance_factor() == -1: self._rotateLR()
        elif self._balance_factor() == -2 and self.right._balance_factor() == 1: self._rotateRL()
        else: self._update_height()

    def insert(self, value):
        is_root = self.parent is None
        if value < self.value: self._insert_left(value)
        else: self._insert_right(value)
        self._rebalance()
        if is_root:
            new_root = self
            while new_root.parent is not None: new_root = new_root.parent
            return new_root

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
        if self.root == None: self.root = AVLNode(value)
        else: self.root = self.root.insert(value)

    def render(self):
        if self.root == None: print('Empty Tree')
        else: self.root.render()
        print('---------------')

tree = AVLTree()
tree.render()
tree.insert(1)
tree.render()
tree.insert(3)
tree.render()
tree.insert(2)
tree.render()

