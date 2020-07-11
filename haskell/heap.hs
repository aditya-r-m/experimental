import qualified Data.Bits as B

data Heap = Leaf | Node {
    value :: Int, size :: Int, left :: Heap, right :: Heap }
    deriving (Show)

ssz :: Heap -> Int
ssz Leaf = 0
ssz node = size node

isBinExp :: Int -> Bool
isBinExp = (flip B.shiftR 1 . (+1) . (flip (-) 1 >>= B.xor)) >>= (==)

push :: Int -> Heap -> Heap
push v Leaf = Node { value = v, size = 1, left = Leaf, right = Leaf }
push v root
    | isLeftBound = root { value = pv, size = 1 + size root, left = push cv (left root) }
    | otherwise = root { value = pv, size = 1 + size root, right = push cv (right root) }
    where
        (sl, sr) = (,) <$> ssz . left <*> ssz . right $ root
        (pv, cv) = (,) <$> uncurry min <*> uncurry max $ (v, value root)
        isLeftBound = (sl == sr) || (not $ isBinExp (sl + 1))

popLast :: Heap -> (Int, Heap)
popLast root
    | ssz targetCh == 0 = (value root, Leaf)
    | isLeftBound = (pv, root { size = size root - 1, left = newChild })
    | otherwise = (pv, root { size = size root - 1, right = newChild })
    where
        (sl, sr) = (,) <$> ssz . left <*> ssz . right $ root
        isLeftBound = (sl /= sr) && (isBinExp (sr + 1))
        targetCh = (if isLeftBound then left else right) root
        (pv, newChild) = popLast targetCh

pushDown :: Int -> Heap -> Heap
pushDown _ Leaf = Leaf
pushDown pv root
    | pv == minCV = root { value = pv }
    | isLeftBound = root { value = minCV, left = pushDown pv (left root) }
    | otherwise = root { value = minCV, right = pushDown pv (right root) }
        where
            lv = if ssz (left root) > 0 then value (left root) else pv
            rv = if ssz (right root) > 0 then value (right root) else pv
            minCV = foldr min pv [lv, rv]
            isLeftBound = lv <= rv

pop :: Heap -> (Maybe Int, Heap)
pop Leaf = (Nothing, Leaf)
pop root = (Just (value root), uncurry pushDown $ popLast root)

fromList :: [Int] -> Heap
fromList = foldr push Leaf

toList :: Heap -> [Int]
toList Leaf = []
toList root = v:(toList nroot)
    where (Just v, nroot) = pop root

heapSort :: [Int] -> [Int]
heapSort = toList . fromList
