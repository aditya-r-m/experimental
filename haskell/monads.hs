import qualified Control.Monad as Mn

p :: [(Int, Int)]
p = do
  x <- [1..4]
  y <- [1..4]
  Mn.guard (even (x + y))
  return (x, y)

q :: [(Int, Int)]
q = [1..4] >>= (\x -> [1..4] >>= (\y -> (Mn.guard (even (x + y)) >> [(x, y)])))

r :: [(Int, Int)]
r = [(x, y) | x <- [1..4], y <- [1..4], even (x + y)]

type Pole = (Int, Int)
type Birds = Int

landLeft :: Birds -> Pole -> Maybe Pole
landLeft b (l, r)
    | abs (b + l - r) <= 4 = Just (b + l, r)
    | otherwise = Nothing

landRight :: Birds -> Pole -> Maybe Pole
landRight b (l, r)
    | abs (b + r - l) <= 4 = Just (l, b + r)
    | otherwise = Nothing


foo :: Maybe String
foo = do
    x <- Just 3
    y <- Just "!"
    Nothing
    return (show x ++ y)

bar :: Maybe String
bar = Just 3 >>= (\x->
        Just "!" >> Just "#" >>= (\y ->
        Just (show x ++ y)))

wopwop :: Maybe Char
wopwop = do
    (x:xs) <- return ""
    return x

main = do
  print p
  print q
  print r
  print wopwop

