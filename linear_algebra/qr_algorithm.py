import numpy as np
from manim import *

CS = [GREEN,RED,YELLOW,TEAL]

def qr(A):
    """
    Computes the QR decomposition of matrix A using 
    the Modified Gram-Schmidt process.
    """
    m, n = A.shape
    Q = np.zeros((m, n))
    R = np.zeros((n, n))
    # Work on a copy to avoid modifying the original matrix
    V = A.copy().astype(float)
    for i in range(n):
        # Compute the norm of the current column
        R[i, i] = np.linalg.norm(V[:, i])
        # Normalize to get the orthogonal vector component
        Q[:, i] = V[:, i] / R[i, i]
        # Project and subtract from remaining columns
        for j in range(i + 1, n):
            R[i, j] = np.dot(Q[:, i], V[:, j])
            V[:, j] -= R[i, j] * Q[:, i]
    return Q, R

def get_arrows(grid, m, q):
    # _, ev = np.linalg.eig(a)
    return [
        Arrow(color=CS[0]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(m[0][0], m[1][0])),
        Arrow(color=CS[1]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(m[0][1], m[1][1])),
        Arrow(color=CS[2]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(q[0][0], q[1][0])),
        Arrow(color=CS[3]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(q[0][1], q[1][1])),
    ]

class QR(Scene):
    def construct(self):
        grid = NumberPlane(x_range=(-4, 4, 1))
        self.play(Create(grid))
        m = np.array([[3,1],[1,3]])
        q = np.array([[1,0],[0,1]])
        arrows = get_arrows(grid, m, q)
        self.play(Create(arrows[0]),
                  Create(arrows[1]),
                  Create(arrows[2]),
                  Create(arrows[3]),
        )
        for _ in range(10):
            q = m @ q
            q, _ = qr(q)
            new_arrows = get_arrows(grid, m, q)
            self.play(ReplacementTransform(arrows[0], new_arrows[0]),
                      ReplacementTransform(arrows[1], new_arrows[1]),
                      ReplacementTransform(arrows[2], new_arrows[2]),
                      ReplacementTransform(arrows[3], new_arrows[3]),
            )
            arrows = new_arrows
        # for faster convergence, we can follow a method similar to exponentiation by squaring
        # A_0 = Q_0 R_0 -> E_0 = Q_0
        # A_1 = Q_0 R_0 Q_0 R_0 = Q_0 Q_1 R_1 Q_0 -> E_1 = Q_01
        # A_2 = Q_01 R_01 Q_01 R_01 = Q_01 Q_2 R_2 R_01 -> E_2 = Q_02
 
