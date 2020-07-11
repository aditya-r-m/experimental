
type Q = ([Int], [Int])

push :: Int -> Q -> Q
push x (l, r) = (x:l, r)

pop :: Q -> Maybe (Q, Int)
pop ([], []) = Nothing
pop (l, []) = pop ([], reverse l)
pop (l, x:xs) = Just ((l, xs), x)

