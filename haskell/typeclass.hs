
class T a where f :: (a i j) -> j i

data D x y = D (y x) deriving (Show)
instance T D where f (D v) = v

main = print $ f (D [0])
