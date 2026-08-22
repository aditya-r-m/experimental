# docker run -it --rm -v "$(pwd)":/manim manimcommunity/manim manim linear_algebraic_computations.py

import numpy as np
from manim import *

CS = [GREEN,RED,YELLOW,TEAL]

class Projection(Scene):
   def construct(self):
        Text.set_default(color=LIGHT_GRAY, font_size=24)
        MathTex.set_default(font_size=42)
        title_texts = [
            "Rotation Matrix",
            "Projection Vector",
            "Rotation Transpose",
            "Spectral Theorem",
            "Eigenvector Computation",
            "Singular Value Decomposition",
            "PCA Dimension Reduction",
            "Projection Matrix",
            "OLS Linear Regression",
        ]
        node_texts = list(map(lambda t: Text(t, color=WHITE, font="Consolas", font_size=16), title_texts))
        layout = [
            np.array([-3,3,0]),
            np.array([3,3,0]),
            np.array([-3,2,0]),
            np.array([-3,1,0]),
            np.array([-3,0,0]),
            np.array([-3,-1,0]),
            np.array([-3,-2,0]),
            np.array([3,-1,0]),
            np.array([3,-2,0]),
        ]
        edges = [
            [],
            [0],
            [0,1],
            [2,1],
            [3,1],
            [4],
            [5],
            [5,1],
            [7],
        ]
        for (i, node_text) in enumerate(node_texts):
            node_text.move_to(layout[i])
            arrows = []
            for u in edges[i]:
                src, dst = node_texts[u], node_text
                sx, dx = layout[u][0], layout[i][0]
                if sx == dx:
                    start = src.get_bottom()
                    end = dst.get_top()
                elif sx < dx:
                    start = src.get_right()
                    end = dst.get_left()
                else:
                    start = src.get_left()
                    end = dst.get_right()
                arrows.append(Arrow(
                    start=start,
                    end=end,
                    stroke_width=2,
                    tip_length=0.1,
                    max_stroke_width_to_length_ratio=100,
                    max_tip_length_to_length_ratio=100,
                ))
            # self.play(Create(node_text), *(Create(arrow) for arrow in arrows))
        # self.wait(8)
        # self.play(FadeOut(*self.mobjects))
        
        grid = NumberPlane(
            x_range=(-4,4,1),
            axis_config={"stroke_width": 2, "color":LIGHT_GRAY},
            background_line_style={"stroke_opacity": 0}
        ).move_to(RIGHT*3)
        tex_f0 = MathTex(r"\text{optimizing} \ f(x,y) = x + y").move_to(LEFT*4+UP*2)
        tex_f10 = MathTex(r"{{ \nabla f(x,y) = \begin{bmatrix} }} \partial f / \partial x \\ \partial f / \partial y {{ \end{bmatrix} }}").next_to(tex_f0, DOWN)
        tex_f11 = MathTex(r"{{ \nabla f(x,y) = \begin{bmatrix} }} 1 \\ 1 {{ \end{bmatrix} }}").next_to(tex_f0, DOWN)
        tex_g0 = MathTex(r"\text{over} \ g(x,y) = x^2 + y^2 = 1").next_to(tex_f11, DOWN)
        tex_g10 = MathTex(r"{{ \nabla g(x,y) = \begin{bmatrix} }} \partial g / \partial x \\ \partial g / \partial y {{ \end{bmatrix} }}").next_to(tex_g0, DOWN)
        tex_g11 = MathTex(r"{{ \nabla g(x,y) = \begin{bmatrix} }} 1 \\ 1 {{ \end{bmatrix} }}").next_to(tex_g0, DOWN)
        tex_s = MathTex(r"\text{requires} \ \nabla f(x,y) = \lambda \nabla g(x,y)").next_to(tex_g11, DOWN)
        tex_f0.set_color(CS[0])
        tex_f10.set_color(CS[0])
        tex_f11.set_color(CS[0])
        tex_g0.set_color(CS[1])
        tex_g10.set_color(CS[1])
        tex_g11.set_color(CS[1])
        tex_s.set_color(CS[-1])
        line_f0 = Line(start=grid.c2p(-4, -4), end=grid.c2p(-4, -4), color=CS[0], stroke_opacity=0)
        line_f0_b = line_f0.copy()
        line_f1 = Line(start=grid.c2p(-4, 4), end=grid.c2p(4, -4), color=CS[0], stroke_opacity=0.5)
        line_f1_b = line_f1.copy()
        line_f2 = Line(start=grid.c2p(4, 4), end=grid.c2p(4, 4), color=CS[0], stroke_opacity=1)
        arrows_f = []
        for i in range(-4, 5):
            for j in range(-4, 5):
                if (i+j)%2: continue
                arrows_f.append(Arrow(start=grid.c2p(i,j), end=grid.c2p(i+1,j+1), color=CS[0], stroke_opacity=0.625, stroke_width=2, tip_length=0.1))
                arrows_f[-1].get_tip().set_opacity(0.625)
        circle_g0 = Circle(radius=0, color=CS[1], stroke_opacity=0).move_to(grid.c2p(0,0))
        circle_g1 = Circle(radius=1, color=CS[1], stroke_opacity=0.625).move_to(grid.c2p(0,0))
        arrows_g = []
        import math
        theta = 0
        while theta < 2*PI:
            x, y = math.cos(theta), math.sin(theta)
            arrows_g.append(Arrow(start=grid.c2p(x,y), end=grid.c2p(3*x,3*y), color=CS[1], stroke_width=2, tip_length=0.1))
            theta += PI/8
        circles_s = [
            Circle(radius=0.1, color=CS[-1]).move_to(grid.c2p(math.cos(PI/4),math.sin(PI/4))),
            Circle(radius=0.1, color=CS[-1]).move_to(grid.c2p(math.cos(PI + PI/4),math.sin(PI + PI/4))),
        ]
        # self.play(Create(Text("Constrained Optimization").to_edge(UP+LEFT)))
        # self.play(Create(grid))
        # self.play(Create(tex_f0))
        # self.play(Create(line_f0))
        # self.play(ReplacementTransform(line_f0, line_f1, rate_func=linear))
        # self.play(ReplacementTransform(line_f1, line_f2, rate_func=linear))
        # self.play(Create(tex_f10))
        # self.play(TransformMatchingTex(tex_f10, tex_f11, transform_mismatches=True))
        # self.play(*(Create(arrow) for arrow in arrows_f))
        # self.play(Create(tex_g0))
        # self.play(Create(circle_g0))
        # self.play(ReplacementTransform(circle_g0, circle_g1, rate_func=rate_functions.ease_in_quad))
        # self.play(Create(tex_g10))
        # self.play(TransformMatchingTex(tex_g10, tex_g11, transform_mismatches=True))
        # self.play(*(Create(arrow) for arrow in arrows_g))
        # self.play(Create(tex_s))
        # self.play(Create(line_f0_b))
        # self.play(ReplacementTransform(line_f0_b, line_f1_b, rate_func=linear))
        # self.play(ReplacementTransform(line_f1_b, line_f2, rate_func=linear))
        # self.play(*(Create(circle) for circle in circles_s))
        # self.wait(8)
        # self.play(FadeOut(*self.mobjects))

        # 1. Projection covectors : Derivation from single axis measurement and rotation covector
        grid = NumberPlane(x_range=(-4,4,1)).move_to(RIGHT*3)
        g = Arrow(color=CS[0]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(1, 0))
        r = Arrow(color=CS[1]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(3, 1))
        tex_to_color_map = {
            r"\hat{g}": CS[0],
            r"g_x": CS[0],
            r"g_y": CS[0],
            r"0": CS[0],
            r"1": CS[0],
            r"\vec{r}": CS[1],
            r"r_x": CS[1],
            r"r_y": CS[1],
        }
        texs = [
            MathTex(r"\vec{r} \cdot \hat{g} = \begin{bmatrix} r_x \\ r_y \end{bmatrix} \cdot \begin{bmatrix} 1 \\ 0 \end{bmatrix} = r_x", tex_to_color_map=tex_to_color_map).move_to(LEFT*4),
            MathTex(r"\vec{r} \cdot \hat{g} = \begin{bmatrix} r_x \\ r_y \end{bmatrix} \cdot \begin{bmatrix} g_x \\ g_y \end{bmatrix} = ?", tex_to_color_map=tex_to_color_map).move_to(LEFT*4),
        ]
        self.play(
            Create(grid),
            Create(r),
            Create(g),
            Create(texs[0]),
        )
        self.wait(8) # The projected length of a vector on axis-aligned unit vector is simply the component in that direction.
        self.play(
            ReplacementTransform(texs[0], texs[1]),
            Rotate(g, angle=PI/3, about_point=g.get_start()))
        self.wait(8) # It's not obvious how the projected length for the same vector on a general unit vector can be computed.
        return

        # Overview of QR algorithm
        def qr(A):
            m, n = A.shape
            Q = np.zeros((m, n))
            R = np.zeros((n, n))
            V = A.copy().astype(float)
            for i in range(n):
                R[i, i] = np.linalg.norm(V[:, i])
                Q[:, i] = V[:, i] / R[i, i]
                for j in range(i + 1, n):
                    R[i, j] = np.dot(Q[:, i], V[:, j])
                    V[:, j] -= R[i, j] * Q[:, i]
            return Q, R

        get_arrows = lambda grid, m, q: [
            Arrow(color=CS[0]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(m[0][0], m[1][0])),
            Arrow(color=CS[1]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(m[0][1], m[1][1])),
            Arrow(color=CS[2]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(q[0][0], q[1][0])),
            Arrow(color=CS[3]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(q[0][1], q[1][1])),
        ]

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
        pass

        # Proof of Spectral Theorem
        # - Lagrange multipliers : \nabla xAx optimized over xx=1
        # - Induction via fixed orthogonal plan : px = 0 and Ax = (\lambda)x => (pA)x = 0
        pass

        # SVD
        pass

        # PCA
        pass

        # OLS
        pass

