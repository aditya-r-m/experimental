

fl :: ([Int] -> Int -> [Int]) -> [Int] -> [Int] -> [Int]
fl _ a [] = a
fl f a (x:xs) = fl f (f a x) xs

fr :: (Int -> [Int] -> [Int]) -> [Int] -> [Int] -> [Int]
fr _ a [] = a
fr f a (x:xs) = f x (fr f a xs)

r :: [Int] -> [Int]
r = fl (flip (:)) []

i :: [Int] -> [Int]
i = fr (:) []
