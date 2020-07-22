import qualified Data.Set as S

type Set = S.Set
type ISet = Set Int

l :: Int
l = 10^6

foldSieve :: ISet -> Int -> ISet
foldSieve sieve i
  | S.member i sieve = S.difference sieve $ S.fromList [2*i,3*i..l]
  | otherwise = sieve

sieve :: ISet
sieve = (S.fromList >>= foldl foldSieve) [2..l]
