import qualified Data.Map as M
import qualified Data.Set as S
import qualified Data.Maybe as Mb

type Map = M.Map
type Set = S.Set
type Graph = Map Int (Map Int Int)

cGraph :: Graph
cGraph = M.fromList [
        (0, M.fromList [(1, 5), (2, 10)]),
        (1, M.fromList [(0, 5), (2, 3)]),
        (2, M.fromList [(0, 10), (1, 5)])]

relaxEdges :: Map Int Int -> Int -> [(Int, Int)] -> [(Int, Int)]
relaxEdges _ _ [] = []
relaxEdges solMap d ((v, dv):xs)
    | M.member v solMap = relaxEdges solMap d xs
    | otherwise = (dv + d, v):(relaxEdges solMap d xs)

shortestPath :: Set (Int, Int) -> Map Int Int -> Map Int Int
shortestPath qSet solMap
    | S.null qSet = solMap
    | otherwise = shortestPath nqSet nSolMap
        where
            (d, u) = S.findMin qSet
            pnqSet = S.delete (d, u) qSet
            nSolMap = if M.member u solMap then solMap else M.insert u d solMap
            nqSet = if M.member u solMap then pnqSet else
                (S.union pnqSet . S.fromList . relaxEdges nSolMap d . M.toList . Mb.fromJust . M.lookup u) cGraph

main = print $ shortestPath (S.fromList [(0, 0)]) M.empty
