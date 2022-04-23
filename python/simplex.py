# python2
from sys import stdin

def get_pivot(n, m, t, basis):
    lr, lim, done = t[-1], len(t[0]) - 1, True
    for en_c in range(lim):
        if int(lr[en_c]*1000+0.5)/(1000.) > 0:
            done = False
            break
    if done: return None

    min_rows, min_ratio = [], 1 << 30
    for i, r in enumerate(t[:n]):
        if int(r[en_c]*1000+0.5)/(1000.) > 0:
            ratio = int(r[-1]/r[en_c]*1000+0.5)/(1000.)
            if ratio < min_ratio: min_rows, min_ratio = [i], ratio
            elif ratio == min_ratio: min_rows.append(i)
    if not len(min_rows): return 0 # unbounded
    en_r, ex_c, min_r_set = min_rows[0], 100, set(min_rows)
    for var in basis:
        if basis[var] in min_r_set and var < ex_c: en_r, ex_c = basis[var], var
    return en_r, en_c, ex_c


def process_pivot(t, i, j):
    p_v = 1 / t[i][j]
    p_r = t[i] = list(map(lambda v: v * p_v, t[i]))
    for k, r in enumerate(t):
        if k != i:
            h = r[j]
            for col, v in enumerate(r): r[col] = v - h * p_r[col]


def simplex(n, m, t, basis):
    p = get_pivot(n, m, t, basis)
    while p:
        enr, enc, exc = p
        basis[enc] = enr
        try: del basis[exc]
        except: pass
        process_pivot(t, enr, enc)
        p = get_pivot(n, m, t, basis)
    return p


def allocate_ads(n, m, A, b, c):
    # add slack variables & artificial
    slack_pad = [0] * n
    A = map(lambda row: row + slack_pad, A)
    c += slack_pad
    for i in range(n):
        A[i][m + i] = 1
    negative_rows = []
    for i, v in enumerate(b):
        if v < 0: negative_rows.append(i)
    # We always append artificial variables to the left of the matrix so that bland's rule prefers them as the leaving variables
    # The following is an example where a bad degenracy causes problem with bland's rule if artificial variables are placed on the right
    # 3 3 \n 1 0 0 \n 0 -1 0 \n 0 1 0 \n 5 -5 5 \n 1 -1 1
    # Note that the above case contains an equality hidden in form of 2 inequalities
    artificial_var_count, artificial_var_counter = len(negative_rows), 0
    if artificial_var_count:
        artificial_pad = [0] * artificial_var_count
        A = map(lambda row: artificial_pad + row, A)
        for i in range(n):
            if b[i] < 0:
                A[i][artificial_var_counter], artificial_var_counter = -1, artificial_var_counter + 1
                A[i], b[i] = map(lambda v: -v, A[i]), -b[i]
        c = artificial_pad + c

    tableau = []
    for i, row in enumerate(A):
        tableau.append(row + [b[i]])
    tableau.append(c + [0])

    # if needed, perform phase 1 operations to find initial feasible solution (http://www.maths.qmul.ac.uk/~ffischer/teaching/opt/notes/notes8.pdf)
    if artificial_var_count:
        basis = {}
        c_phase_one = [-1] * artificial_var_count + [0] * (m + n + 1)
        for inr, nr in enumerate(negative_rows):
            basis[inr] = nr
            c_phase_one = map(lambda a, b: a + b, c_phase_one, tableau[nr])
        tableau.append(c_phase_one)
        simplex(n, m, tableau, basis)
        if any(c < artificial_var_count for c in basis): return [-1, None]
        basis = { var - artificial_var_count: basis[var] for var in basis }
        tableau.pop()
        tableau = map(lambda row: row[artificial_var_count:], tableau)
    else:
        basis = { m + s: s for s in range(n) }

    if simplex(n, m, tableau, basis) == 0: return [1, None]
    return [0, [tableau[basis[i]][-1] if i in basis else 0 for i in range(m)]]

'''
Input Format.
You are given a linear programming problem of the form 𝐴𝑥 ≤ 𝑏, 𝑥 ≥ 0,
∑︀𝑐𝑖𝑥𝑖 → max, where 𝐴 is a matrix 𝑝 × 𝑞, 𝑏 is a vector of length 𝑝,
𝑐 is a vector of length 𝑞 and 𝑥 is the unknown vector of length 𝑞.

The first line of the input contains integers 𝑝 and 𝑞 — the number of inequalities in the system and the
number of variables respectively. The next 𝑝 + 1 lines contain the coefficients of the linear inequalities
in the standard form 𝐴𝑥 ≤ 𝑏. Specifically, 𝑖-th of the next 𝑝 lines contains 𝑞 integers 𝐴𝑖1, 𝐴𝑖2, . . . , 𝐴𝑖𝑞,
and the next line after those 𝑝 contains 𝑝 integers 𝑏1, 𝑏2, . . . , 𝑏𝑝. These lines describe 𝑝 inequalities of
the form 𝐴𝑖1 · 𝑥1 + 𝐴𝑖2 · 𝑥2 + · · · + 𝐴𝑖𝑞 · 𝑥𝑞 ≤ 𝑏𝑖.
The last line of the input contains 𝑞 integers — the coefficients 𝑐𝑖 of the objective ∑︀𝑐𝑖𝑥𝑖 → max.
Constraints. 1 ≤ 𝑛, 𝑚 ≤ 100; −100 ≤ 𝐴𝑖𝑗 ≤ 100; −1 000 000 ≤ 𝑏𝑖 ≤ 1 000 000; −100 ≤ 𝑐𝑖 ≤ 100.

Output Format.
If there is no feasible solultion, output “No solution” (without quotes).
If you can get as much revenue as you want despite all the requirements, output “Infinity” (without quotes).
If the maximum possible revenue is bounded, output two lines. On the first line,
On the first line, output “Bounded solution” (without quotes).
On the second line, output 𝑞 real numbers — the optimal values of the vector 𝑥.
'''
def main():
    n, m = map(int, stdin.readline().split())
    A = [map(float, stdin.readline().split()) for _ in range(n)]
    b = map(int, stdin.readline().split())
    c = map(int, stdin.readline().split())

    anst, ansx = allocate_ads(n, m, A, b, c)
    if anst == -1:
        print("No solution")
    if anst == 0:
        print("Bounded solution")
        print(' '.join(map(lambda x: '%.15f' % x, ansx)))
    if anst == 1:
        print("Infinity")

main()