class Determinant(Scene):
   def construct(self):
        Text.set_default(color=LIGHT_GRAY, font_size=24)
        def update_title(title, content):
            updated_title = Text(content).to_edge(UP+LEFT)
            self.play(ReplacementTransform(title, updated_title))
            return updated_title
        title = Text("Introduction").to_edge(UP+LEFT)
        self.play(Create(title))
        line = NumberLine(x_range=(-4, 4, 1)).move_to(RIGHT*3)
        matrix = Matrix([["{{x_0}}"]]).move_to(LEFT*4)
        matrix.get_entries()[0].set_color(CS[0])
        arrow = Arrow(start=line.n2p(0), end=line.n2p(2), buff=0, color=CS[0])
        brace = Brace(arrow, direction=UP, buff=0.2, color=CS[-1])
        self.play(Create(line, run_time=1, lag_ratio=0.1))
        self.play(
            Create(matrix),
            Create(arrow),
        )
        self.wait(8) # The determinant measures the size of some very special n-dimensional shapes formed by n-vectors.
        self.wait(8) # The basic computation can be performed by an efficient vector-reduction algorithm, as well as an elegant closed form.
        self.play(
            matrix.brackets.animate.set_style(fill_opacity=0, stroke_opacity=0),
            matrix[0][0].animate.set_color(CS[-1]),
        )
        self.play(
            matrix.animate.next_to(brace, UP, buff=0),
            FadeIn(brace)
        )
        self.wait(8) # In the 1-dimensional case, the determinant is simply the value representing the length of the single vector.
        self.play(
            FadeOut(line),
            FadeOut(matrix),
            FadeOut(arrow),
            FadeOut(brace),
        )
        title = update_title(title, "1) Reducing Columns")
        get_arrows = lambda arrays: [
            Arrow(color=CS[0], start=grid.c2p(0, 0), end=grid.c2p(*arrays[0].flatten()), buff=0),
            Arrow(color=CS[1], start=grid.c2p(0, 0), end=grid.c2p(*arrays[1].flatten()), buff=0),
        ]
        get_polygon = lambda arrays: Polygon(
            grid.c2p(0, 0),
            grid.c2p(*arrays[0].flatten()),
            grid.c2p(*(arrays[0] + arrays[1]).flatten()),
            grid.c2p(*(arrays[1].flatten())),
            color=BLUE,
            fill_opacity=0.5,
        )
        grid = NumberPlane(x_range=(-4, 4, 1)).move_to(RIGHT*3)
        self.play(Create(grid))
        arrays = [np.array([[1], [0]]), np.array([[0], [2]])]
        polygons = [get_polygon(arrays)]
        arrows = [get_arrows(arrays)]
        diff_arrows = [
            Arrow(color=CS[0], start=grid.c2p(*arrays[1].flatten()), end=grid.c2p(*(arrays[0] + arrays[1]).flatten()), buff=0)]
        arrays = [arrays[0], arrays[0] + arrays[1]]
        polygons.append(get_polygon(arrays))
        arrows.append(get_arrows(arrays))
        diff_arrows.append(
            Arrow(color=CS[1], start=grid.c2p(*arrays[0].flatten()), end=grid.c2p(*(arrays[0] + arrays[1]).flatten()), buff=0))
        arrays = [arrays[0] + arrays[1], arrays[1]]
        polygons.append(get_polygon(arrays))
        arrows.append(get_arrows(arrays))
        polygons.reverse()
        arrows.reverse()
        diff_arrows.reverse()
        matrices = [
            Matrix([["x_0","x_1"],["y_0","y_1"]], element_alignment_corner=ORIGIN, h_buff=2, v_buff=1).move_to(LEFT*4),
            Matrix([[r"x_0 - \frac{y_0}{y_1} x_1","x_1"],["0","y_1"]], element_alignment_corner=ORIGIN, h_buff=2, v_buff=1).move_to(LEFT*4),
            Matrix([[r"x_0 - \frac{y_0}{y_1} x_1","0"],["0","y_1"]], element_alignment_corner=ORIGIN, h_buff=2, v_buff=1).move_to(LEFT*4),
        ]
        secondary_matrices= [
            Matrix([["1","0"],[r"\frac{-y_0}{y_1}","1"]], element_alignment_corner=ORIGIN, h_buff=2, v_buff=1).move_to(LEFT*4 + DOWN*2.4),
            Matrix([["1",r"\frac{-x_1}{x_0 - \frac{y_0}{y_1} x_1}"],["0","1"]], element_alignment_corner=ORIGIN, h_buff=2, v_buff=1).move_to(LEFT*4 + DOWN*2.4),
        ]
        tex = MathTex(r"{{x_0}} {{y_1}} - {{y_0}} {{x_1}}")
        for c in ["x", "y"]:
            for i in range(2):
                tex.set_color_by_tex(f"{c}_{i}", CS[i])
        for (m, matrix) in enumerate(matrices):
            for i in range(4):
                if (m, i) in [(1, 2), (2, 1), (2, 2)]: continue
                matrix.get_entries()[i].set_color(CS[i%2])
        self.play(
            Create(matrices[0]),
            Create(polygons[0]),
            Create(arrows[0][0]),
            Create(arrows[0][1]),
        )
        self.wait(8) # 2D version of this measure is area of the parallelogram.
        self.wait(8) # This value can be computed by aligning the vectors with coordinate axes without changing the covered area.
        self.play(
            Create(diff_arrows[0]),
            Create(secondary_matrices[0]),
        )
        self.wait(8) # This shear transformation slides the area as smoothly connected parallel lines, by subtracting one vector direction from another.
        self.play(
            ReplacementTransform(polygons[0], polygons[1]),
            ReplacementTransform(arrows[0][0], arrows[1][0]),
            ReplacementTransform(arrows[0][1], arrows[1][1]),
            ReplacementTransform(matrices[0], matrices[1]),
            FadeOut(secondary_matrices[0]),
            FadeOut(diff_arrows[0])
        )
        self.wait(8) # Note : the standard row-reduction pushes both vectors in the direction of a coordinate axis by a left-shear-multiplication instead.
        self.play(
            Create(diff_arrows[1]),
            Create(secondary_matrices[1]),
        )
        self.wait(8) # Finally, we can get a rectangle with edge lengths in the diagonal matrix, the determinant will be base times height.
        self.play(
            ReplacementTransform(polygons[1], polygons[2]),
            ReplacementTransform(arrows[1][0], arrows[2][0]),
            ReplacementTransform(arrows[1][1], arrows[2][1]),
            ReplacementTransform(matrices[1], matrices[2]),
            FadeOut(secondary_matrices[1]),
            FadeOut(diff_arrows[1]),
        )
        self.wait(8) # The approach also generalizes efficiently in higher dimensions,
        self.wait(8) # sliding continuous copies of parallel n-1 dimensional slices to align edges of n-dimensional parallelotopes with coordinate axes.
        self.play(
            FadeOut(grid, lag_ratio=0),
            FadeOut(polygons[2]),
            FadeOut(arrows[2][0]),
            FadeOut(arrows[2][1]),
        )
        title = update_title(title, "2.1) Closed form : 2D Computation")
        self.play(TransformMatchingShapes(matrices[2], tex))
        self.wait(8) # The multiplication leads to a really nice 2D closed form, sum of signed products of distinct components.
        self.wait(8) # this makes sense, since picking two components from the same vector or picking the same axis from both vectors will span zero area.
        self.wait(8) # The most interesting bit is that the two products work against each other.
        self.wait(8) # One pair is trying to inflate the 2D balloon normally, while the second pair is trying to push its skin inside-out.
        self.play(FadeOut(tex))
        title = update_title(title, "2.2) Closed form : Generalizing Permutation sign")
        matrices = [
            Matrix([["w_0","w_1","0","0"],["x_0","x_1","0","0"],["0","0","y_2","0"],["0","0","0","z_3"]], left_bracket="|", right_bracket="|").move_to(LEFT*2),
            Matrix([["w_0","0","0","0"],["0","x_1","x_2","0"],["0","y_1","y_2","0"],["0","0","0","z_3"]], left_bracket="|", right_bracket="|").move_to(LEFT*2),
        ]
        texs = [
            [
                MathTex("= ( {{w_0}} {{x_1}} - {{x_0}} {{w_1}} ) {{y_2}} {{z_3}}"),
                MathTex("= {{w_0}} {{x_1}} {{y_2}} {{z_3}} - {{x_0}} {{w_1}} {{y_2}} {{z_3}}"),
            ],
            [
                MathTex("= {{w_0}} ( {{x_1}} {{y_2}} - {{y_1}} {{x_2}} ) {{z_3}}"),
                MathTex("= {{w_0}} {{x_1}} {{y_2}} {{z_3}} - {{w_0}} {{y_1}} {{x_2}} {{z_3}}"),
            ]
        ]
        for matrix in matrices:
            for entry in matrix.get_entries():
                for c in ["w","x", "y", "z"]:
                    for i in range(4):
                        entry.set_color_by_tex(f"{c}_{i}", CS[i])
        for tex in texs[0] + texs[1]:
            tex.next_to(matrices[0], RIGHT)
            for c in ["w","x", "y", "z"]:
                for i in range(4):
                    tex.set_color_by_tex(f"{c}_{i}", CS[i])
        self.play(Create(matrices[0]))
        self.play(Create(texs[0][0]))
        self.wait(8) # Focusing on 4 4D vectors in this nearly diagonal matrix, yz can simply be thought of as uniform weight per unit area.
        self.play(FadeOut(texs[0][0]))
        self.play(Create(texs[0][1]))
        self.wait(8) # wxyz and xwyz work against earch other, as in the 2D formula.
        self.play(
            FadeOut(matrices[0]),
            FadeOut(texs[0][1]),
        )
        self.play(Create(matrices[1]))
        self.play(Create(texs[1][0]))
        self.wait(8) # wxyz and wyxz work against each other in this second case.
        self.play(FadeOut(texs[1][0]))
        self.play(Create(texs[1][1]))
        self.wait(8) # The sign flips similarly generalize to any component pair swaps in any number of dimensions.
        self.play(
            FadeOut(matrices[1]),
            FadeOut(texs[1][1]),
        )
        title = update_title(title, "2.3) Closed form : Deriving Permutations")
        grid = NumberPlane(x_range=(-2, 6, 1), y_range=(-2, 6, 1)).move_to(RIGHT*3)
        self.play(Create(grid))
        tex = MathTex(
            r'''
            &| {{v_x}} + {{v_y}} \ \ {{w}} | \\
            = &| {{v_x}} \ \ {{w}} | + | {{v_y}} \ \ {{w}} |
            '''
        ).move_to(LEFT*4)
        tex.set_color_by_tex("v_x", CS[0])
        tex.set_color_by_tex("v_y", CS[0])
        tex.set_color_by_tex("w", CS[1])
        arrows = [
            Arrow(color=CS[1]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(-1, 2)),
            Arrow(color=CS[0]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(3, 3)),
            Arrow(color=CS[0]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(3, 0)),
            Arrow(color=CS[0]).put_start_and_end_on(grid.c2p(3, 0), grid.c2p(3, 3)),
            Arrow(color=CS[1]).put_start_and_end_on(grid.c2p(3, 0), grid.c2p(2, 2)),
        ]
        polygons = [
            Polygon(
                grid.c2p(0, 0),
                grid.c2p(2, 2),
                grid.c2p(3, 3),
                grid.c2p(2, 5),
                grid.c2p(1, 4),
                grid.c2p(-1, 2),
                color=BLUE,
                fill_opacity=0.5,
            ),
            Polygon(
                grid.c2p(0, 0),
                grid.c2p(3, 0),
                grid.c2p(3, 3),
                grid.c2p(2, 5),
                grid.c2p(2, 2),
                grid.c2p(-1, 2),
                color=BLUE,
                fill_opacity=0.5,
            ),
        ]
        self.play(
            Create(tex),
            Create(polygons[0]),
            Create(arrows[0]),
            Create(arrows[1]),
        )
        self.wait(8) # To get all the permutations, we can split the terms aligned with components of any of the vectors as shown.
        self.play(FadeOut(arrows[1]))
        self.play(Create(arrows[2]))
        self.play(Create(arrows[3]))
        self.play(Create(arrows[4]))
        self.play(ReplacementTransform(polygons[0], polygons[1]))
        self.wait(8) # Using this property, the determinant can be expanded level-by-level while clearing rows one-by-one.
        self.play(
            FadeOut(grid),
            FadeOut(tex),
            FadeOut(arrows[0]),
            FadeOut(arrows[2]),
            FadeOut(arrows[3]),
            FadeOut(arrows[4]),
            FadeOut(polygons[1]),
        )
        self.play(title.animate.to_edge(UP+RIGHT))
        from copy import deepcopy
        base_array = [[f"{j}_{i}" for i in range(4)] for j in ["w","x","y","z"]]
        matrice_groups = [[Matrix(base_array, left_bracket="|", right_bracket="|")],[],[],[]]
        matrice_groups_final = [[Matrix(base_array, left_bracket="|", right_bracket="|")],[],[],[]]
        for k in range(3):
            for i in range(k, 4):
                array = deepcopy(base_array)
                for j in set(range(k, 4)) - {i}:
                    array[j][k] = "0"
                matrice_groups[k+1].append(Matrix(array, left_bracket="|", right_bracket="|"))
                for j in range(k+1,4):
                    array[i][j] = "0"
                matrice_groups_final[k+1].append(Matrix(array, left_bracket="|", right_bracket="|"))
                if i == k: new_base_array = deepcopy(array)
            base_array = new_base_array
        for matrices in matrice_groups + matrice_groups_final:
            for matrix in matrices:
                for entry in matrix.get_entries():
                    for c in ["w","x", "y", "z"]:
                        for i in range(4):
                            entry.set_color_by_tex(f"{c}_{i}", CS[i])
        for (i, matrices) in enumerate(matrice_groups):
            rects = []
            for (j, matrix) in enumerate(matrices):
                matrix_final = matrice_groups_final[i][j]
                for m in [matrix, matrix_final]:
                    m.scale(0.5)
                    m.shift(3*UP + i*2*DOWN + 4*LEFT + j*3*RIGHT)
                if i:
                    if not j:
                        arrow = Arrow(start=matrice_groups[i-1][0].get_bottom(), end=matrix.get_top())
                        arrow.set_stroke(width=1)
                        arrow.tip.scale(0.5)
                        self.play(Create(arrow))
                    else:
                        tex = MathTex("+")
                        tex.scale(0.5)
                        tex.next_to(matrices[j-1], RIGHT)
                        self.play(Create(tex))
                        for m in [matrix, matrix_final]:
                            m.next_to(tex, RIGHT)
                self.play(Create(matrix))
                if i:
                    rects.append(SurroundingRectangle(VGroup(*matrix.get_rows()[j+i-1][i-1:]), color=BLUE))
                    self.play(Create(rects[-1]))
            if i:
                for (j, (matrix, matrix_final)) in enumerate(zip(matrices, matrice_groups_final[i])):
                    self.play(
                        ReplacementTransform(matrix, matrix_final),
                        FadeOut(rects[j]),
                    )
        tex = MathTex("= {{w_0}} {{x_1}} {{y_2}} {{z_3}} - {{w_0}} {{x_1}} {{z_2}} {{y_3}}")
        for c in ["w","x", "y", "z"]:
            for i in range(4):
                tex.set_color_by_tex(f"{c}_{i}", CS[i])
        tex.scale(0.5)
        tex.next_to(matrix_final, RIGHT)
        self.play(Create(tex))
        self.wait(8) # Fully expanding the recursive tree structure leads to all permutation, with the orientation defined by the swap-distance from identity permutation.
        self.play(FadeOut(*self.mobjects))
        tex = MathTex(r"\sum_{\sigma \in S_n} sgn(\sigma) \prod_{i=1}^n a_{\sigma(i)i}")
        self.play(Create(tex))
        self.wait(8) # Finally, the entire computation can be represented compactly as a sum of products of signed permutations!
        self.play(FadeOut(tex))
