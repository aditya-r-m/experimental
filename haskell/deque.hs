
type Deque = ([Int], Int, [Int], Int)

empty :: Deque
empty = ([], 0, [], 0)

pushFront :: Int -> Deque -> Deque
pushFront i (f, fl, b, bl) = (i:f, fl+1, b, bl)

pushBack :: Int -> Deque -> Deque
pushBack i (f, fl, b, bl) = (f, fl, i:b, bl+1)

popFront :: Deque -> (Maybe Int, Deque)
popFront ([], 0, [], 0) = (Nothing, empty)
popFront ((fh:ft), fl, b, bl) = (Just fh, (ft, fl-1, b, bl))
popFront ([], 0, b, bl) = popFront (reverse nfr, nfl, nb, nbl)
    where
        dbl2 = div bl 2
        (nfl, nbl) = (bl - dbl2, dbl2)
        (nb, nfr) = splitAt nfl b

popBack :: Deque -> (Maybe Int, Deque)
popBack ([], 0, [], 0) = (Nothing, empty)
popBack (f, fl, (bh:bt), bl) = (Just bh, (f, fl, bt, bl-1))
popBack (f, fl, [], 0) = popBack (nf, nfl, reverse nbr, nbl)
    where
        dfl2 = div fl 2
        (nfl, nbl) = (dfl2, fl - dfl2)
        (nf, nbr) = splitAt nfl f
