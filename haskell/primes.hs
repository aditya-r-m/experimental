import qualified Data.Bits as B
import qualified Data.Set as S

-- Sieve of Eratosthenes

foldSieve :: S.Set Int -> Int -> S.Set Int
foldSieve sieve i
  | S.member i sieve = S.difference sieve $ S.fromList [2*i,3*i..S.findMax sieve]
  | otherwise = sieve

sieve :: S.Set Int
sieve = (S.fromList >>= foldl foldSieve) [2..10^6]

-- Miller–Rabin primality test

(>>>) :: Int -> Int
(>>>) = flip B.shiftR 1

modExp :: Int -> Int -> Int -> Int
modExp p 0 b = 1
modExp p e b
  | even e = modExp p ((>>>) e) (mod (b^2) p)
  | otherwise = mod (b * modExp p (e - 1) b) p

witnesses :: [Int]
witnesses = [2,3,5,7,11,13,17,19,23,29,31,37]

testifiedCompositeness :: Int -> Int -> Int -> Bool
testifiedCompositeness p r wd
  | wd == 1 = False
  | otherwise = notElem (p - 1) $ take r $ iterate (flip mod p . (^2)) wd

isPrime :: Int -> Bool
isPrime p
  | p == 2 = True
  | p < 2 || even p = False
  | otherwise = not $ any (testifiedCompositeness p r) $ map (modExp p d) $ filter (<p) witnesses
  where
    l = takeWhile even $ iterate (>>>) (p - 1)
    (r, d) = (,) <$> length <*> (>>>) . last $ l
