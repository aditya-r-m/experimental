import Unsafe.Coerce
uc = Unsafe.Coerce.unsafeCoerce

-- y f = f (y f)
y :: (t -> t) -> t
y f = (\x -> f (uc x x)) (\x -> f (uc x x))

partialFactorial :: (Int -> Int) -> Int -> Int
partialFactorial _ 0 = 1
partialFactorial self x = x * self (x - 1)

factorial :: Int -> Int
factorial = y partialFactorial

f9 :: Int
f9 = factorial 9

-- recursion without assigning names to functions
f9' :: Int
f9' = (\f -> (\x -> f (uc x x)) (\x -> f (uc x x)))
  (\slf -> \x -> if x == 0 then 1 else x * slf (x - 1)) 9

-- compact version
f9'' :: Int
f9'' = (\f -> (\x -> uc x x) (\x -> f (uc x x)))
  (\slf -> \x -> if x == 0 then 1 else x * slf (x - 1)) 9

main = print $ [f9, f9', f9'']
