suffixSumUsingApplicatives :: [Integer] -> [Integer]
suffixSumUsingApplicatives = foldr (curry $ (:) <$> uncurry (flip $ (+) . head) <*> snd) [0]

suffixSumUsingMonads :: [Integer] -> [Integer]
suffixSumUsingMonads = foldr ((>>= (:)) .  (flip $ (+) . head)) [0]
