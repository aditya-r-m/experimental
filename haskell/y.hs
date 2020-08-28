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

main = print $ factorial 9
