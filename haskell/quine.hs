render s = do
  putStrLn s
  putStrLn $ "main = render " ++ show s
main = render "render s = do\n  putStrLn s\n  putStrLn $ \"main = render \" ++ show s"      
