
data Tree = Leaf | Node {
    val :: Int, depth :: Int, left :: Tree, right :: Tree }
    deriving (Show)

sdepth :: Tree -> Int
sdepth Leaf = 0
sdepth node = depth node

balanceFactor :: Tree -> Int
balanceFactor Leaf = 0
balanceFactor node = sdepth (left node) - sdepth (right node)

recomputeDepth :: Tree -> Tree
recomputeDepth node
    | depth node /= newDepth = node { depth = newDepth }
    | otherwise = node
    where newDepth = 1 + max (sdepth $ left node) (sdepth $ right node)

rotateLeftward :: Tree -> Tree
rotateLeftward node = recomputeDepth $ (right node) { left = recomputeDepth $ node { right = left (right node) } }

rotateRightward :: Tree -> Tree
rotateRightward node = recomputeDepth $ (left node) { right = recomputeDepth $ node { left = right (left node) } }

fixLeftward :: Tree -> Tree
fixLeftward node
    | balanceFactor (right node) == -1 = rotateLeftward node
    | otherwise = rotateLeftward $ recomputeDepth $ node { right = rotateRightward (right node) }

fixRightward :: Tree -> Tree
fixRightward node
    | balanceFactor (left node) == 1 = rotateRightward node
    | otherwise = rotateRightward $ recomputeDepth $ node { left = rotateLeftward (left node) }

balance :: Tree -> Tree
balance node
    | bf == -1 || bf == 0 || bf == 1 = node
    | bf == -2 = fixLeftward node
    | bf == 2 = fixRightward node
    where bf = balanceFactor node

add :: Int -> Tree -> Tree
add v Leaf = Node { val = v, depth = 1, left = Leaf, right = Leaf }
add v node
    | v < val node = balance $ recomputeDepth $ node { left = add v (left node) }
    | otherwise = balance $ recomputeDepth $ node { right = add v (right node) }

contains :: Tree -> Int -> Bool
contains Leaf _ = False
contains node v
    | v == val node = True
    | v < val node = contains (left node) v
    | otherwise = contains (right node) v

popMin :: Tree -> (Maybe Int, Tree)
popMin Leaf = (Nothing, Leaf)
popMin node
    | sdepth (left node) == 0 = (Just (val node), right node)
    | otherwise = (Just v, balance $ recomputeDepth $ node { left = nlc })
    where (Just v, nlc) = popMin $ left node

del :: Int -> Tree -> Tree
del _ Leaf = Leaf
del v node
    | v == val node && sdepth (left node) == 0 = right node
    | v == val node && sdepth (right node) == 0  = left node
    | v == val node = balance $ recomputeDepth $ node { val = poppedVal, right = poppedRight }
    where (Just poppedVal, poppedRight) = popMin $ right node
del v node
    | v < val node = balance $ recomputeDepth $ node { left = del v $ left node }
    | otherwise = balance $ recomputeDepth $ node { right = del v $ right node }

merge :: Tree -> Tree -> Tree
merge l r
    | sdepth l == 0 = r
    | sdepth r == 0 = l
    | sdepth l < sdepth r - 1 = balance $ recomputeDepth $ r { left = merge l (left r) }
    | sdepth l > sdepth r + 1 = balance $ recomputeDepth $ l { right = merge (right l) r }
    | otherwise = balance $ recomputeDepth $ Node { val = poppedVal, depth = -1, left = l, right = poppedRight }
    where (Just poppedVal, poppedRight) = popMin r

split_ :: Int -> Tree -> (Tree, Tree) -> (Tree, Tree)
split_ _ Leaf (l, r) = (l, r)
split_ v node (l, r)
    | val node <= v = split_ v (right node) (add (val node) $ uncurry merge (l, left node), r)
    | otherwise = split_ v (left node) (l, add (val node) $ uncurry merge (right node, r))

split :: Int -> Tree -> (Tree, Tree)
split v node = split_ v node (Leaf, Leaf)

fromList :: [Int] -> Tree
fromList = foldr add Leaf

toList_ :: Tree -> [Int] -> [Int]
toList_ Leaf lls = lls
toList_ node lls = toList_ (left node) (val node : toList_ (right node) lls)

toList :: Tree -> [Int]
toList = flip toList_ []
