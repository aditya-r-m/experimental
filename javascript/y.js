// y(f)(a) = f(y(f))(a)
y =  f => (x => a => f(x(x))(a)) (x => a => f(x(x))(a))

partialFactorial = slf => a => a ? a * slf(a - 1) : 1

factorial = y(partialFactorial)

console.log(factorial(9))

// recursion without assigning names to functions
console.log(
  (f => (x => a => f(x(x))(a)) (x => a => f(x(x))(a)))
  (slf => a => a ? a * slf(a - 1) : 1)
  (9)
)

// compact version
console.log(
  (f => (x => x(x)) (x => a => f(x(x))(a)))
  (slf => a => a ? a * slf(a - 1) : 1)
  (9)
)
