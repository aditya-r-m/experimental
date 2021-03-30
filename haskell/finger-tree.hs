-- https://www.staff.city.ac.uk/~ross/papers/FingerTree.pdf

{-# LANGUAGE MultiParamTypeClasses #-}
{-# LANGUAGE FlexibleInstances #-}
{-# LANGUAGE FlexibleContexts #-}

-- Util

(~.) :: (c -> d) -> (a -> b -> c) -> (a -> b -> d)
(~.) f g = curry $ f . uncurry g

-- Core

class Reduce f where
    reducer :: (a -> b -> b) -> f a -> b -> b
    reducel :: (b -> a -> b) -> b -> f a -> b

class (Monoid v) => Measured v a where
    measure :: a -> v

data Digit a = One a | Two a a | Three a a a | Four a a a a
    deriving (Show)

data Node v a = Node2 v a a | Node3 v a a a
    deriving (Show)
node2 :: (Measured v a) => a -> a -> Node v a
node2 a b = Node2 (measure a <> measure b) a b
node3 :: (Measured v a) => a -> a -> a -> Node v a
node3 a b c = Node3 (measure a <> measure b <> measure c) a b c

data FingerTree v a = Empty
                    | Single a
                    | Deep v (Digit a) (FingerTree v (Node v a)) (Digit a)
    deriving (Show)
deep :: (Measured v a) => Digit a -> FingerTree v (Node v a) -> Digit a -> FingerTree v a
deep l m r = Deep (measure l <> measure m <> measure r) l m r

instance Reduce Digit where
    reducer (-<) (One m) z = m -< z
    reducer (-<) (Two m n) z = m -< (n -< z)
    reducer (-<) (Three m n o) z = m -< (n -< (o -< z))
    reducer (-<) (Four m n o p) z = m -< (n -< (o -< (p -< z)))
    reducel (>-) z (One m) = z >- m
    reducel (>-) z (Two m n) = (z >- m) >- n
    reducel (>-) z (Three m n o) = ((z >- m) >- n) >- o
    reducel (>-) z (Four m n o p) = (((z >- m) >- n) >- o) >- p

instance (Measured v a) => Measured v (Digit a) where
    measure (One a) = measure a
    measure (Two a b) = measure a <> measure b
    measure (Three a b c) = measure a <> measure b <> measure c
    measure (Four a b c d) = measure a <> measure b <> measure c <> measure d

instance Reduce (Node v) where
    reducer (-<) (Node2 _ l r) z = l -< (r -< z)
    reducer (-<) (Node3 _ l m r) z = l -< (m -< (r -< z))
    reducel (>-) z (Node2 _ l r) = (z >- l) >- r
    reducel (>-) z (Node3 _ l m r) = ((z >- l) >- m) >- r

instance (Measured v a) => Measured v (Node v a) where
    measure (Node2 v _ _) = v
    measure (Node3 v _ _ _) = v

instance Reduce (FingerTree v) where
    reducer (-<) (Empty) z = z
    reducer (-<) (Single v) z = v -< z
    reducer (-<) (Deep _ l m r) z = l -<| (m -<|| (r -<| z))
        where
            (-<|) = reducer (-<)
            (-<||) = reducer (reducer (-<))
    reducel (>-) z (Empty) = z
    reducel (>-) z (Single v) = z >- v
    reducel (>-) z (Deep _ l m r) = ((z |>- l) ||>- m) |>- r
        where
            (|>-) = reducel (>-)
            (||>-) = reducel (reducel (>-))

instance (Measured v a) => Measured v (FingerTree v a) where
    measure Empty = mempty
    measure (Single a) = measure a
    measure (Deep v _ _ _) = v

infixr 5 <|
(<|) :: (Measured v a) => a -> FingerTree v a -> FingerTree v a
a <| Empty = Single a
a <| Single b = deep (One a) Empty (One b)
a <| Deep _ (One b) m r = deep (Two a b) m r
a <| Deep _ (Two b c) m r = deep (Three a b c) m r
a <| Deep _ (Three b c d) m r = deep (Four a b c d) m r
a <| Deep _ (Four b c d e) m r = deep (Two a b) (node3 c d e <| m) r

infixr 5 |>
(|>) :: (Measured v a) => FingerTree v a -> a -> FingerTree v a
Empty |> a = Single a
Single b |> a = deep (One b) Empty (One a)
Deep _ l m (One b) |> a = deep l m (Two b a)
Deep _ l m (Two c b) |> a = deep l m (Three c b a)
Deep _ l m (Three d c b) |> a = deep l m (Four d c b a)
Deep _ l m (Four e d c b) |> a = deep l (m |> node3 e d c) (Two b a)

(<||) :: (Reduce f, Measured v a) => f a -> FingerTree v a -> FingerTree v a
(<||) = reducer (<|)

(||>) :: (Reduce f, Measured v a) => FingerTree v a -> f a -> FingerTree v a
(||>) = reducel (|>)

instance Reduce [] where
    reducer f l v = foldr f v l
    reducel f v l = foldl f v l

toDigit :: [a] -> Digit a
toDigit [a] = One a
toDigit [a, b] = Two a b
toDigit [a, b, c] = Three a b c
toDigit [a, b, c, d] = Four a b c d

toTree :: (Reduce f, Measured v a) => f a -> FingerTree v a
toTree l = (<||) l Empty

toList :: (Reduce f) => f a -> [a]
toList t = reducer (:) t []

data ViewL s a = NilL | ConsL a (s a)
    deriving (Show)

viewL :: (Measured v a) => FingerTree v a -> ViewL (FingerTree v) a
viewL Empty = NilL
viewL (Single x) = ConsL x Empty
viewL (Deep _ (One a) m r) = ConsL a $ case viewL m of
    NilL -> toTree r
    ConsL (Node2 _ b c) mm -> deep (Two b c) mm r
    ConsL (Node3 _ b c d) mm -> deep (Three b c d) mm r
viewL (Deep _ (Two a b) m r) = ConsL a (deep (One b) m r)
viewL (Deep _ (Three a b c) m r) = ConsL a (deep (Two b c) m r)
viewL (Deep _ (Four a b c d) m r) = ConsL a (deep (Three b c d) m r)

data ViewR s a = NilR | ConsR a (s a)

viewR :: (Measured v a) => FingerTree v a -> ViewR (FingerTree v) a
viewR Empty = NilR
viewR (Single x) = ConsR x Empty
viewR (Deep _ l m (One a)) = ConsR a $ case viewR m of
    NilR -> toTree l
    ConsR (Node2 _ b c) mm -> deep l mm (Two b c)
    ConsR (Node3 _ b c d) mm -> deep l mm (Three b c d)
viewR (Deep _ l m (Two a b)) = ConsR b (deep l m (One a))
viewR (Deep _ l m (Three a b c)) = ConsR c (deep l m (Two a b))
viewR (Deep _ l m (Four a b c d)) = ConsR d (deep l m (Three a b c))

nodes :: (Measured v a) => [a] -> [Node v a]
nodes [a, b] = [node2 a b]
nodes [a, b, c] = [node3 a b c]
nodes [a, b, c, d] = [node2 a b, node2 c d]
nodes (a:b:c:xs) = node3 a b c : nodes xs

concat_ :: (Measured v a) => FingerTree v a -> [a] -> FingerTree v a -> FingerTree v a
concat_ Empty ts m = ts <|| m
concat_ m ts Empty = m ||> ts
concat_ (Single x) ts m = x <| (ts <|| m)
concat_ m ts (Single x) = (m ||> ts) |> x
concat_ (Deep _ l1 m1 r1) ts (Deep _ l2 m2 r2) = deep l1 (concat_ m1 (nodes $ (toList r1) ++ ts ++ (toList l2)) m2) r2

(|><|) :: (Measured v a) => FingerTree v a -> FingerTree v a -> FingerTree v a
(|><|) = flip concat_ []

data Split f a = Split (f a) a (f a)
    deriving (Show)

deepL :: (Measured v a) => [a] -> FingerTree v (Node v a) -> [a] -> FingerTree v a
deepL [] m rs = case viewL m of
    NilL -> toTree rs
    ConsL (Node2 _ va vb) mm -> deep (Two va vb) mm (toDigit rs)
    ConsL (Node3 _ va vb vc) mm -> deep (Three va vb vc) mm (toDigit rs)
deepL ls m rs = deep (toDigit ls) m (toDigit rs)

deepR :: (Measured v a) => [a] -> FingerTree v (Node v a) -> [a] -> FingerTree v a
deepR ls m [] = case viewR m of
    NilR -> toTree ls
    ConsR (Node2 _ va vb) mm -> deep (toDigit ls) mm (Two va vb)
    ConsR (Node3 _ va vb vc) mm -> deep (toDigit ls) mm (Three va vb vc)
deepR ls m rs = deep (toDigit ls) m (toDigit rs)

splitDigit_ :: (Measured v a) => (v -> Bool) -> v -> [a] ->  Split [] a
splitDigit_ p i [v] = Split [] v []
splitDigit_ p i (v:vs)
    | p i' = Split [] v vs
    | otherwise = let Split l m r = splitDigit_ p i' vs in Split (v:l) m r
    where i' = i <> measure v

splitTree_ :: (Measured v a) => (v -> Bool) -> v -> FingerTree v a -> Split (FingerTree v) a
splitTree_ p i (Single v) = Split Empty v Empty
splitTree_ p i (Deep _ l m r)
    | p il = let Split sl sm sr = splitDigit_ p i (toList l) in Split (toTree sl) sm (deepL (toList sr) m (toList r))
    | p im = let Split sl sm sr = splitTree_ p i m; Split ssl ssm ssr = splitDigit_ p (il <> measure sl) (toList sm) in
        Split (deepR (toList l) sl (toList ssl)) ssm (deepL (toList ssr) sr (toList r))
    | otherwise = let Split sl sm sr = splitDigit_ p i (toList r) in Split (deepR (toList l) m (toList sl)) sm (toTree sr)
    where
        il = i <> measure l
        im = il <> measure m

split :: (Measured v a) => (v -> Bool) -> FingerTree v a -> (FingerTree v a, FingerTree v a)
split p Empty = (Empty, Empty)
split p tree
    | p (measure v) = (l, v <| r)
    | otherwise = (tree, Empty)
    where Split l v r = splitTree_ p mempty tree

-- Deque Implementation using Finger Tree

newtype Size = Size { getSize :: Int }
    deriving (Eq, Ord, Show)
instance Semigroup Size where
    (Size m) <> (Size n) = Size $ m + n
instance Monoid Size where
    mempty = Size 0

newtype Elem a = Elem { getElem :: a }
    deriving (Show)
instance Measured Size (Elem a) where
    measure _ = Size 1

newtype Deque a = Deque (FingerTree Size (Elem a))
    deriving (Show)

pushFront :: a -> Deque a -> Deque a
pushFront a (Deque t) = Deque $ (Elem a) <| t

peekFront :: Deque a -> Maybe a
peekFront (Deque t) = case viewL t of
    NilL -> Nothing
    ConsL (Elem v) _ -> Just v

popFront :: Deque a -> Deque a
popFront (Deque t) = case viewL t of
    NilL -> Deque Empty
    ConsL _ pt -> Deque pt

pushBack :: Deque a -> a -> Deque a
pushBack (Deque t) a = Deque $ t |> (Elem a)

peekBack :: Deque a -> Maybe a
peekBack (Deque t) = case viewR t of
    NilR -> Nothing
    ConsR (Elem v) _ -> Just v

popBack :: Deque a -> Deque a
popBack (Deque t) = case viewR t of
    NilR -> Deque Empty
    ConsR _ pt -> Deque pt

qsize :: Deque a -> Size
qsize (Deque t) = measure t

-- Priority Queue Implementation using Finger Tree

data Prio a = MInf | Prio a
    deriving (Eq, Ord, Show)
instance (Ord a) => Semigroup (Prio a) where
    MInf <> Prio n = Prio n
    Prio m <> MInf = Prio m
    (Prio m) <> (Prio n) = Prio $ max m n
instance (Ord a) => Monoid (Prio a) where
    mempty = MInf

instance (Ord a) => Measured (Prio a) (Elem a) where
    measure (Elem v) = Prio v

newtype Heap a = Heap (FingerTree (Prio a) (Elem a))
    deriving (Show)

push :: (Ord a) => a -> Heap a -> Heap a
push v (Heap t) = Heap (Elem v <| t)

pop :: (Ord a) => Heap a -> (a, Heap a)
pop (Heap t) = (e, Heap (l |><| r))
    where Split l (Elem e) r = splitTree_ (== measure t) MInf t

-- Ordered Sequence Implementation using Finger Tree

data Key a = NoKey | Key a
    deriving (Eq, Ord, Show)
instance (Ord a) => Semigroup (Key a) where
    k <> NoKey = k
    _ <> k = k
instance (Ord a) => Monoid (Key a) where
    mempty = NoKey

instance (Ord a) => Measured (Key a) (Elem a) where
    measure (Elem v) = Key v

instance (Ord a) => Measured (Key a, Size) (Elem a) where
    measure v = (measure v, measure v)

newtype OrdSeq a = OrdSeq (FingerTree (Key a, Size) (Elem a))
    deriving (Show)

partition :: (Ord a) => a -> OrdSeq a -> (OrdSeq a, OrdSeq a)
partition k (OrdSeq xs) = (OrdSeq l, OrdSeq r)
    where (l, r) = split ((>= (Key k)) . fst) xs

partitionAt :: (Ord a) => Int -> OrdSeq a -> (OrdSeq a, OrdSeq a)
partitionAt i (OrdSeq xs) = (OrdSeq l, OrdSeq r)
    where (l, r) = split ((>= (Size i)) . snd) xs

insert :: (Ord a) => a -> OrdSeq a -> OrdSeq a
insert x xs = OrdSeq (l |><| (Elem x <| r))
    where (OrdSeq l, OrdSeq r) = partition x xs

deleteAll :: (Ord a) => a -> OrdSeq a -> OrdSeq a
deleteAll x (OrdSeq xs) = OrdSeq (l |><| r)
    where
        (l, m) = split ((>= (Key x)) . fst) xs
        (_, r) = split ((> (Key x)) . fst) m

getValueAt :: (Ord a) => Int -> OrdSeq a -> Maybe a
getValueAt i xs = case viewL r of
    NilL -> Nothing
    ConsL (Elem x) _ -> Just x
    where (_, OrdSeq r) = partitionAt i xs

getLeftMeasure_ :: (Ord a) => a -> OrdSeq a -> (Key a, Size)
getLeftMeasure_ x oxs = measure l
    where (OrdSeq l, _) = partition x oxs

getEqMeasure_ :: (Ord a) => a -> OrdSeq a -> (Key a, Size)
getEqMeasure_ x oxs = measure e
    where
        (_, OrdSeq m) = partition x oxs
        (e, _) = split ((> (Key x)) . fst) m

countSmallerElems :: (Ord a) => a -> OrdSeq a -> Size
countSmallerElems = snd ~. getLeftMeasure_

countEqualElems :: (Ord a) => a -> OrdSeq a -> Size
countEqualElems = snd ~. getEqMeasure_

-- Interval Tree Implementation using Finger Tree

data Interval a = Interval a a
    deriving (Show)

instance (Ord a, Show a) => Measured (Key a, Prio a) (Interval a)
    where measure (Interval x y) = (Key x, Prio y)

newtype IntervalTree a = IntervalTree (FingerTree (Key a, Prio a) (Interval a))
    deriving (Show)

partitionIT :: (Ord a, Show a) => Interval a -> IntervalTree a -> (IntervalTree a, IntervalTree a)
partitionIT (Interval k p) (IntervalTree xs) = (IntervalTree l, IntervalTree r)
    where (l, r) = split ((>= (Key k)) . fst) xs

insertIT :: (Ord a, Show a) => Interval a -> IntervalTree a -> IntervalTree a
insertIT i xs = IntervalTree (l |><| (i <| r))
    where (IntervalTree l, IntervalTree r) = partitionIT i xs

crossesHigh :: (Ord a) => a -> (Key a, Prio a) -> Bool
crossesHigh x (_, Prio h) = x <= h

preceedsLow :: (Ord a) => a -> (Key a, Prio a) -> Bool
preceedsLow x (Key l, _) = x >= l

getOverlappingInterval :: (Ord a, Show a) => Interval a -> IntervalTree a -> Maybe (Interval a)
getOverlappingInterval _ (IntervalTree Empty) = Nothing
getOverlappingInterval (Interval il ih) (IntervalTree t)
    | crossesHigh il (measure t) && preceedsLow ih (measure oi) = Just oi
    | otherwise = Nothing
    where (Split _ oi _) = splitTree_ (crossesHigh il) mempty t

getOverlappingIntervals :: (Ord a, Show a) => Interval a -> IntervalTree a -> [Interval a]
getOverlappingIntervals _ (IntervalTree Empty) = []
getOverlappingIntervals (Interval il ih) (IntervalTree t)
    | preceedsLow ih (measure x) = matches t
    | otherwise = matches l
    where
        (Split l x _) = splitTree_ (not . preceedsLow ih) mempty t
        matches Empty = []
        matches ft
            | crossesHigh il (measure ft) = let (Split _ x r) = splitTree_ (crossesHigh il) mempty ft in (x: matches r)
            | otherwise = []
