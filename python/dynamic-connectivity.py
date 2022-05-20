class AVLNode():
    total_nodes = 0

    def __init__(self, value, left=None, right=None):
        self.value = value
        self.id = AVLNode.total_nodes
        AVLNode.total_nodes += 1
        self.left = self.right = self.parent = None
        self.height = 1
        self.link_left(left)
        self.link_right(right)

    @staticmethod
    def safe_height(node):
        return 0 if node is None else node.height

    def left_height(self):
        return AVLNode.safe_height(self.left)

    def right_height(self):
        return AVLNode.safe_height(self.right)

    def update_height(self):
        self.height = 1 + max(self.left_height(), self.right_height())
        return self

    def balance_factor(self):
        return self.left_height() - self.right_height()

    def link_left(self, new_left):
        self.left = new_left
        if new_left is not None: new_left.parent = self
        self.update_height()
        return self

    def link_right(self, new_right):
        self.right = new_right
        if new_right is not None: new_right.parent = self
        self.update_height()
        return self

    def rotateR(self):
        child = self.left
        self.link_left(child.right)
        child.link_right(self)
        self.update_height()
        child.update_height()
        return child

    def rotateL(self):
        child = self.right
        self.link_right(child.left)
        child.link_left(self)
        self.update_height()
        child.update_height()
        return child

    @staticmethod
    def merge_left(left, midv, right):
        if AVLNode.safe_height(left) > AVLNode.safe_height(right) + 1:
            left.link_right(AVLNode.merge_left(left.right, midv, right))
            if left.balance_factor() < -1:
                if left.right.balance_factor() < 0: return left.rotateL()
                return left.link_right(left.right.rotateR()).rotateL()
            return left
        return AVLNode(midv, left, right)

    @staticmethod
    def merge_right(left, midv, right):
        if AVLNode.safe_height(right) > AVLNode.safe_height(left) + 1:
            right.link_left(AVLNode.merge_right(left, midv, right.left))
            if right.balance_factor() > 1:
                if right.left.balance_factor() > 0: return right.rotateR()
                return right.link_left(right.left.rotateL()).rotateR()
            return right
        return AVLNode(midv, left, right)

    @staticmethod
    def merge(left, midv, right):
        if AVLNode.safe_height(left) > AVLNode.safe_height(right) + 1:
            return AVLNode.merge_left(left, midv, right)
        if AVLNode.safe_height(right) > AVLNode.safe_height(left) + 1:
            return AVLNode.merge_right(left, midv, right)
        return AVLNode(midv, left, right)

    def inorder(self, traversal):
        if self.left is not None: self.left.inorder(traversal)
        traversal.append(self.value)
        if self.right is not None: self.right.inorder(traversal)
        return traversal

    def render(self, offset):
        print(offset, 'node id', self.id)
        print(offset, 'node value', self.value)
        print(offset, 'node height', self.height)
        print(offset, 'node balance', self.balance_factor())
        if self.parent is not None:
            print(offset, 'node parent id', self.parent.id)
        if self.left is not None:
            print(offset, 'left subtree')
            self.left.render(offset + '  ')
        if self.right is not None:
            print(offset, 'right subtree')
            self.right.render(offset + '  ')

class AVLTree():
    def __init__(self, root=None):
        self.root = root

    def reset(self):
        self.root = None
        return

    def height(self):
        return AVLNode.safe_height(self.root)

    def move(self, other):
        self.root = other.root
        other.reset()
        return self

    @staticmethod
    def merge(left_tree, mid_value, right_tree):
        return AVLTree(AVLNode.merge(left_tree.root, mid_value, right_tree.root))

    def push_back(self, value):
        return self.move(AVLTree.merge(self, value, AVLTree()))

    def push_front(self, value):
        return self.move(AVLTree.merge(AVLTree(), value, self))

    def inorder(self):
        if self.root is None: return []
        return self.root.inorder([])

    def render(self):
        if self.root is None: print('Empty Tree')
        else: self.root.render('')
        print('---------------')
        print(self.inorder())
        print('===============')

def run_tests():
    from random import randint

    def validate_structure(node):
        if node is None: return
        validate_structure(node.left)
        validate_structure(node.right)
        assert node.height == 1 + max(map(AVLNode.safe_height, [node.left, node.right]))
        assert node.balance_factor() in [-1,0,1]

    l = 1<<10
    tree = AVLTree()
    for j in range(l): tree.push_back(j)
    validate_structure(tree.root)
    assert tree.inorder() == list(range(l))

    tree.reset()
    for j in range(l-1, -1, -1): tree.push_front(j)
    validate_structure(tree.root)
    assert tree.inorder() == list(range(l))

    tree_list = list(map(lambda v: AVLTree(AVLNode(v)), range(l)))
    while len(tree_list) > 1:
        m = randint(0, len(tree_list)-2)
        tree_list = tree_list[:m] + [AVLTree.merge(tree_list[m], -1, tree_list[m+1])] + tree_list[m+2:]
    tree.move(tree_list[0])
    validate_structure(tree.root)
    assert list(filter(lambda x: x >= 0, tree.inorder())) == list(range(l))

if __name__ == "__main__":
    run_tests()

