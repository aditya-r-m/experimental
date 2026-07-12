import numpy as np
from manim import *

CS = [GREEN,RED,YELLOW,TEAL]

class Determinant(Scene):
   def construct(self):
        '''
        This animation provides a vector-oriented view to determinants.
        The textbook approach is often focused on a covector oriented view, with transformations as left-multiplications.
        The distinction is not important in this context, but matters when solving systems of equations.

        Let's call the n-dimensional version of the volume the "measure".
        1D measure is simply the length of any line.
        This is the fundamental building block which can be stretched into higher dimensions to create a sequence of measures.

        First, we will look at a simple efficient determinant computation by shearing the vectors into an orthogonal arrangement.
        The 1D computation is trivial, the single value in a 1x1 matrix represents this measure.
        '''
        line = NumberLine(x_range=(-4, 4, 1)).move_to(RIGHT*3)
        self.play(Create(line, run_time=1, lag_ratio=0.1))
        tex_0 = MathTex(r"det \begin{bmatrix} 2 \end{bmatrix} = 2").move_to(LEFT*4)
        tex_1 = MathTex(r"det \begin{bmatrix} -3 \end{bmatrix} = -3").move_to(LEFT*4)
        tex_0[0][4].set_color(CS[0])
        tex_1[0][4:6].set_color(CS[0])
        arrows = [
            Arrow(color=CS[0]).put_start_and_end_on(line.n2p(0), line.n2p(2)),
            Arrow(color=CS[0]).put_start_and_end_on(line.n2p(0), line.n2p(-3)),
        ]
        self.play(Create(tex_0),
                  Create(arrows[0]))
        self.wait()
        self.play(Uncreate(tex_0))
        self.play(Create(tex_1),
                  ReplacementTransform(arrows[0], arrows[1]))
        self.wait()
        self.play(Uncreate(tex_1),
                  Uncreate(line),
                  Uncreate(arrows[1]))
        '''
        2D version of this measure is area of the parallelogram, the simplest case being a rectangle.
        The key idea is that any parallelogram can be changed to a rectangle of the same area by shear transformations.
        Shear can be though of as sliding the full area as smoothly connected parallel lines of constant length.
        Finally, we are left with just a rectangle with edge lengths in the diagonal, determinant being the simple product.
        '''
        get_arrows = lambda arrays: [
            Arrow(color=CS[0]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(*arrays[0].flatten())),
            Arrow(color=CS[1]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(*arrays[1].flatten())),
        ]
        get_polygon = lambda arrays: Polygon(grid.c2p(0, 0),
                                            grid.c2p(*arrays[0].flatten()),
                                            grid.c2p(*(arrays[0] + arrays[1]).flatten()),
                                            grid.c2p(*(arrays[1].flatten())),
                                            color=BLUE, fill_opacity=0.5)
        grid = NumberPlane(x_range=(-4, 4, 1)).move_to(RIGHT*3)
        self.play(Create(grid))
        arrays = [np.array([[1], [0]]), np.array([[0], [1]])]
        polygons = [get_polygon(arrays)]
        arrows = [get_arrows(arrays)]
        diff_arrows = [Arrow(color=CS[1]).put_start_and_end_on(
                             grid.c2p(*arrays[0].flatten()),
                             grid.c2p(*(arrays[0] + arrays[1]).flatten()))]
        arrays = [arrays[0] + arrays[1], arrays[1]]
        polygons.append(get_polygon(arrays))
        arrows.append(get_arrows(arrays))
        diff_arrows.append(Arrow(color=CS[0]).put_start_and_end_on(
                             grid.c2p(*arrays[1].flatten()),
                             grid.c2p(*(arrays[0] + arrays[1]).flatten())))
        arrays = [arrays[0], arrays[0] + arrays[1]]
        polygons.append(get_polygon(arrays))
        arrows.append(get_arrows(arrays))
        polygons.reverse()
        arrows.reverse()
        diff_arrows.reverse()
        tex = MathTex(r'{{det}} \begin{bmatrix}',
                      r'1 & 1 \\ 1 & 2 \end{bmatrix} \\',
                      r'= {{det}} \begin{bmatrix}',
                      r'1 & 0 \\ 1 & 1 \end{bmatrix} \\',
                      r'= {{det}} \begin{bmatrix}',
                      r'1 & 0 \\ 0 & 1 \end{bmatrix} \\',
                      r'= 1', substrings_to_isolate=["0"]).move_to(LEFT*4)
        for t in tex[2::4]:
            t[0:3:2].set_color(CS[0])
            t[1:4:2].set_color(CS[1])
        tex.set_color_by_tex("0", WHITE)
        self.play(Create(tex),
                  Create(polygons[0]),
                  Create(arrows[0][0]),
                  Create(arrows[0][1]))
        self.wait()
        self.play(Create(diff_arrows[0]))
        self.play(ReplacementTransform(polygons[0], polygons[1]),
                  ReplacementTransform(arrows[0][0], arrows[1][0]),
                  ReplacementTransform(arrows[0][1], arrows[1][1]))
        self.play(Uncreate(diff_arrows[0]))
        self.wait()
        self.play(Create(diff_arrows[1]))
        self.play(ReplacementTransform(polygons[1], polygons[2]),
                  ReplacementTransform(arrows[1][0], arrows[2][0]),
                  ReplacementTransform(arrows[1][1], arrows[2][1]))
        self.play(Uncreate(diff_arrows[1]))
        self.wait()
        self.play(Uncreate(tex),
                  Uncreate(grid, lag_ratio=0),
                  Uncreate(polygons[2]),
                  Uncreate(arrows[2][0]),
                  Uncreate(arrows[2][1]))
        self.wait()
        '''
        For all practical purposes, this shearing algorithm is sufficient.
        In higher dimensions, the shear operations slide continuous copies of parallel n-1 dimensional objects instead of lines.

        In the next section, we work towards a compact closed form computation.
        Focusing on the 2x2 case, we can eliminate lower half below the triangle with a simple shear matrix multiplication.
        This leads to a very nice formula, where we're choosing complementary components from two vectors and multiplying them for the result.
        The most interesting bit is that the two products work against each other.
        The best analogy I can think of is that one pair is trying to inflate the 2D balloon the default way,
        while the second pair is trying to inflate it while pushing its insides out.
        '''
        get_arrows = lambda arrays: [
            Arrow(color=CS[0]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(*arrays[0].flatten())),
            Arrow(color=CS[1]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(*arrays[1].flatten())),
        ]
        get_polygon = lambda arrays: Polygon(grid.c2p(0, 0),
                                            grid.c2p(*arrays[0].flatten()),
                                            grid.c2p(*(arrays[0] + arrays[1]).flatten()),
                                            grid.c2p(*(arrays[1].flatten())),
                                            color=BLUE, fill_opacity=0.5)
        grid = NumberPlane(x_range=(-2, 6, 1), y_range=(-2, 6, 1)).move_to(RIGHT*3)
        self.play(Create(grid))
        arrays = [np.array([[3], [3]]), np.array([[1], [2]])]
        polygons = [get_polygon(arrays)]
        arrows = [get_arrows(arrays)]
        diff_arrows = [
            Arrow(color=CS[1]).put_start_and_end_on(
                 grid.c2p(*(arrays[0] - arrays[1]).flatten()),
                 grid.c2p(*(arrays[0]).flatten())),
            Arrow(color=CS[1]).put_start_and_end_on(
                 grid.c2p(*(arrays[0] - 2*arrays[1]).flatten()),
                 grid.c2p(*(arrays[0] - arrays[1]).flatten())),
        ]
        arrays = [arrays[0] - 3/2*arrays[1], arrays[1]]
        polygons.append(get_polygon(arrays))
        arrows.append(get_arrows(arrays))
        tex = MathTex(
            r'{{ det }} \begin{bmatrix}',
            r'{{x_0}} & {{x_1}} \\ {{y_0}} & {{y_1}}',
            r'\end{bmatrix} \\ =',
            r'{{ det }} \begin{bmatrix}',
            r'{{x_0}} & {{x_1}} \\ {{y_0}} & {{y_1}}',
            r'\end{bmatrix} \begin{bmatrix} 1 & 0 \\ -\frac{y_0}{y_1} & 1 \end{bmatrix} \\ = {{ det }} \begin{bmatrix}',
            r'{{x_0 - \frac{y_0 x_1}{y_1}}} & {{x_1}} \\ 0 & {{y_1}}',
            r'\end{bmatrix} \\ =',
            r'{{x_0}} {{y_1}} - {{y_0}} {{x_1}}').move_to(LEFT*4)
        for c in ["x", "y"]:
            for i in range(2):
                tex.set_color_by_tex(f"{c}_{i}", CS[i])
        tex[22][:10].set_color(CS[0])
        self.play(Create(tex),
                  Create(polygons[0]),
                  Create(arrows[0][0]),
                  Create(arrows[0][1]))
        self.wait()
        self.play(Create(diff_arrows[0]), Create(diff_arrows[1]))
        self.play(ReplacementTransform(polygons[0], polygons[1]),
                  ReplacementTransform(arrows[0][0], arrows[1][0]),
                  ReplacementTransform(arrows[0][1], arrows[1][1]))
        self.wait()
        self.play(Uncreate(tex),
                  Uncreate(grid, lag_ratio=0),
                  Uncreate(polygons[1]),
                  Uncreate(arrows[1][0]),
                  Uncreate(arrows[1][1]),
                  Uncreate(diff_arrows[0]),
                  Uncreate(diff_arrows[1]))
        self.wait()
        '''
        The same concept of two-valued orientation generalizes in higher dimensions.
        it doesn't matter whether we turn a sphere inside-out horizontally or vertically, the inner surface becomes the outer surface.
        While this is much harder to imagine this starting with 3D surface of a 4D volume, we generalize the orientation sign as follows,
        - let's restrict our focus to 4 4D vectors which are almost diagonal.
        - In the first case, w & x components are similar to the 2D case, and y2z3 can simply be thought of as uniform weight per unit area.
          we can see how wxyz and xwyz work against earch other from our previous formula.
        - In the second case, x & y components are similar to the 2D case, and w0z3 can be though of as uniform density.
          again, we see that wxyz and wyxz work against each other.
        Thus, swapping the order of any 2 dimensions flips the sign of the permutations combination!
        '''
        tex = MathTex(
            r'''
            {{ det }} \begin{bmatrix}
            {{w_0}} & {{w_1}} & 0 & 0 \\
            {{x_0}} & {{x_1}} & 0 & 0 \\
            0 & 0 & {{y_2}} & 0 \\
            0 & 0 & 0 & {{z_3}} \end{bmatrix}
            = {{w_0}} {{x_1}} {{y_2}} {{z_3}} - {{x_0}} {{w_1}} {{y_2}} {{z_3}} \\
            {{ det }} \begin{bmatrix}
            {{w_0}} & 0 & 0 & 0 \\
            0 & {{x_1}} & {{x_2}} & 0 \\
            0 & {{y_1}} & {{y_2}} & 0 \\
            0 & 0 & 0 & {{z_3}}
            \end{bmatrix}
            = {{w_0}} {{x_1}} {{y_2}} {{z_3}} - {{w_0}} {{y_1}} {{x_2}} {{z_3}}
            ''')
        for c in ["w","x", "y", "z"]:
            for i in range(4):
                tex.set_color_by_tex(f"{c}_{i}", CS[i])
        self.play(Create(tex))
        self.wait()
        self.play(Uncreate(tex))
        grid = NumberPlane(x_range=(-2, 6, 1), y_range=(-2, 6, 1)).move_to(RIGHT*3)
        self.play(Create(grid))
        tex = MathTex(
            r'''{{ det }} \begin{bmatrix} {{v_x}} + {{v_y}} & {{w}} \end{bmatrix} \\
            = {{ det }} \begin {bmatrix} {{v_x}} & {{w}} \end{bmatrix} \\
            + {{ det }} \begin {bmatrix} {{v_y}} & {{w}} \end{bmatrix}
            ''').move_to(LEFT*4)
        tex.set_color_by_tex("v_x", CS[0])
        tex.set_color_by_tex("v_y", CS[0])
        tex.set_color_by_tex("w", CS[1])
        '''
        Apart from the sign flips on swaps, the only other part we need is that all permutations must play a role in a symmetric way.
        The intuition for this is that if we can form n-dimensional volume by picking n distinct orthogonal parts
        of n distinct vectors.
        Picking multiple parts from the same vector or aligned parts from different vectors does't create n-d volumes.
        This is also why we don't see x0*y0 or x0*x1 in the 2D determinant formula.
        More rigorously, the following property can be used to split the first vector into n subproblems, second into n-1, and so on.
        '''
        arrows = [
            Arrow(color=CS[1]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(-1, 2)),
            Arrow(color=CS[0]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(3, 3)),
            Arrow(color=CS[0]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(3, 0)),
            Arrow(color=CS[0]).put_start_and_end_on(grid.c2p(3, 0), grid.c2p(3, 3)),
            Arrow(color=CS[1]).put_start_and_end_on(grid.c2p(3, 0), grid.c2p(2, 2)),
        ]
        polygons = [
            Polygon(grid.c2p(0, 0),
                    grid.c2p(2, 2),
                    grid.c2p(3, 3),
                    grid.c2p(2, 5),
                    grid.c2p(1, 4),
                    grid.c2p(-1, 2),
                    color=BLUE, fill_opacity=0.5),
            Polygon(grid.c2p(0, 0),
                    grid.c2p(3, 0),
                    grid.c2p(3, 3),
                    grid.c2p(2, 5),
                    grid.c2p(2, 2),
                    grid.c2p(-1, 2),
                    color=BLUE, fill_opacity=0.5),
        ]
        self.play(Create(tex),
                  Create(polygons[0]),
                  Create(arrows[0]),
                  Create(arrows[1]))
        self.wait()
        self.play(Uncreate(arrows[1]))
        self.play(Create(arrows[2]))
        self.play(Create(arrows[3]))
        self.play(Create(arrows[4]))
        self.play(ReplacementTransform(polygons[0], polygons[1]))
        self.wait()
        polygons[1].set_shebang(polygons[1].get_center())
        self.play(Uncreate(grid),
                  Uncreate(tex),
                  Uncreate(arrows[0]),
                  Uncreate(arrows[2]),
                  Uncreate(arrows[3]),
                  Uncreate(arrows[4]),
                  polygons[1].animate.scale(0).set_opacity(0))
        self.remove(polygons[1])
        '''
        Using this property, the determinant can be expanded level-by-level while clearing rows one-by-one.
        Eventually we end up with all the permutations, with the orientation defined by the swap-distance from identity permutation.
        This finally can be summarized in a single compact equation.
        '''
        tex_str = r'''
            &{{det}} \begin{bmatrix}
            {{w_0}} & {{w_1}} & {{w_2}} & {{w_3}} \\
            {{x_0}} & {{x_1}} & {{x_2}} & {{x_3}} \\
            {{y_0}} & {{y_1}} & {{y_2}} & {{y_3}} \\
            {{z_0}} & {{z_1}} & {{z_2}} & {{z_3}} \\
            \end{bmatrix} \\
            '''
        c = r"=\ &"
        for d in ["w","x","y","z"]:
            tex_str += rf"{c}{{det}} \begin{{bmatrix}}"
            for r in ["w","x","y","z"]:
                tex_str += rf" {{{{{r}_0}}}} " if d == r else rf"0 "
                tex_str += rf"& {{{{{r}_1}}}} & {{{{{r}_2}}}} & {{{{{r}_3}}}} \\"
            tex_str += r"\end{bmatrix}"
            c = r"&+\ "
        tex_str += r"\\"
        c = r"=\ &"
        for d in ["w","x","y","z"]:
            tex_str += rf"{c}{{det}} \begin{{bmatrix}}"
            for r in ["w","x","y","z"]:
                tex_str += rf" {{{{{r}_0}}}} & 0 & 0 & 0 \\" if d == r else rf"0 & {{{{{r}_1}}}} & {{{{{r}_2}}}} & {{{{{r}_3}}}} \\"
            tex_str += r"\end{bmatrix}"
            c = r"&+\ "
        tex = MathTex(tex_str)
        tex.scale_to_fit_width(12)
        for c in ["w","x", "y", "z"]:
            for i in range(4):
                tex.set_color_by_tex(f"{c}_{i}", CS[i])
        self.play(Create(tex))
        self.wait()
        self.play(Uncreate(tex))
        tex_str = r'''
            &{{det}} \begin{bmatrix}
            {{w_0}} & 0 & 0 & 0 \\
            0 & {{x_1}} & {{x_2}} & {{x_3}} \\
            0 & {{y_1}} & {{y_2}} & {{y_3}} \\
            0 & {{z_1}} & {{z_2}} & {{z_3}} \\
            \end{bmatrix} \\
            '''
        c = r"=\ &"
        for d in ["x","y","z"]:
            tex_str += rf"{c}{{det}} \begin{{bmatrix}}"
            tex_str += rf" {{{{w_0}}}} & 0 & 0 & 0 \\"
            for r in ["x","y","z"]:
                tex_str += rf"0 & {{{{{r}_1}}}} " if d == r else rf"0 & 0 "
                tex_str += rf"& {{{{{r}_2}}}} & {{{{{r}_3}}}} \\"
            tex_str += r"\end{bmatrix}"
            c = r"&+\ "
        tex_str += r"\\"
        c = r"=\ &"
        for d in ["x","y","z"]:
            tex_str += rf"{c}{{det}} \begin{{bmatrix}}"
            tex_str += rf" {{{{w_0}}}} & 0 & 0 & 0 \\"
            for r in ["x","y","z"]:
                tex_str += rf" 0 & {{{{{r}_1}}}} & 0 & 0 \\" if d == r else rf"0 & 0 & {{{{{r}_2}}}} & {{{{{r}_3}}}} \\"
            tex_str += r"\end{bmatrix}"
            c = r"&+\ "
        tex = MathTex(tex_str)
        tex.scale_to_fit_width(12)
        for c in ["w","x", "y", "z"]:
            for i in range(4):
                tex.set_color_by_tex(f"{c}_{i}", CS[i])
        self.play(Create(tex))
        self.wait()
        self.play(Uncreate(tex))
        '''
        This gives us all the tools that we need to build the simple compact formulae : sum of all signed permutation products!
        '''
        tex_str = r'''
            &{{det}} \begin{bmatrix}
            {{w_0}} & 0 & 0 & 0 \\
            0 & {{x_1}} & 0 & 0 \\
            0 & 0 & {{y_2}} & {{y_3}} \\
            0 & 0 & {{z_2}} & {{z_3}} \\
            \end{bmatrix} \\
            '''
        c = r"=\ &"
        for d in ["y","z"]:
            tex_str += rf"{c}{{det}} \begin{{bmatrix}}"
            tex_str += rf" {{{{w_0}}}} & 0 & 0 & 0 \\"
            tex_str += rf"0 & {{{{x_1}}}} & 0 & 0 \\"
            for r in ["y","z"]:
                tex_str += rf"0 & 0 & {{{{{r}_2}}}} " if d == r else rf"0 & 0 & 0 "
                tex_str += rf"& {{{{{r}_3}}}} \\"
            tex_str += r"\end{bmatrix}"
            c = r"&+\ "
        tex_str += r"\\"
        c = r"=\ &"
        for d in ["y","z"]:
            tex_str += rf"{c}{{det}} \begin{{bmatrix}}"
            tex_str += rf" {{{{w_0}}}} & 0 & 0 & 0 \\"
            tex_str += rf"0 & {{{{x_1}}}} & 0 & 0 \\"
            for r in ["y","z"]:
                tex_str += rf" 0 & 0 & {{{{{r}_2}}}} & 0 \\" if d == r else rf"0 & 0 & 0 & {{{{{r}_3}}}} \\"
            tex_str += r"\end{bmatrix}"
            c = r"&+\ "
        tex = MathTex(tex_str)
        tex.scale_to_fit_width(8)
        for c in ["w","x", "y", "z"]:
            for i in range(4):
                tex.set_color_by_tex(f"{c}_{i}", CS[i])
        self.play(Create(tex))
        self.wait()
        self.play(Uncreate(tex))
        tex = MathTex(r"\sum_{\sigma \in S_n} sgn(\sigma) \prod_{i=1}^n a_{\sigma(i)i}")
        self.play(Create(tex))
        self.wait()
        self.play(Uncreate(tex))

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
 