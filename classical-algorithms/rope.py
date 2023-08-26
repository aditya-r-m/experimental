# python3

import sys
from math import inf

# Splay tree implementation

# Vertex of a splay tree
class Vertex:
  def __init__(self, value, left, right, parent):
    (self.value, self.left, self.right, self.parent) = (value, left, right, parent)
    self.size = 1
    update(self)

def update(v):
  if v == None:
    return
  v.size = 1 + (v.left.size if v.left else 0) + (v.right.size if v.right else 0)
  if v.left != None:
    v.left.parent = v
  if v.right != None:
    v.right.parent = v

def smallRotation(v):
  parent = v.parent
  if parent == None:
    return
  grandparent = v.parent.parent
  if parent.left == v:
    m = v.right
    v.right = parent
    parent.left = m
  else:
    m = v.left
    v.left = parent
    parent.right = m
  update(parent)
  update(v)
  v.parent = grandparent
  if grandparent != None:
    if grandparent.left == parent:
      grandparent.left = v
    else: 
      grandparent.right = v

def bigRotation(v):
  if v.parent.left == v and v.parent.parent.left == v.parent:
    # Zig-zig
    smallRotation(v.parent)
    smallRotation(v)
  elif v.parent.right == v and v.parent.parent.right == v.parent:
    # Zig-zig
    smallRotation(v.parent)
    smallRotation(v)    
  else: 
    # Zig-zag
    smallRotation(v)
    smallRotation(v)

# Makes splay of the given vertex and makes
# it the new root.
def splay(v):
  if v == None:
    return None
  while v.parent != None:
    if v.parent.parent == None:
      smallRotation(v)
      break
    bigRotation(v)
  return v

def find(root, index): 
  v = root
  last = root
  nxt = None
  while v != None:
    s = 1 + (v.left.size if v.left else 0)
    last = v
    if s == index:
      nxt = v
      break
    if s < index:
      index = index - s
      v = v.right
    else:
      nxt = v
      v = v.left      
  root = splay(last)
  return (nxt, root)

def split(root, index):  
  (result, root) = find(root, index)
  if result == None:    
    return (root, None)  
  right = splay(result)
  left = right.left
  right.left = None
  if left != None:
    left.parent = None
  update(left)
  update(right)
  return (left, right)

  
def merge(left, right):
  if left == None:
    return right
  if right == None:
    return left
  while right.left != None:
    right = right.left
  right = splay(right)
  right.left = left
  update(right)
  return right

  
# Code that uses splay tree to implement rope
                                    
root = None

def insert(x):
  global root
  (left, right) = split(root, inf)
  new_vertex = Vertex(x, None, None, None)  
  root = merge(merge(left, new_vertex), right)

def splice(i, j, k):
  global root
  (mid, right) = split(root, j + 2)
  (left, mid) = split(mid, i + 1)
  root = merge(left, right)
  (left, right) = split(root, k + 1)
  root = merge(merge(left, mid), right)


def inOrder(cur, result=[]):
  global root
  cur, result, stack = None, [], [root]
  while len(stack):
    cur = stack.pop()
    if type(cur) is str:
      result.append(cur)
    else:
      if cur.right: stack.append(cur.right)
      stack.append(cur.value)
      if cur.left: stack.append(cur.left)
  return result

class Rope:
  def __init__(self, s):
    global root
    self.s = s
    root = Vertex(s[0], None, None, None)
    for c in s[1:]:
      insert(c)
  def result(self):
    global root
    return inOrder(root)
  def process(self, i, j, k):
    splice(i, j, k)
             
rope = Rope(sys.stdin.readline().strip())
q = int(sys.stdin.readline())
for _ in range(q):
  i, j, k = map(int, sys.stdin.readline().strip().split())
  rope.process(i, j, k)
print("".join(rope.result()))
