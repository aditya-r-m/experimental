# y(f)(a) = f(y(f))(a)
y = lambda f: (lambda x: lambda a: f(x(x))(a)) (lambda x: lambda a: f(x(x))(a))

partialFactorial = lambda slf: lambda a: a * slf(a - 1) if a else 1

factorial = y(partialFactorial)

print(factorial(9))

# recursion without assigning names to functions
print(
  (lambda f: (lambda x: lambda a: f(x(x))(a)) (lambda x: lambda a: f(x(x))(a)))
  (lambda slf: lambda a: a * slf(a - 1) if a else 1)
  (9)
)

# compact version
print(
  (lambda f: (lambda x: x(x)) (lambda x: lambda a: f(x(x))(a)))
  (lambda slf: lambda a: a * slf(a - 1) if a else 1)
  (9)
)
