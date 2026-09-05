# docker run -it --rm -v "$(pwd)":/manim manimcommunity/manim manim linear_algebraic_computations.py

import math
import numpy as np
from manim import *

CS = [GREEN,RED,YELLOW,TEAL]

class Projection(Scene):
   def construct(self):
        Text.set_default(font_size=24)
        MathTex.set_default(font_size=42)
        '''
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
            self.play(Create(node_text), *(Create(arrow) for arrow in arrows))
        self.play(FadeOut(*self.mobjects))
        '''

        '''
        # TODO: Defining circles via right triangles
        title = Text("Rotation Matrix").to_edge(UP+LEFT)
        self.play(Create(title))
        grid = Axes(x_range=[-4, 4, 1], y_range=[-4, 4, 1], x_length=8, y_length=8).move_to(RIGHT*3)
        unit_circle = Circle(radius=1, color=LIGHT_GRAY).move_to(grid.c2p(0, 0))
        self.play(Create(grid), Create(unit_circle))
        i_arrow = Arrow(start=grid.c2p(0, 0), end=grid.c2p(1, 0), color=CS[0], buff=0)
        j_arrow = Arrow(start=grid.c2p(0, 0), end=grid.c2p(0, 1), color=CS[1], buff=0)
        ij_angle = RightAngle(i_arrow, j_arrow, length=0.2, color=LIGHT_GRAY)
        v_tex = Matrix([["v_g"],["v_r"]]).move_to(LEFT*4)
        v_tex.set_column_colors(CS[2])
        v_arrow = Arrow(start=grid.c2p(0, 0), end=grid.c2p(2, 1), color=CS[2], buff=0)
        r_tex = Matrix([["g_x","r_x"],["g_y","r_y"]])
        r_tex.set_column_colors(*CS)
        self.play(Create(i_arrow), Create(j_arrow), Create(ij_angle))
        self.play(Create(v_tex), Create(v_arrow))
        self.play(v_tex.animate.move_to(LEFT*3))
        r_tex.next_to(v_tex, LEFT)
        self.play(
            Create(r_tex),
            *(Rotate(obj, PI/4, about_point=grid.c2p(0, 0)) for obj in [i_arrow, j_arrow, ij_angle, v_arrow]),
        )
        v_tex_1 = MathTex("v_r").move_to(LEFT*2)
        v_tex_1.set_color(CS[2])
        r_tex_1 = Matrix([["r_x"],["r_y"]]).next_to(v_tex_1, LEFT)
        r_tex_1.set_column_colors(CS[1])
        p_tex = MathTex("+").next_to(r_tex_1, LEFT)
        v_tex_0 = MathTex("v_g").next_to(p_tex, LEFT)
        v_tex_0.set_color(CS[2])
        r_tex_0 = Matrix([["g_x"],["g_y"]]).next_to(v_tex_0, LEFT)
        r_tex_0.set_column_colors(CS[0])
        self.play(
            FadeOut(r_tex.get_brackets()),
            FadeOut(v_tex.get_brackets())
        )
        self.play(
            ReplacementTransform(r_tex.get_columns()[0], r_tex_0.get_columns()[0]),
            ReplacementTransform(r_tex.get_columns()[1], r_tex_1.get_columns()[0]),
            ReplacementTransform(v_tex.get_rows()[0], v_tex_0),
            ReplacementTransform(v_tex.get_rows()[1], v_tex_1),
            Create(p_tex),
        )
        self.play(
            FadeIn(r_tex_0.get_brackets()),
            FadeIn(r_tex_1.get_brackets()),
        )
        v_tex_0_c = v_tex_0.copy()
        v_tex_1_c = v_tex_1.copy()
        p_tex_c = p_tex.copy()
        self.play(
            FadeOut(r_tex_0.get_brackets()),
            FadeOut(r_tex_1.get_brackets()),
        )
        self.play(
            v_tex_0.animate.next_to(r_tex_0.get_entries()[0], RIGHT),
            v_tex_0_c.animate.next_to(r_tex_0.get_entries()[1], RIGHT),
            v_tex_1.animate.next_to(r_tex_1.get_entries()[0], RIGHT),
            v_tex_1_c.animate.next_to(r_tex_1.get_entries()[1], RIGHT),
            p_tex.animate.next_to(r_tex_1.get_entries()[0], LEFT),
            p_tex_c.animate.next_to(r_tex_1.get_entries()[1], LEFT),
        )
        self.play(
            p_tex.animate.next_to(v_tex_0, RIGHT),
            p_tex_c.animate.next_to(v_tex_0_c, RIGHT),
            r_tex_1.get_entries()[0].animate.next_to(p_tex.target, RIGHT),
            r_tex_1.get_entries()[1].animate.next_to(p_tex_c.target, RIGHT),
            v_tex_1.animate.next_to(r_tex_1.get_entries()[0].target, RIGHT),
            v_tex_1_c.animate.next_to(r_tex_1.get_entries()[1].target, RIGHT),
        )
        r_tex_1.get_brackets()[1].set_x(v_tex_1.get_right()[0] + MED_SMALL_BUFF)
        self.play(
            FadeIn(r_tex_0.get_brackets()[0]),
            FadeIn(r_tex_1.get_brackets()[1]),
        )
        brace = BraceBetweenPoints(
            np.array([v_arrow.get_start()[0], v_arrow.get_end()[1], 0]),
            np.array([v_arrow.get_end()[0], v_arrow.get_end()[1], 0]),
            direction=UP,
            buff=0,
        )
        self.play(
            FadeIn(brace),
            FadeOut(r_tex_0.get_brackets()[0]),
            FadeOut(r_tex_1.get_brackets()[1]),
            FadeOut(r_tex_0.get_entries()[1]),
            FadeOut(r_tex_1.get_entries()[1]),
            FadeOut(p_tex_c),
            FadeOut(v_tex_0_c),
            FadeOut(v_tex_1_c),
        )
        v_tex = Matrix([["v_g"],["v_r"]]).move_to(LEFT*4)
        v_tex.set_column_colors(CS[2])
        r_tex = Matrix([["g_x","r_x"]], h_buff=0.9)
        r_tex.set_column_colors(*CS)
        p_tex = MathTex("=")
        p_tex.set_x(r_tex_0.get_entries()[0].get_x() - 0.9)
        p_tex.set_y(r_tex_0.get_entries()[0].get_y() - LARGE_BUFF)
        r_tex.next_to(p_tex, RIGHT)
        v_tex.next_to(r_tex, RIGHT, aligned_edge=UP)
        self.play(
            Create(p_tex),
            Create(r_tex),
            Create(v_tex),
        )
        self.play(
            FadeOut(*[mob for mob in self.mobjects if mob not in [grid, title, i_arrow, j_arrow, ij_angle, v_arrow, unit_circle]]),
            *(Rotate(obj, -PI/4, about_point=grid.c2p(0, 0)) for obj in [i_arrow, j_arrow, ij_angle, v_arrow]),
        )
        matrix_180 = Matrix([[-1, 0],[0,-1]]).move_to(LEFT*4)
        matrix_180.set_column_colors(*CS)
        tex_180 = MathTex(r"x \rightarrow -x,\ y \rightarrow -y").next_to(matrix_180, UP)
        self.play(
            Create(matrix_180),
            Create(tex_180),
        )
        self.play(*(Rotate(obj, PI, about_point=grid.c2p(0, 0), axis=UP) for obj in [i_arrow, j_arrow, ij_angle, v_arrow]))
        self.play(*(Rotate(obj, PI, about_point=grid.c2p(0, 0), axis=RIGHT) for obj in [i_arrow, j_arrow, ij_angle, v_arrow]))
        self.play(*(Rotate(obj, -PI, about_point=grid.c2p(0, 0)) for obj in [i_arrow, j_arrow, ij_angle, v_arrow]))
        matrix_90 = Matrix([[0, -1],[1, 0]]).move_to(LEFT*4)
        matrix_90.set_column_colors(*CS)
        tex_90 = MathTex(r"x \leftrightarrow y,\ y \rightarrow -y").next_to(matrix_90, UP)
        self.play(
            FadeOut(matrix_180),
            FadeOut(tex_180),
        )
        self.play(
            Create(matrix_90),
            Create(tex_90),
        )
        self.play(*(Rotate(obj, PI, about_point=grid.c2p(0, 0), axis=UP+RIGHT) for obj in [i_arrow, j_arrow, ij_angle, v_arrow]))
        self.play(*(Rotate(obj, PI, about_point=grid.c2p(0, 0), axis=UP) for obj in [i_arrow, j_arrow, ij_angle, v_arrow]))
        self.play(*(Rotate(obj, -PI/2, about_point=grid.c2p(0, 0)) for obj in [i_arrow, j_arrow, ij_angle, v_arrow]))
        self.play(FadeOut(*self.mobjects))
        '''

        # '''
        # self.play(Create(Text("Projection Vector").to_edge(UP+LEFT)))
        grid = Axes(x_range=[-4, 4, 1], y_range=[-4, 4, 1], x_length=8, y_length=8).move_to(RIGHT*3)
        unit_circle = Circle(radius=1, color=LIGHT_GRAY).move_to(grid.c2p(0, 0))
        self.play(Create(grid), Create(unit_circle))
        color_1, color_0, color_c = CS[0:3]
        theta = PI/3
        x, y = math.cos(theta), math.sin(theta)
        x_line = DashedLine(start=grid.c2p(x, y - 0.1), end=grid.c2p(x, -1), color=color_c)
        y_line = DashedLine(start=grid.c2p(x + 0.1, y), end=grid.c2p(2, y), color=color_c)
        x_brace = BraceBetweenPoints(grid.c2p(0, -1), grid.c2p(x, -1), direction=DOWN, buff=0, color=color_c)
        y_brace = BraceBetweenPoints(grid.c2p(2, 0), grid.c2p(2, y), direction=RIGHT, buff=0, color=color_c)
        x_tex = MathTex("x", color=color_c, font_size=32).next_to(x_brace, 0.5 * DOWN)
        y_tex = MathTex("y", color=color_c, font_size=32).next_to(y_brace, 0.5 * RIGHT)
        covector = Matrix([["x", "y"]]).move_to(LEFT*5)
        covector.set_column_colors(color_c, color_c)
        circle_c = Circle(radius=0.1, color=color_c).move_to(grid.c2p(x, y))
        self.play(
            Create(covector),
            Create(x_line),
            Create(y_line),
            Create(x_brace),
            Create(y_brace),
            Create(x_tex),
            Create(y_tex),
            Create(circle_c),
        )
        arrow_1 = Arrow(color=color_1, start=grid.c2p(0, 0), end=grid.c2p(x, y), buff=0)
        vector_1 = Matrix([["x"], ["y"]]).next_to(covector)
        vector_1.set_column_colors(color_1)
        tex_1 = MathTex("1", color=color_1).next_to(arrow_1.get_end(), UP)
        tex_1_l = MathTex("= 1", color=color_1).next_to(vector_1, RIGHT)
        self.play(
            Create(vector_1),
            Create(tex_1_l),
            Create(arrow_1),
            Create(tex_1),
        )
        arrow_0 = Arrow(color=color_0, start=grid.c2p(0, 0), end=grid.c2p(-y, x), buff=0)
        angle_01 = RightAngle(arrow_0, arrow_1, length=0.25, color=LIGHT_GRAY)
        vector_0 = Matrix([["-y"], ["x"]]).next_to(covector)
        vector_0.set_column_colors(color_0)
        tex_0 = MathTex("0", color=color_0).next_to(arrow_0.get_end(), LEFT)
        tex_0_l = MathTex("= 0", color=color_0).next_to(vector_0, RIGHT)
        self.play(
            FadeOut(vector_1),
            FadeOut(tex_1_l),
        )
        self.play(
            Create(vector_0),
            Create(tex_0_l),
            Create(arrow_0),
            Create(angle_01),
            Create(tex_0),
        )
        line_c = Line(color=color_c, start=grid.c2p(1, -8), end=grid.c2p(1, 8)).rotate(theta, about_point=grid.c2p(0, 0))
        angle_1c = RightAngle(arrow_1, line_c, length=0.25, quadrant=(-1,1), color=LIGHT_GRAY)
        vector_01 = Matrix([["x - cy"], ["y + cx"]]).next_to(covector)
        vector_01.get_entries()[0][0][0:2].set_color(color_1)
        vector_01.get_entries()[0][0][2:].set_color(color_0)
        vector_01.get_entries()[1][0][0:2].set_color(color_1)
        vector_01.get_entries()[1][0][2:].set_color(color_0)
        vector_01.get_brackets().set_color(CS[-1])
        self.play(
            FadeOut(vector_0),
            FadeOut(tex_0_l),
        )
        tex_1_l.next_to(vector_01, DOWN)
        tex_1_l.set_color(CS[-1])
        self.play(
            Create(vector_01),
            Create(line_c),
            Create(angle_1c),
            FadeIn(tex_1_l),
        )
        self.play(
            tex_1.animate.set_color(CS[-1]),
            arrow_1.animate.set_color(CS[-1]),
            FadeOut(angle_01),
            FadeOut(angle_1c),
        )
        ax, ay = x, y
        for diff in [(-4*y, 4*x), (8*y, -8*x), (-4*y, 4*x)]:
            ax, ay = ax + diff[0], ay + diff[1]
            self.play(
                arrow_1.animate.put_start_and_end_on(grid.c2p(0, 0), grid.c2p(ax, ay)),
                tex_1.animate.next_to(arrow_1.target.get_end(), UP),
        )
        self.play(
            FadeOut(vector_01),
            FadeOut(arrow_0),
            FadeOut(arrow_1),
            FadeOut(tex_0),
            FadeOut(tex_1),
            FadeOut(tex_1_l),
            FadeOut(x_line),
            FadeOut(y_line),
            FadeOut(x_brace),
            FadeOut(y_brace),
            FadeOut(x_tex),
            FadeOut(y_tex),
        )
        self.play(covector.animate.move_to(LEFT*4))
        for diff in [(1, 0), (0, -0.5), (-1, 0), (0, 0.5)]:
            x += diff[0]
            y += diff[1]
            new_circle_c = circle_c.copy().move_to(grid.c2p(x, y))
            new_line_c = Line(color=color_c, start=grid.c2p(-8*x, -8*y), end=grid.c2p(8*x, 8*y))
            new_line_c.rotate(PI/2, about_point=grid.c2p(x / (x*x + y*y), y / (x*x + y*y)))
            self.play(
                ReplacementTransform(circle_c, new_circle_c),
                ReplacementTransform(line_c, new_line_c),
            )
            circle_c = new_circle_c
            line_c = new_line_c
        self.play(FadeOut(*self.mobjects))
        covector_4 = Matrix([["w_c","x_c","y_c","z_c"]])
        covector_4.get_entries()[:].set_color(CS[2])
        vector_4 = Matrix([["w"],["x"],["y"],["z"]]).next_to(covector_4, RIGHT)
        vector_4.get_entries()[:].set_color(CS[-1])
        self.play(Create(covector_4))
        self.play(Create(vector_4))
        tex_p = MathTex("+")
        vector_4_l = Matrix([["w"],["x"],[0],[0]])
        vector_4_l.get_entries()[:2].set_color(CS[-1])
        vector_4_l.next_to(tex_p, LEFT)
        covector_4_l = covector_4.copy().next_to(vector_4_l, LEFT)
        covector_4_r = covector_4.copy().next_to(tex_p, RIGHT)
        vector_4_r = Matrix([[0],[0],["y"],["z"]])
        vector_4_r.get_entries()[2:].set_color(CS[-1])
        vector_4_r.next_to(covector_4_r, RIGHT)
        self.play(
            Create(tex_p),
            ReplacementTransform(vector_4, vector_4_l),
            ReplacementTransform(vector_4.copy(), vector_4_r),
            ReplacementTransform(covector_4, covector_4_l),
            ReplacementTransform(covector_4.copy(), covector_4_r),
        )
        covector_4_l_f = Matrix([["w_c","x_c",0,0]]).next_to(vector_4_l, LEFT)
        covector_4_l_f.get_entries()[:2].set_color(CS[2])
        covector_4_r_f = Matrix([[0,0,"y_c","z_c"]]).next_to(vector_4_r, LEFT)
        covector_4_r_f.get_entries()[2:].set_color(CS[2])
        self.play(
            ReplacementTransform(covector_4_l, covector_4_l_f),
            ReplacementTransform(covector_4_r, covector_4_r_f),
        )
        self.play(FadeOut(*self.mobjects))
        vector_4 = Matrix([["w"],["x"],["y"],["z"]])
        vector_4.get_entries()[:].set_color(CS[-1])
        covector_4 = Matrix([["w_c","x_c","y_c","z_c"]]).next_to(vector_4, LEFT)
        covector_4.get_entries()[:].set_color(CS[2])
        tex = MathTex(r"= {{w_c}} {{w}} + {{x_c}} {{x}} + {{y_c}} {{y}} + {{z_c}} {{z}}").next_to(vector_4, RIGHT)
        for c in ["w","x","y","z"]:
            tex.set_color_by_tex(f"{c}_c", CS[2])
            tex.set_color_by_tex(c, CS[-1])
        self.play(Create(covector_4))
        self.play(Create(vector_4))
        self.play(Create(tex))
        self.play(FadeOut(*self.mobjects))
        # TODO: vector projection formula
        # '''

        '''
        self.play(Create(Text("Rotation Transpose").to_edge(UP+LEFT)))
        # TODO: transpose based inverse
        unit_circle = Circle(radius=1, color=CS[-1]).move_to(grid.c2p(0, 0))
        self.play(Create(unit_circle))
        g_arrow = Arrow(color=CS[0]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(1, 0))
        g_matrix = Matrix([["1"], ["0"]]).move_to(LEFT*4)
        g_matrix_rotated = Matrix([["g_x"], ["g_y"]]).move_to(LEFT*4)
        g_matrix.set_column_colors(CS[0])
        g_matrix_rotated.set_column_colors(CS[0])
        dot = MathTex(r"\cdot").next_to(g_matrix, LEFT)
        v_arrow = Arrow(color=CS[2]).put_start_and_end_on(grid.c2p(0, 0), grid.c2p(3, 1))
        v_matrix = Matrix([["v_x"], ["v_y"]]).next_to(dot, LEFT)
        v_matrix.set_column_colors(CS[2])
        v_dots = DashedLine(color=CS[2]).put_start_and_end_on(v_arrow.get_end(), [v_arrow.get_end()[0], 0, 0])
        v_brace = BraceBetweenPoints(
            np.array([v_arrow.get_start()[0], v_arrow.get_end()[1], 0]),
            np.array([v_arrow.get_end()[0], v_arrow.get_end()[1], 0]),
            direction=UP,
            buff=0,
            color=CS[2]
        )
        equals = MathTex(r"=").next_to(g_matrix, RIGHT)
        result = MathTex(r"v_x").next_to(equals, RIGHT)
        question = MathTex(r"?").next_to(equals, RIGHT)
        self.play(
            Create(g_arrow),
            Create(v_arrow),
        )
        self.play(Create(v_matrix))
        self.play(Create(dot))
        self.play(Create(g_matrix))
        self.play(Create(equals))
        self.play(
            Create(result),
            FadeIn(v_brace),
        )
        self.play(
            FadeOut(v_brace),
            FadeOut(result),
        )
        self.play(
            Rotate(g_arrow, angle=PI/3, about_point=g_arrow.get_start()),
            ReplacementTransform(g_matrix, g_matrix_rotated),
            dot.animate.next_to(g_matrix_rotated, LEFT),
            v_matrix.animate.next_to(dot.target, LEFT),
            equals.animate.next_to(g_matrix_rotated, RIGHT),
            question.animate.next_to(equals.target, RIGHT),
        )
        rotation_matrix_1 = MathTex(r"R").next_to(dot, RIGHT)
        rotation_matrix_0 = MathTex(r"R").next_to(v_matrix, LEFT)
        self.play(
            g_matrix_rotated.animate.next_to(rotation_matrix_1, RIGHT),
            equals.animate.next_to(g_matrix_rotated.target, RIGHT),
            question.animate.next_to(equals.target, RIGHT),
        )
        self.play(
            Create(rotation_matrix_0),
            Create(rotation_matrix_1),
            Rotate(g_arrow, angle=-PI/3, about_point=g_arrow.get_start()),
            Rotate(v_arrow, angle=-PI/3, about_point=v_arrow.get_start()),
        )
        self.play(FadeOut(*self.mobjects))
        '''

        '''
        self.play(Create(Text("Spectral Theorem").to_edge(UP+LEFT)))
        - Lagrange multipliers : \nabla xAx optimized over xx=1
        - Induction via fixed orthogonal plan : px = 0 and Ax = (\lambda)x => (pA)x = 0
        self.play(FadeOut(*self.mobjects))
        '''

        '''
        self.play(Create(Text("Eigenvector Computation").to_edge(UP+LEFT)))
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
        for faster convergence, we can follow a method similar to exponentiation by squaring
        A_0 = Q_0 R_0 -> E_0 = Q_0
        A_1 = Q_0 R_0 Q_0 R_0 = Q_0 Q_1 R_1 Q_0 -> E_1 = Q_01
        A_2 = Q_01 R_01 Q_01 R_01 = Q_01 Q_2 R_2 R_01 -> E_2 = Q_02
        self.play(FadeOut(*self.mobjects))
        '''


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
