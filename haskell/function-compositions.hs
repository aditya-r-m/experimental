suffixSum :: [Integer] -> [Integer]
suffixSum (x:[]) = [x,0]
suffixSum (x:ls) = (x+h:h:ss) where (h:ss) = suffixSum ls

suffixSumUsingApplicatives :: [Integer] -> [Integer]
suffixSumUsingApplicatives = foldr (curry $ (:) <$> uncurry (flip $ (+) . head) <*> snd) [0]

suffixSumUsingMonads :: [Integer] -> [Integer]
suffixSumUsingMonads = foldr ((>>= (:)) .  (flip $ (+) . head)) [0]

cartesianProduct :: [[a]] -> [[a]]
cartesianProduct [] = [[]]
cartesianProduct (l:ls) = [i:r | i <- l, r <- cartesianProduct ls]

cartesianProductUsingApplicatives :: [[a]] -> [[a]]
cartesianProductUsingApplicatives = foldr ((<*>) . (<$>) (:)) [[]]
