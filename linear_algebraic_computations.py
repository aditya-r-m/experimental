# docker run -it --rm -v "$(pwd)":/manim manimcommunity/manim manim linear_algebraic_computations.py

import math
import numpy as np
from manim import *

CS = [GREEN,RED,YELLOW,TEAL]
Z = np.array([0., 0., 0.,])

class Projection(Scene):
    def play_introduction(self):
        circle = Circle(radius=1, color=LIGHT_GRAY)
        counter_shear = [[1, 0.5],[0.5, 1]]
        g_arrow = Arrow(start=(0, 0, 0), end=(1, 0, 0), color=CS[0], buff=0)
        r_arrow = Arrow(start=(0, 0, 0), end=(0, 1, 0), color=CS[1], buff=0)
        g_arrow_counter_sheared = Arrow(start=(0, 0, 0), end=(counter_shear[0][0], counter_shear[1][0], 0), color=CS[0], buff=0)
        r_arrow_counter_sheared = Arrow(start=(0, 0, 0), end=(counter_shear[0][1], counter_shear[1][1], 0), color=CS[1], buff=0)
        lines = []
        lines_counter_sheared = []
        for t in range(32):
            theta = 2*PI*t/32
            x, y = 4*math.cos(theta), 4*math.sin(theta)
            c = (abs(x)*CS[0] + abs(y)*CS[1])/(abs(x)+abs(y))
            lines.append(Line(start=(0, 0, 0), end=(x, y, 0), color=c, buff=0, stroke_opacity=0.5))
            x, y = counter_shear[0][0]*x + counter_shear[0][1]*y, counter_shear[1][0]*x + counter_shear[1][1]*y
            lines_counter_sheared.append(Line(start=(0, 0, 0), end=(x, y, 0), color=c, buff=0, stroke_opacity=0.5))
        arrows_counter_sheared = []
        for t in range(32):
            theta = 2*PI*t/32
            x, y = math.cos(theta), math.sin(theta)
            c = (abs(x)*CS[0] + abs(y)*CS[1])/(abs(x)+abs(y))
            x_u, y_u = counter_shear[0][0]*x + counter_shear[0][1]*y, counter_shear[1][0]*x + counter_shear[1][1]*y
            arrows_counter_sheared.append(Arrow(start=(x, y, 0), end=(x_u, y_u, 0), color=c, buff=0))
        self.play(Create(circle))
        self.play(
            GrowArrow(g_arrow),
            GrowArrow(r_arrow),
            *(Create(line) for (line) in lines),
        )
        self.play(
            ReplacementTransform(g_arrow, g_arrow_counter_sheared),
            ReplacementTransform(r_arrow, r_arrow_counter_sheared),
            *(ReplacementTransform(line, line_counter_sheared) for (line, line_counter_sheared) in zip(lines, lines_counter_sheared)),
            *(GrowArrow(arrow_counter_sheared) for arrow_counter_sheared in arrows_counter_sheared),
        )
        _, eigen_vectors = np.linalg.eig(np.array(counter_shear))
        self.play(
            FadeOut(g_arrow_counter_sheared),
            FadeOut(r_arrow_counter_sheared),
            *(FadeOut(line_counter_sheared) for line_counter_sheared in lines_counter_sheared),
            *(Rotate(arrow_counter_sheared, -math.atan2(eigen_vectors[1][0], eigen_vectors[0][0]), about_point=(0, 0, 0)) for arrow_counter_sheared in arrows_counter_sheared),
        )
        self.play(FadeOut(*(obj for obj in self.mobjects)))

    def get_titles(self):
        title_texts = [
            "Rotation Matrix",
            "Projection Covector",
            "Rotation Inverse",
            "Spectral Theorem",
            "Eigenvector Computation\n     (QR Iteration)",
            "Singular Value Decomposition",
            "      Dimension Reduction\n(Principal Component Analysis)",
            "Projection Matrix",
            "    Linear Regression\n(Ordinary Least Squares)",
        ]
        title_texts = list(map(lambda t: Text(t, color=WHITE, font="Noto Mono", font_size=16), title_texts))
        layout = [
            np.array([-5,3,0]),
            np.array([5,3,0]),
            np.array([-5,1,0]),
            np.array([-5,-1,0]),
            np.array([-5,-3,0]),
            np.array([0,-1,0]),
            np.array([0,-3,0]),
            np.array([5,-1,0]),
            np.array([5,-3,0]),
        ]
        edges = [
            [],
            [0],
            [0,1],
            [2,1],
            [3],
            [3,1],
            [5],
            [5,1],
            [7],
        ]
        arrows = []
        for (i, title_text) in enumerate(title_texts):
            title_text.move_to(layout[i])
            for u in edges[i]:
                src, dst = title_texts[u], title_text
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
        return title_texts, arrows

    def get_arrow(self, start, end, color):
        return Arrow(start=self.axes.c2p(start), end=self.axes.c2p(end), color=color, buff=0)

    def get_line(self, start, end, color, stroke_opacity=1):
        return Line(color=color, start=self.axes.c2p(*start), end=self.axes.c2p(*end), stroke_opacity=stroke_opacity)

    def get_dashed_line(self, start, end, color):
        return DashedLine(color=color, start=self.axes.c2p(*start), end=self.axes.c2p(*end))

    def get_polygon(self, *points, color, fill_color, fill_opacity):
        return Polygon(*(self.axes.c2p(*point) for point in points), color=color, fill_color=fill_color, fill_opacity=fill_opacity)

    def get_brace_between_points(self, start, end, color, direction):
        return BraceBetweenPoints(self.axes.c2p(*start), self.axes.c2p(*end), color=color, direction=direction, buff=0)

    def get_circle(self, center, radius, color):
        return Circle(radius=radius, color=color).move_to(self.axes.c2p(*center))

    def get_lircle(self, center, color, radius=0.1, length_scale=8):
        circle = self.get_circle(center, 0.1, color)
        line = self.get_line(
            (-length_scale*center[0], -length_scale*center[1]),
            (length_scale*center[0], length_scale*center[1]),
            color)
        line.rotate(PI/2, about_point=self.axes.c2p(
            center[0] / (center[0]**2 + center[1]**2),
            center[1] / (center[0]**2 + center[1]**2)))
        return line, circle

    def get_elliptic_contours(self, width, height, color):
        group = VGroup()
        group.add(Ellipse(
            width=2*width,
            height=2*height,
            color=color).move_to(self.origin))
        for (dx, dy) in [(0,1),(1,0),(-1,0),(0,-1)]:
            group.add(Line(
                color=color,
                start=self.axes.c2p(width*dx, height*dy),
                end=self.axes.c2p((width+0.25)*dx, (height+0.25)*dy)))
        return group

    def play_rotation_matrix(self, title):
        self.play(Create(self.axes), Create(self.unit_circle))
        lines = [
            self.get_line((0, 0), (3/5, 4/5), LIGHT_GRAY),
            self.get_line((3/5, 4/5), (3/5, 0), LIGHT_GRAY),
        ]
        self.play(Create(lines[0]))
        self.play(Create(lines[1]))
        texs = [
            MathTex(r"{{A_x}} + {{A_y}} = {{A_1}}").move_to(LEFT*4),
            MathTex(r"{{c x^2}} + {{c y^2}} = {{c 1^2}}").move_to(LEFT*4),
        ]
        triangles = [
            self.get_polygon(
                (0, 0), (3/5 * 3/5 * 3/5, 3/5 * 4/5 * 3/5), (3/5, 0), color=CS[0], fill_color=CS[0], fill_opacity=0.5),
            self.get_polygon(
                (3/5, 0), (3/5 * 3/5 * 3/5, 3/5 * 4/5 * 3/5), (3/5, 4/5), color=CS[1], fill_color=CS[1], fill_opacity=0.5),
            self.get_polygon(
                (0, 0), (3/5, 0), (3/5, 4/5), color=CS[2], fill_color=CS[2], fill_opacity=0.5),
        ]
        braces = [
            self.get_brace_between_points((0, 0), (3/5, 0), direction=DOWN, color=CS[0]),
            self.get_brace_between_points((3/5, 0), (3/5, 4/5), direction=RIGHT, color=CS[1]),
            self.get_brace_between_points((3/5, 4/5), (0, 0), direction=Z, color=CS[2]),
        ]
        labels = [
            MathTex("x", color=CS[0]),
            MathTex("y", color=CS[1]),
            MathTex("1", color=CS[2]),
        ]
        for (brace, label) in zip(braces, labels):
            brace.put_at_tip(label, buff=0.1)
            self.play(
                GrowFromCenter(brace),
                Write(label),
            )
        for tex in texs:
            for i in range(3):
                tex[i*2].set_color(CS[i])
        self.play(Create(triangles[2]), Write(texs[0][4]))
        self.play(triangles[2].animate
            .rotate(-math.atan2(4, 3), about_point=triangles[2].get_vertices()[0])
            .next_to(texs[0][4][0], DOWN)
            .shift(0.16 * RIGHT)
        )
        self.play(Write(texs[0][:4]))
        self.play(Create(triangles[0]))
        self.play(Create(triangles[1]))
        self.play(
            triangles[0].animate
                .next_to(texs[0][0][0], DOWN),
            triangles[1].animate
                .rotate(-PI/2, about_point=triangles[1].get_vertices()[0])
                .next_to(texs[0][2][0], DOWN),
        )
        self.play(
            triangles[0].animate
                .flip(LEFT),
            triangles[1].animate
                .flip(LEFT),
        )
        squares = [
            Square(color=CS[0], side_length=np.linalg.norm(triangles[0].get_vertices()[2] - triangles[0].get_vertices()[0])),
            Square(color=CS[1], side_length=np.linalg.norm(triangles[1].get_vertices()[2] - triangles[1].get_vertices()[0])),
            Square(color=CS[2], side_length=np.linalg.norm(triangles[2].get_vertices()[2] - triangles[2].get_vertices()[0])),
        ]
        squares[0].shift(triangles[0].get_vertices()[0] - squares[0].get_corner(UL))
        squares[1].shift(triangles[1].get_vertices()[0] - squares[1].get_corner(UL))
        squares[2].shift(triangles[2].get_vertices()[0] - squares[2].get_corner(UL))
        self.play(
            Create(squares[0]),
            Create(squares[1]),
            Create(squares[2]),
        )
        self.play(ReplacementTransform(texs[0], texs[1]))
        self.play(Unwrite(texs[1][0][0]), Unwrite(texs[1][2][0]), Unwrite(texs[1][4][0]))
        self.play(*(FadeOut(obj) for obj in lines + triangles + braces + labels + [texs[1]] + squares))
        i_arrow = self.get_arrow((0, 0), (1, 0), CS[0])
        j_arrow = self.get_arrow((0, 0), (0, 1), CS[1])
        ij_angle = RightAngle(i_arrow, j_arrow, length=0.2, color=LIGHT_GRAY)
        v_tex = MathTex("v =").move_to(LEFT*6)
        v_tex[0].set_color(CS[2])
        r_mat = Matrix([["g_x","r_x"],["g_y","r_y"]]).next_to(v_tex, RIGHT)
        r_mat.set_column_colors(*CS)
        v_vec = Matrix([["v_g"],["v_r"]]).next_to(r_mat, RIGHT)
        v_arrow = self.get_arrow((0, 0), (2, 1), CS[2])
        self.play(Create(i_arrow), Create(j_arrow), Create(ij_angle))
        self.play(Create(v_arrow))
        self.play(Write(v_tex))
        self.play(Write(r_mat))
        self.play(Write(v_vec))
        self.play(*(Rotate(obj, PI/4, about_point=self.origin) for obj in [i_arrow, j_arrow, ij_angle, v_arrow]))
        r_mat_0 = Matrix([["g_x"],["g_y"]]).next_to(v_tex, RIGHT)
        r_mat_0.set_column_colors(CS[0])
        v_vec_0 = MathTex("v_g").next_to(r_mat_0, RIGHT)
        p_tex = MathTex("+").next_to(v_vec_0, RIGHT)
        r_mat_1 = Matrix([["r_x"],["r_y"]]).next_to(p_tex, RIGHT)
        r_mat_1.set_column_colors(CS[1])
        v_vec_1 = MathTex("v_r").next_to(r_mat_1, RIGHT)
        self.play(
            FadeOut(r_mat.get_brackets()),
            FadeOut(v_vec.get_brackets())
        )
        self.play(
            ReplacementTransform(r_mat.get_columns()[0], r_mat_0.get_columns()[0]),
            ReplacementTransform(r_mat.get_columns()[1], r_mat_1.get_columns()[0]),
            ReplacementTransform(v_vec.get_rows()[0], v_vec_0),
            ReplacementTransform(v_vec.get_rows()[1], v_vec_1),
            Create(p_tex),
        )
        self.play(
            FadeIn(r_mat_0.get_brackets()),
            FadeIn(r_mat_1.get_brackets()),
        )
        v_vec_0_c = v_vec_0.copy()
        v_vec_1_c = v_vec_1.copy()
        p_tex_c = p_tex.copy()
        self.play(
            FadeOut(r_mat_0.get_brackets()),
            FadeOut(r_mat_1.get_brackets()),
        )
        self.play(
            v_vec_0.animate.next_to(r_mat_0.get_entries()[0], RIGHT),
            v_vec_0_c.animate.next_to(r_mat_0.get_entries()[1], RIGHT),
            v_vec_1.animate.next_to(r_mat_1.get_entries()[0], RIGHT),
            v_vec_1_c.animate.next_to(r_mat_1.get_entries()[1], RIGHT),
            p_tex.animate.next_to(r_mat_1.get_entries()[0], LEFT),
            p_tex_c.animate.next_to(r_mat_1.get_entries()[1], LEFT),
        )
        self.play(
            p_tex.animate.next_to(v_vec_0, RIGHT),
            p_tex_c.animate.next_to(v_vec_0_c, RIGHT),
            r_mat_1.get_entries()[0].animate.next_to(p_tex.target, RIGHT),
            r_mat_1.get_entries()[1].animate.next_to(p_tex_c.target, RIGHT),
            v_vec_1.animate.next_to(r_mat_1.get_entries()[0].target, RIGHT),
            v_vec_1_c.animate.next_to(r_mat_1.get_entries()[1].target, RIGHT),
        )
        r_mat_1.get_brackets()[1].set_x(v_vec_1.get_right()[0] + MED_SMALL_BUFF)
        self.play(
            FadeIn(r_mat_0.get_brackets()[0]),
            FadeIn(r_mat_1.get_brackets()[1]),
        )
        brace = BraceBetweenPoints(
            np.array([v_arrow.get_start()[0], v_arrow.get_end()[1], 0]),
            np.array([v_arrow.get_end()[0], v_arrow.get_end()[1], 0]),
            direction=UP,
            buff=0,
            color=CS[2]
        )
        label = MathTex(
            r"{{v_x}}",
            r"= \begin{bmatrix} {{g_x}} & {{r_x}} \end{bmatrix}",
            r"\begin{bmatrix} v_g \\ v_r \end{bmatrix}")
        label[0].set_color(CS[2])
        label[2].set_color(CS[0])
        label[4].set_color(CS[1])
        label.next_to(brace.get_tip(), UP, aligned_edge=LEFT)
        self.play(GrowFromCenter(brace))
        self.play(Write(label))
        self.play(
            FadeOut(*(mob for mob in self.mobjects if mob not in [
                self.axes, self.unit_circle, title, i_arrow, j_arrow, ij_angle, v_arrow])),
            *(Rotate(obj, -PI/4, about_point=self.origin) for obj in [i_arrow, j_arrow, ij_angle, v_arrow]),
        )
        matrix_180 = Matrix([[-1, 0],[0,-1]]).move_to(LEFT*4)
        matrix_180.set_column_colors(*CS)
        tex_180 = MathTex(r"\text{1/2 turn : } x \leftrightarrow -x,\ y \leftrightarrow -y").next_to(matrix_180, UP)
        self.play(
            Create(matrix_180),
            Create(tex_180),
        )
        self.play(*(Rotate(obj, PI, about_point=self.origin, axis=UP) for obj in [i_arrow, j_arrow, ij_angle, v_arrow]))
        self.play(*(Rotate(obj, PI, about_point=self.origin, axis=RIGHT) for obj in [i_arrow, j_arrow, ij_angle, v_arrow]))
        self.play(*(Rotate(obj, -PI, about_point=self.origin) for obj in [i_arrow, j_arrow, ij_angle, v_arrow]))
        matrix_90 = Matrix([[0, -1],[1, 0]]).move_to(LEFT*4)
        matrix_90.set_column_colors(*CS)
        tex_90 = MathTex(r"\text{1/4 turn : } x \leftrightarrow y,\ y \leftrightarrow -y").next_to(matrix_90, UP)
        self.play(
            FadeOut(matrix_180),
            FadeOut(tex_180),
        )
        self.play(
            Create(matrix_90),
            Create(tex_90),
        )
        self.play(*(Rotate(obj, PI, about_point=self.origin, axis=UP+RIGHT) for obj in [i_arrow, j_arrow, ij_angle, v_arrow]))
        self.play(*(Rotate(obj, PI, about_point=self.origin, axis=UP) for obj in [i_arrow, j_arrow, ij_angle, v_arrow]))
        self.play(*(Rotate(obj, -PI/2, about_point=self.origin) for obj in [i_arrow, j_arrow, ij_angle, v_arrow]))

    def play_projection_covector(self, title):
        self.play(Create(self.axes), Create(self.unit_circle))
        color_1, color_0, color_c = CS[0:3]
        theta = PI/3
        x, y = math.cos(theta), math.sin(theta)
        x_line = self.get_dashed_line((x, y - 0.1), (x, -1), color_c)
        y_line = self.get_dashed_line((x + 0.1, y), (2, y), color_c)
        x_brace = self.get_brace_between_points((0, -1), (x, -1), color_c, DOWN)
        y_brace = self.get_brace_between_points((2, 0), (2, y), color_c, RIGHT)
        x_tex = MathTex("x", color=color_c, font_size=32).next_to(x_brace, 0.5 * DOWN)
        y_tex = MathTex("y", color=color_c, font_size=32).next_to(y_brace, 0.5 * RIGHT)
        covector = Matrix([["x", "y"]]).move_to(LEFT*5)
        covector.set_column_colors(color_c, color_c)
        line_c, circle_c = self.get_lircle((x, y), color_c)
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
        arrow_1 = self.get_arrow((0, 0), (x, y), color_1)
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
        arrow_0 = self.get_arrow((0, 0), (-y, x), color_0)
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
            GrowFromPoint(line_c, self.origin),
            Create(angle_1c),
            FadeIn(tex_1_l),
        )
        arrow_1_c = arrow_1.copy()
        tex_1_c = tex_1.copy()
        self.play(
            tex_1_c.animate.set_color(CS[-1]),
            arrow_1_c.animate.set_color(CS[-1]),
        )
        ax, ay = x, y
        for diff in [(-4*y, 4*x), (8*y, -8*x), (-4*y, 4*x)]:
            ax, ay = ax + diff[0], ay + diff[1]
            self.play(
                arrow_1_c.animate.put_start_and_end_on(self.origin, self.axes.c2p(ax, ay)),
                tex_1_c.animate.next_to(arrow_1_c.target.get_end(), UP),
        )
        self.play(
            FadeOut(angle_01),
            FadeOut(angle_1c),
            FadeOut(vector_01),
            FadeOut(arrow_0),
            FadeOut(arrow_1),
            FadeOut(arrow_1_c),
            FadeOut(tex_0),
            FadeOut(tex_1),
            FadeOut(tex_1_c),
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
            new_line_c, new_circle_c = self.get_lircle((x, y), color_c)
            self.play(
                ReplacementTransform(circle_c, new_circle_c),
                ReplacementTransform(line_c, new_line_c),
            )
            circle_c = new_circle_c
            line_c = new_line_c
        self.play(FadeOut(*(obj for obj in self.mobjects if obj != title)))
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
        self.play(
            FadeOut(vector_4_l.get_brackets()),
            FadeOut(vector_4_l.get_entries()[2:]),
            FadeOut(vector_4_r.get_brackets()),
            FadeOut(vector_4_r.get_entries()[:2]),
            FadeOut(covector_4_l_f.get_brackets()),
            FadeOut(covector_4_l_f.get_entries()[2:]),
            FadeOut(covector_4_r_f.get_brackets()),
            FadeOut(covector_4_r_f.get_entries()[:2]),
        )
        self.play(
            vector_4_l.get_entries()[1].animate.next_to(tex_p, LEFT),
            covector_4_l_f.get_entries()[1].animate.next_to(vector_4_l.get_entries()[1].target, LEFT),
            covector_4_r_f.get_entries()[2].animate.next_to(tex_p, RIGHT),
            vector_4_r.get_entries()[2].animate.next_to(covector_4_r_f.get_entries()[2].target, RIGHT),
        )
        tex_p_l = tex_p.copy().next_to(covector_4_l_f.get_entries()[1], LEFT)
        tex_p_r = tex_p.copy().next_to(vector_4_r.get_entries()[2], RIGHT)
        self.play(
            Create(tex_p_l),
            Create(tex_p_r),
        )
        self.play(
            vector_4_l.get_entries()[0].animate.next_to(tex_p_l, LEFT),
            covector_4_l_f.get_entries()[0].animate.next_to(vector_4_l.get_entries()[0].target, LEFT),
            covector_4_r_f.get_entries()[3].animate.next_to(tex_p_r, RIGHT),
            vector_4_r.get_entries()[3].animate.next_to(covector_4_r_f.get_entries()[3].target, RIGHT),
        )
        self.play(FadeOut(*(obj for obj in self.mobjects if obj not in [title, self.axes, self.unit_circle])))
        tex_0 = MathTex(
            r"{{v}} = {{v_u}} + {{v_{u^\perp}}}",
            tex_to_color_map={"v": CS[1], "v_u": CS[-1], r"v_{u^\perp}": CS[2]},
        ).move_to(LEFT*4)
        arrow_u = self.get_arrow((0, 0), (2, 1), CS[0])
        arrow_v = self.get_arrow((0, 0), (2, 4), CS[1])
        arrow_vu = self.get_arrow((0, 0), (2*8/5, 1*8/5), CS[-1])
        arrow_vup = self.get_arrow((2*8/5, 1*8/5), (2, 4), CS[2])
        angle_v = RightAngle(arrow_vu, arrow_vup, length=0.4, quadrant=(-1, 1), color=LIGHT_GRAY)
        self.play(
            FadeIn(self.axes),
            FadeIn(self.unit_circle),
        )
        self.play(
            Create(tex_0),
            Create(arrow_u),
            Create(arrow_v),
        )
        self.play(Create(arrow_vu))
        self.play(
            Create(arrow_vup),
            Create(angle_v)
        )
        self.play(FadeOut(arrow_vu, arrow_vup, angle_v))
        self.play(tex_0.animate.shift(UP))
        tex_1 = MathTex(
            r"{{\hat{u}}} = \frac{ {{u}} }{\sqrt{ {{u^T}} {{u}} }}",
            tex_to_color_map={r"\hat{u}": CS[0], "u": CS[0], r"u^T": CS[0]},
        ).next_to(tex_0, DOWN)
        self.play(Create(tex_1))
        line_u, circle_u = self.get_lircle((2, 1), CS[0])
        self.play(
            arrow_u.animate.set_opacity(0.5),
            ReplacementTransform(arrow_u.copy(), circle_u),
            GrowFromPoint(line_u, self.origin),
        )
        arrow_uu = self.get_arrow((0, 0), (2 / math.sqrt(5), 1 / math.sqrt(5)), CS[0])
        line_uu, circle_uu = self.get_lircle((2 / math.sqrt(5), 1 / math.sqrt(5)), CS[0])
        self.play(
            ReplacementTransform(arrow_u, arrow_uu),
            ReplacementTransform(circle_u, circle_uu),
            ReplacementTransform(line_u, line_uu),
        )
        tex_2 = MathTex(
            r"{{ v_u }} = \left( {{ \hat{u}^T }} {{ v }} \right) {{ \hat{u} }} = \left( \frac{u^T v}{u^T u} \right) u",
            tex_to_color_map={"v_u": CS[-1], r"\hat{u}^T": CS[0], "v": CS[1], r"\hat{u}": CS[0], r"u^T": CS[0], "u": CS[0]},
        ).next_to(tex_1, DOWN)
        self.play(Create(tex_2))
        self.play(Create(arrow_vu))
        tex_3 = MathTex(
            r"\implies {{v_{u^\perp}}} = {{v}} - {{v_u}}",
            tex_to_color_map={"v": CS[1], "v_u": CS[-1], r"v_{u^\perp}": CS[2]},
        ).next_to(tex_0, RIGHT)
        self.play(Create(tex_3))
        self.play(
            Create(arrow_vup),
            Create(angle_v),
        )

    def play_rotation_inverse(self, title):
        self.play(Create(self.axes), Create(self.unit_circle))
        theta = PI/3
        x, y = math.cos(theta), math.sin(theta)
        i_arrow = self.get_arrow((0, 0), (1, 0), CS[0])
        j_arrow = self.get_arrow((0, 0), (0, 1), CS[1])
        ij_angle = RightAngle(i_arrow, j_arrow, length=0.2, color=LIGHT_GRAY)
        r_tex = Matrix([["g_x","r_x"],["g_y","r_y"]]).move_to(LEFT*4)
        r_tex.set_column_colors(*CS)
        self.play(Create(i_arrow), Create(j_arrow), Create(ij_angle))
        self.play(
            Create(r_tex),
            *(Rotate(obj, theta, about_point=self.origin) for obj in [i_arrow, j_arrow, ij_angle]),
        )
        self.play(r_tex.animate.shift(RIGHT*1.5))
        s_tex = MathTex("-1").next_to(r_tex, RIGHT+UP, buff=0)
        e_tex = MathTex("=").next_to(r_tex, LEFT)
        t_tex = Matrix([["g_x","g_y"],["r_x","r_y"]]).next_to(e_tex, LEFT)
        t_tex.set_row_colors(*CS)
        i_line, i_circle = self.get_lircle((x, y), CS[0])
        j_line, j_circle = self.get_lircle((-y, x), CS[1])
        self.play(
            Create(s_tex),
            Create(e_tex),
            Create(t_tex),
            i_arrow.animate.set_opacity(0.5),
            ReplacementTransform(i_arrow.copy(), i_circle),
            GrowFromPoint(i_line, self.origin),
            j_arrow.animate.set_opacity(0.5),
            ReplacementTransform(j_arrow.copy(), j_circle),
            GrowFromPoint(j_line, self.origin),
        )
        self.play(
            i_arrow.animate.set_opacity(1),
            j_arrow.animate.set_opacity(1),
        )
        self.play(FadeOut(*(obj for obj in self.mobjects if obj not in [title, self.axes, self.unit_circle])))
        theta = PI/3
        x, y = math.cos(theta), math.sin(theta)
        g_arrow = self.get_arrow((0, 0), (x, y), CS[0])
        y_arrow = self.get_arrow((0, 0), (3, 1), CS[2])
        g_matrix = Matrix([["g_x","g_y"],["-","-"]]).move_to(LEFT*5)
        g_matrix.set_row_colors(CS[0])
        y_matrix = Matrix([["v_x"],["v_y"]]).next_to(g_matrix, RIGHT)
        y_matrix.set_column_colors(CS[2])
        self.play(
            Create(g_arrow),
            Create(y_arrow),
            Create(g_matrix),
            Create(y_matrix),
        )
        self.play(
            Rotate(g_arrow, -theta, about_point=self.origin),
            Rotate(y_arrow, -theta, about_point=self.origin),
        )
        y_line = DashedLine(start=y_arrow.get_end(), end=[y_arrow.get_end()[0], y_arrow.get_start()[1], 0], color=CS[2])
        self.play(Create(y_line))
        r_tex = MathTex("g_x v_x + g_y v_y", tex_to_color_map={"g_x": CS[0], "g_y": CS[0], "v_x": CS[2], "v_y": CS[2]}).next_to(y_line, UP)
        self.play(Create(r_tex))

    def play_spectral_theorem(self, title):
        self.play(Create(self.axes), Create(self.unit_circle))
        g_arrow = self.get_arrow((0, 0), (1, 0), CS[0])
        r_arrow = self.get_arrow((0, 0), (0, 1), CS[1])
        matrix = Matrix([[1,0],[0,1]]).move_to(LEFT*5)
        matrix.set_column_colors(*CS)
        eigen_tex = MathTex(r"v = \lambda v").next_to(matrix, RIGHT)
        eigen_tex[0][::3].set_color(CS[-1])
        self.play(
            Create(g_arrow),
            Create(r_arrow),
            Create(matrix),
            Create(eigen_tex),
        )
        lines = []
        for t in range(32):
            theta = 2*PI*t/32
            x, y = 4*math.cos(theta), 4*math.sin(theta)
            c = (abs(x)*CS[0] + abs(y)*CS[1])/(abs(x)+abs(y))
            lines.append(self.get_line((0, 0), (x, y), c, 0.5))
        self.play(*(Create(line) for line in lines))
        eigen_vector = self.get_line((-4, 0), (4, 0), CS[-1])
        self.play(GrowFromCenter(eigen_vector))
        self.play(Rotate(eigen_vector, PI, about_point=self.origin))
        self.play(ShrinkToCenter(eigen_vector))
        
        shear = [[1, 0],[0.5, 1]]
        g_arrow_sheared = self.get_arrow((0, 0), (shear[0][0], shear[1][0]), CS[0])
        r_arrow_sheared = self.get_arrow((0, 0), (shear[0][1], shear[1][1]), CS[1])
        matrix_sheared = Matrix(shear).move_to(LEFT*5)
        matrix_sheared.set_column_colors(*CS)
        lines_sheared = []
        for t in range(32):
            theta = 2*PI*t/32
            x, y = 4*math.cos(theta), 4*math.sin(theta)
            c = (abs(x)*CS[0] + abs(y)*CS[1])/(abs(x)+abs(y))
            x, y = shear[0][0]*x + shear[0][1]*y, shear[1][0]*x + shear[1][1]*y
            lines_sheared.append(self.get_line((0, 0), (x, y), c, stroke_opacity=0.5))
        arrows_sheared = []
        for t in range(32):
            theta = 2*PI*t/32
            x, y = math.cos(theta), math.sin(theta)
            c = (abs(x)*CS[0] + abs(y)*CS[1])/(abs(x)+abs(y))
            x_u, y_u = shear[0][0]*x + shear[0][1]*y, shear[1][0]*x + shear[1][1]*y
            arrows_sheared.append(self.get_arrow((x, y), (x_u, y_u), c))
        _, eigen_vectors = np.linalg.eig(np.array(shear))
        self.play(
            ReplacementTransform(g_arrow, g_arrow_sheared),
            ReplacementTransform(r_arrow, r_arrow_sheared),
            ReplacementTransform(matrix, matrix_sheared),
            eigen_tex.animate.next_to(matrix_sheared, RIGHT),
            *(ReplacementTransform(line, line_sheared) for (line, line_sheared) in zip(lines, lines_sheared)),
            *(Create(arrow_sheared) for arrow_sheared in arrows_sheared),
        )
        eigen_line = self.get_line((-4*eigen_vectors[0][0], -4*eigen_vectors[1][0]), (4*eigen_vectors[0][0], 4*eigen_vectors[1][0]), CS[-1])
        self.play(Create(eigen_line))
        eigen_line.put_start_and_end_on(eigen_line.get_end(), eigen_line.get_start())
        self.play(Uncreate(eigen_line))
        aligned_shear = [[1, -0.5],[0.5, 1]]
        g_arrow_aligned_sheared = self.get_arrow((0, 0), (aligned_shear[0][0], aligned_shear[1][0]), CS[0])
        r_arrow_aligned_sheared = self.get_arrow((0, 0), (aligned_shear[0][1], aligned_shear[1][1]), CS[1])
        matrix_aligned_sheared = Matrix(aligned_shear).move_to(LEFT*5)
        matrix_aligned_sheared.set_column_colors(*CS)
        lines_aligned_sheared = []
        for t in range(32):
            theta = 2*PI*t/32
            x, y = 4*math.cos(theta), 4*math.sin(theta)
            c = (abs(x)*CS[0] + abs(y)*CS[1])/(abs(x)+abs(y))
            x, y = aligned_shear[0][0]*x + aligned_shear[0][1]*y, aligned_shear[1][0]*x + aligned_shear[1][1]*y
            lines_aligned_sheared.append(self.get_line((0, 0), (x, y), c, stroke_opacity=0.5))
        arrows_aligned_sheared = []
        for t in range(32):
            theta = 2*PI*t/32
            x, y = math.cos(theta), math.sin(theta)
            c = (abs(x)*CS[0] + abs(y)*CS[1])/(abs(x)+abs(y))
            x_u, y_u = aligned_shear[0][0]*x + aligned_shear[0][1]*y, aligned_shear[1][0]*x + aligned_shear[1][1]*y
            arrows_aligned_sheared.append(self.get_arrow((x, y), (x_u, y_u), c))
        self.play(
            ReplacementTransform(g_arrow_sheared, g_arrow_aligned_sheared),
            ReplacementTransform(r_arrow_sheared, r_arrow_aligned_sheared),
            ReplacementTransform(matrix_sheared, matrix_aligned_sheared),
            eigen_tex.animate.next_to(matrix_aligned_sheared, RIGHT),
            *(ReplacementTransform(line_sheared, line_aligned_sheared) for (line_sheared, line_aligned_sheared) in zip(lines_sheared, lines_aligned_sheared)),
            *(ReplacementTransform(arrow_sheared, arrow_aligned_sheared) for (arrow_sheared, arrow_aligned_sheared) in zip(arrows_sheared, arrows_aligned_sheared)),
        )
        counter_shear = [[1, 0.5],[0.5, 1]]
        g_arrow_counter_sheared = self.get_arrow((0, 0), (counter_shear[0][0], counter_shear[1][0]), CS[0])
        r_arrow_counter_sheared = self.get_arrow((0, 0), (counter_shear[0][1], counter_shear[1][1]), CS[1])
        matrix_counter_sheared = Matrix(counter_shear).move_to(LEFT*5)
        matrix_counter_sheared.set_column_colors(*CS)
        lines_counter_sheared = []
        for t in range(32):
            theta = 2*PI*t/32
            x, y = 4*math.cos(theta), 4*math.sin(theta)
            c = (abs(x)*CS[0] + abs(y)*CS[1])/(abs(x)+abs(y))
            x, y = counter_shear[0][0]*x + counter_shear[0][1]*y, counter_shear[1][0]*x + counter_shear[1][1]*y
            lines_counter_sheared.append(self.get_line((0, 0), (x, y), c, stroke_opacity=0.5))
        arrows_counter_sheared = []
        for t in range(32):
            theta = 2*PI*t/32
            x, y = math.cos(theta), math.sin(theta)
            c = (abs(x)*CS[0] + abs(y)*CS[1])/(abs(x)+abs(y))
            x_u, y_u = counter_shear[0][0]*x + counter_shear[0][1]*y, counter_shear[1][0]*x + counter_shear[1][1]*y
            arrows_counter_sheared.append(self.get_arrow((x, y), (x_u, y_u), c))
        self.play(
            ReplacementTransform(g_arrow_aligned_sheared, g_arrow_counter_sheared),
            ReplacementTransform(r_arrow_aligned_sheared, r_arrow_counter_sheared),
            ReplacementTransform(matrix_aligned_sheared, matrix_counter_sheared),
            eigen_tex.animate.next_to(matrix_counter_sheared, RIGHT),
            *(ReplacementTransform(line_aligned_sheared, line_counter_sheared) for (line_aligned_sheared, line_counter_sheared) in zip(lines_aligned_sheared, lines_counter_sheared)),
            *(ReplacementTransform(arrow_aligned_sheared, arrow_counter_sheared) for (arrow_aligned_sheared, arrow_counter_sheared) in zip(arrows_aligned_sheared, arrows_counter_sheared)),
        )
        _, eigen_vectors = np.linalg.eig(np.array(counter_shear))
        for i in range(2):
            eigen_line = self.get_line((-4*eigen_vectors[0][i], -4*eigen_vectors[1][i]), (4*eigen_vectors[0][i], 4*eigen_vectors[1][i]), CS[-1])
            self.play(Create(eigen_line))
            eigen_line.put_start_and_end_on(eigen_line.get_end(), eigen_line.get_start())
            self.play(Uncreate(eigen_line))
        imbalanced_counter_shear = [[1.5, 0.5],[0.5, 1]]
        g_arrow_imbalanced_counter_sheared = self.get_arrow((0, 0), (imbalanced_counter_shear[0][0], imbalanced_counter_shear[1][0]), CS[0])
        r_arrow_imbalanced_counter_sheared = self.get_arrow((0, 0), (imbalanced_counter_shear[0][1], imbalanced_counter_shear[1][1]), CS[1])
        matrix_imbalanced_counter_sheared = Matrix(imbalanced_counter_shear).move_to(LEFT*5)
        matrix_imbalanced_counter_sheared.set_column_colors(*CS)
        lines_imbalanced_counter_sheared = []
        for t in range(32):
            theta = 2*PI*t/32
            x, y = 4*math.cos(theta), 4*math.sin(theta)
            c = (abs(x)*CS[0] + abs(y)*CS[1])/(abs(x)+abs(y))
            x, y = imbalanced_counter_shear[0][0]*x + imbalanced_counter_shear[0][1]*y, imbalanced_counter_shear[1][0]*x + imbalanced_counter_shear[1][1]*y
            lines_imbalanced_counter_sheared.append(self.get_line((0, 0), (x, y), c, stroke_opacity=0.5))
        arrows_imbalanced_counter_sheared = []
        for t in range(32):
            theta = 2*PI*t/32
            x, y = math.cos(theta), math.sin(theta)
            c = (abs(x)*CS[0] + abs(y)*CS[1])/(abs(x)+abs(y))
            x_u, y_u = imbalanced_counter_shear[0][0]*x + imbalanced_counter_shear[0][1]*y, imbalanced_counter_shear[1][0]*x + imbalanced_counter_shear[1][1]*y
            arrows_imbalanced_counter_sheared.append(self.get_arrow((x, y), (x_u, y_u), c))
        self.play(
            ReplacementTransform(g_arrow_counter_sheared, g_arrow_imbalanced_counter_sheared),
            ReplacementTransform(r_arrow_counter_sheared, r_arrow_imbalanced_counter_sheared),
            ReplacementTransform(matrix_counter_sheared, matrix_imbalanced_counter_sheared),
            eigen_tex.animate.next_to(matrix_imbalanced_counter_sheared, RIGHT),
            *(ReplacementTransform(line_counter_sheared, line_imbalanced_counter_sheared) for (line_counter_sheared, line_imbalanced_counter_sheared) in zip(lines_counter_sheared, lines_imbalanced_counter_sheared)),
            *(ReplacementTransform(arrow_counter_sheared, arrow_imbalanced_counter_sheared) for (arrow_counter_sheared, arrow_imbalanced_counter_sheared) in zip(arrows_counter_sheared, arrows_imbalanced_counter_sheared)),
        )
        _, eigen_vectors = np.linalg.eig(np.array(imbalanced_counter_shear))
        for i in range(2):
            eigen_line = self.get_line((-4*eigen_vectors[0][i], -4*eigen_vectors[1][i]), (4*eigen_vectors[0][i], 4*eigen_vectors[1][i]), CS[-1])
            self.play(Create(eigen_line))
            eigen_line.put_start_and_end_on(eigen_line.get_end(), eigen_line.get_start())
            self.play(Uncreate(eigen_line))
        self.play(
            FadeOut(self.axes),
            FadeOut(g_arrow_imbalanced_counter_sheared),
            FadeOut(r_arrow_imbalanced_counter_sheared),
            FadeOut(matrix_imbalanced_counter_sheared),
            FadeOut(eigen_tex),
            *(FadeOut(line) for line in lines_imbalanced_counter_sheared),
            *(Rotate(arrow, -math.atan2(eigen_vectors[1][0], eigen_vectors[0][0]), about_point=self.origin) for arrow in arrows_imbalanced_counter_sheared),
        )
        tex = MathTex(r"\left(\frac{x}{a}\right)^2 + \left(\frac{y}{b}\right)^2 = c^2").move_to(LEFT*4)
        tex.set_color_by_gradient(CS[:2])
        self.play(Write(tex))
        self.play(FadeOut(*(obj for obj in self.mobjects if obj != title)))

        tex = MathTex(
            r"f(x, y) = xy",
            r"\implies \partial_x f = y"
        ).move_to(LEFT*3)
        tex[0].set_color(CS[1])
        tex[1].set_color(CS[0])
        rectangle = Rectangle(width=2, height=4, color=CS[1], fill_color=CS[1], fill_opacity=0.3).shift(3*RIGHT)
        line_v = Line(color=CS[0], start=(rectangle.get_corner(DOWN + RIGHT) + [0.05, 0, 0]), end=(rectangle.get_corner(UP + RIGHT) + [0.05, 0, 0]), stroke_width=8)
        tex_v = MathTex("y").next_to(rectangle, RIGHT)
        tex_h = MathTex("x").next_to(rectangle, UP)
        self.play(
            Write(tex),
            Create(rectangle),
            Write(tex_v),
            Write(tex_h),
        )
        self.play(Create(line_v))
        self.play(FadeOut(*(obj for obj in self.mobjects if obj != title)))
        tex = MathTex(
            r"f(x, y) = x^2",
            r"\implies \partial_x f = 2x"
        ).move_to(LEFT*3)
        tex[0].set_color(CS[1])
        tex[1].set_color(CS[0])
        square = Square(side_length=2, color=CS[1], fill_color=CS[1], fill_opacity=0.3).shift(3*RIGHT)
        line_v = Line(color=CS[0], start=(square.get_corner(DOWN + RIGHT) + [0.05,0,0]), end=(square.get_corner(UP + RIGHT) + 0.05), stroke_width=8)
        line_h = Line(color=CS[0], start=(square.get_corner(UP + RIGHT) + 0.05), end=(square.get_corner(UP + LEFT) + [0,0.05,0]), stroke_width=8)
        tex_v = MathTex("x").next_to(square, RIGHT)
        tex_h = MathTex("x").next_to(square, UP)
        self.play(
            Write(tex),
            Create(square),
            Write(tex_v),
            Write(tex_h),
        )
        self.play(Create(line_v))
        self.play(Create(line_h))
        self.play(FadeOut(*(obj for obj in self.mobjects if obj != title)))

        self.play(FadeIn(self.axes), FadeIn(self.unit_circle))
        circle_c = self.get_circle((1, 0), 0.1, CS[1])
        line_c = self.get_line((0, 0), (1, 0), CS[1])
        tex_f = VGroup(
            MathTex(r"f(x, y) = ", color=CS[-2]),
            Matrix([[1, 1]], h_buff=0.6),
            Matrix([["x"], ["y"]]),
            MathTex(r"= x + y", color=CS[-2]),
        ).arrange(RIGHT, buff=0.2).move_to(LEFT*3 + UP*1.5)
        box_f = Underline(tex_f[2], color=CS[1])
        tex_f[1].get_entries()[:].set_color(CS[-2])
        tex_f[1].get_brackets().set_color(CS[-2])
        tex_f[2].get_entries()[:].set_color(CS[-2])
        tex_f[2].get_brackets().set_color(CS[-2])
        line_f, circle_f = self.get_lircle((1, 1), CS[-2])
        tex_nf = VGroup(
            MathTex(r"\nabla f(x, y) = ", color=CS[-1]),
            Matrix([[r"\partial_x f"], [r"\partial_y f"]]),
            MathTex(r" = ", color=CS[-1]),
            Matrix([[1], [1]]),
        ).arrange(RIGHT, buff=0.2).move_to(LEFT*3 - UP*1.5)
        tex_nf[1].get_entries()[:].set_color(CS[-1])
        tex_nf[1].get_brackets().set_color(CS[-1])
        tex_nf[3].get_entries()[:].set_color(CS[-1])
        tex_nf[3].get_brackets().set_color(CS[-1])
        arrow_nf = always_redraw(
            lambda: Arrow(
                start=circle_c.get_center(),
                end=circle_c.get_center() + self.axes.c2p(1, 1) - self.origin,
                color=CS[-1], buff=0)
        )
        self.play(
            Write(tex_f),
            GrowFromCenter(circle_f),
            GrowFromPoint(line_f, self.origin),
        )
        self.play(
            GrowFromCenter(circle_c),
            Create(line_c),
            Create(box_f),
            Write(tex_nf),
        )
        self.play(
            Create(arrow_nf),
        )
        self.play(
            Rotate(circle_c, PI/3, about_point=self.origin),
            Rotate(line_c, PI/3, about_point=self.origin),
        )
        self.play(
            Rotate(circle_c, -PI/12, about_point=self.origin),
            Rotate(line_c, -PI/12, about_point=self.origin),
        )
        tex_g = VGroup(
            MathTex(r"g(x, y) = ", color=CS[-2]),
            Matrix([["x", "y"]], h_buff=0.6),
            Matrix([["x"], ["y"]]),
            MathTex(r"= x^2 + y^2", color=CS[-2]),
        ).arrange(RIGHT, buff=0.2).move_to(LEFT*3 + UP*1.5)
        tex_g[1].get_entries()[:].set_color(CS[-2])
        tex_g[1].get_brackets().set_color(CS[-2])
        tex_g[2].get_entries()[:].set_color(CS[-2])
        tex_g[2].get_brackets().set_color(CS[-2])
        box_g = Underline(tex_g[2], color=CS[1])
        bracket_g = always_redraw(
            lambda: BraceBetweenPoints(
                self.origin,
                circle_c.get_center(),
                color=CS[-2],
            )
        )
        tex_ng = VGroup(
            MathTex(r"\nabla g(x, y) = ", color=CS[-1]),
            Matrix([[r"\partial_x g"], [r"\partial_y g"]]),
            MathTex(r" = 2 ", color=CS[-1]),
            Matrix([["x"], ["y"]]),
        ).arrange(RIGHT, buff=0.2).move_to(LEFT*3 - UP*1.5)
        tex_ng[1].get_entries()[:].set_color(CS[-1])
        tex_ng[1].get_brackets().set_color(CS[-1])
        tex_ng[3].get_entries()[:].set_color(CS[-1])
        tex_ng[3].get_brackets().set_color(CS[-1])
        arrow_ng = always_redraw(
            lambda: Arrow(
                start=circle_c.get_center(),
                end=3*circle_c.get_center() - 2*self.origin,
                color=CS[-1], buff=0)
        )
        self.play(
            ReplacementTransform(tex_f, tex_g),
            ReplacementTransform(box_f, box_g),
            FadeOut(circle_f),
            FadeOut(line_f),
            ReplacementTransform(tex_nf, tex_ng),
            ReplacementTransform(arrow_nf, arrow_ng),
            GrowFromCenter(bracket_g),
        )
        self.play(
            Rotate(circle_c, 2*PI, about_point=self.origin),
            Rotate(line_c, 2*PI, about_point=self.origin),
        )
        self.play(
            FadeOut(tex_g[3]),
        )
        tex_h = VGroup(
            MathTex(r"h(x, y) = ", color=CS[-2]),
            Matrix([["x", "y"]], h_buff=0.6),
            Matrix([["A_x", "A_d"], ["A_d", "A_x"]], h_buff=0.7),
            Matrix([["x"], ["y"]]),
        ).arrange(RIGHT, buff=0.2).move_to(LEFT*3 + UP*1.5)
        tex_h[1].get_entries()[:].set_color(CS[-2])
        tex_h[1].get_brackets().set_color(CS[-2])
        tex_h[2].get_entries()[:].set_color(CS[-2])
        tex_h[2].get_brackets().set_color(CS[-2])
        tex_h[3].get_entries()[:].set_color(CS[-2])
        tex_h[3].get_brackets().set_color(CS[-2])
        box_h = Underline(tex_h[3], color=CS[1])
        box_ht = Underline(tex_h[2:], color=CS[0], buff=0.3)
        arrow_hv = always_redraw(
            lambda: Arrow(
                self.origin,
                self.origin + np.dot(np.array([[1,0.5,0],[0.5,1,0],[0,0,0]]), (circle_c.get_center() - self.origin)),
                color=CS[0],
                buff=0,
            )
        )
        arrow_h = always_redraw(
            lambda: Arrow(
                start=self.origin,
                end=self.origin
                    + (v := circle_c.get_center() - self.origin) * np.dot(v, np.dot(np.array([[1,0.5,0],[0.5,1,0],[0,0,0]]), v)),
                color=CS[-2],
                buff=0,
            )
        )
        dash_h = always_redraw(
            lambda: DashedLine(
                start=self.origin + np.dot(np.array([[1,0.5,0],[0.5,1,0],[0,0,0]]), (circle_c.get_center() - self.origin)),
                end=self.origin
                    + (v := circle_c.get_center() - self.origin) * np.dot(v, np.dot(np.array([[1,0.5,0],[0.5,1,0],[0,0,0]]), v)),
                color=CS[-2],
                buff=0,
            )
        )
        tex_nh = VGroup(
            MathTex(r"\nabla h(x, y) = ", color=CS[-1]),
            Matrix([[r"\partial_x h"], [r"\partial_y h"]]),
            MathTex(r" = 2 ", color=CS[-1]),
            Matrix([["A_x", "A_d"], ["A_d", "A_x"]], h_buff=0.7),
            Matrix([["x"], ["y"]]),
        ).arrange(RIGHT, buff=0.2).move_to(LEFT*3 - UP*1.5)
        tex_nh[1].get_entries()[:].set_color(CS[-1])
        tex_nh[1].get_brackets().set_color(CS[-1])
        tex_nh[3].get_entries()[:].set_color(CS[-1])
        tex_nh[3].get_brackets().set_color(CS[-1])
        tex_nh[4].get_entries()[:].set_color(CS[-1])
        tex_nh[4].get_brackets().set_color(CS[-1])
        arrow_nh = always_redraw(
            lambda: Arrow(
                circle_c.get_center(),
                circle_c.get_center() + 2*np.dot(np.array([[1,0.5,0],[0.5,1,0],[0,0,0]]), (circle_c.get_center() - self.origin)),
                color=CS[-1],
                buff=0,
            )
        )
        box_hnt = Underline(tex_nh[3:], color=CS[0], buff=0.3)
        self.play(
            ReplacementTransform(tex_g[0], tex_h[0]),
            ReplacementTransform(tex_g[1], tex_h[1]),
            ReplacementTransform(tex_g[2], tex_h[3]),
            ReplacementTransform(box_g, box_h),
            FadeOut(bracket_g),
            Create(arrow_hv),
            Create(arrow_h),
            Create(dash_h),
            ReplacementTransform(tex_ng[0], tex_nh[0]),
            ReplacementTransform(tex_ng[1].get_entries(), tex_nh[1].get_entries()),
            tex_ng[1].get_brackets().animate.move_to(tex_nh[1].get_brackets()),
            ReplacementTransform(tex_ng[2], tex_nh[2]),
            ReplacementTransform(tex_ng[3], tex_nh[4]),
            ReplacementTransform(arrow_ng, arrow_nh),
        )
        self.play(
            Write(tex_h[2]),
            Create(box_ht),
            Create(box_hnt),
            Write(tex_nh[3]),
        )
        self.play(
            Rotate(circle_c, PI/3, about_point=self.origin),
            Rotate(line_c, PI/3, about_point=self.origin),
        )
        box_h00 = SurroundingRectangle(tex_h[2].get_rows()[0], color=CS[-1])
        box_h01 = SurroundingRectangle(tex_h[2].get_columns()[0], color=CS[-1])
        box_nh = SurroundingRectangle(tex_nh[2][0][1], color=CS[-2])
        box_nh0 = SurroundingRectangle(tex_nh[3].get_rows()[0], color=CS[-2])
        self.play(*(Create(box) for box in [box_h00, box_h01, box_nh, box_nh0]))
        self.play(*(FadeOut(box) for box in [box_h00, box_h01, box_nh, box_nh0]))
        box_h10 = SurroundingRectangle(tex_h[2].get_rows()[1], color=CS[-1])
        box_h11 = SurroundingRectangle(tex_h[2].get_columns()[1], color=CS[-1])
        box_nh = SurroundingRectangle(tex_nh[2][0][1], color=CS[-2])
        box_nh1 = SurroundingRectangle(tex_nh[3].get_rows()[1], color=CS[-2])
        self.play(*(Create(box) for box in [box_h10, box_h11, box_nh, box_nh1]))
        self.play(*(FadeOut(box) for box in [box_h10, box_h11, box_nh, box_nh1]))
        self.play(
            Rotate(circle_c, -2*PI/3, about_point=self.origin),
            Rotate(line_c, -2*PI/3, about_point=self.origin),
        )
        self.play(
            Rotate(circle_c, PI/3, about_point=self.origin),
            Rotate(line_c, PI/3, about_point=self.origin),
        )
        self.play(FadeOut(*(obj for obj in self.mobjects if obj not in [title, self.axes, self.unit_circle])))

        x_u, y_u = math.cos(PI/4), math.sin(PI/4)
        x_v, y_v = -math.sin(PI/4), math.cos(PI/4)
        arrow_u = self.get_arrow((0, 0), (x_u, y_u), CS[0])
        span_u = self.get_line((-4, -4), (4, 4), CS[0])
        arrow_v = self.get_arrow((0, 0), (x_v, y_v), CS[1])
        span_v = self.get_line((4, -4), (-4, 4), CS[1])
        angle_uv = RightAngle(arrow_u, arrow_v, length=0.2, color=LIGHT_GRAY)
        tex = VGroup(
            Matrix([["x_v", "y_v"]], h_buff=0.7),
            Matrix([["A_x", "A_d"], ["A_d", "A_y"]]),
            Matrix([["x_u"], ["y_u"]]),
        ).arrange(RIGHT, buff=0.2).move_to(LEFT*4)
        tex[0].get_entries().set_color(CS[1])
        tex[2].get_entries().set_color(CS[0])
        tex_0 = MathTex(" = 0").next_to(tex, DOWN)
        box_u = Underline(tex[1:], color=CS[0])
        box_v = Underline(tex[1:], color=CS[1])
        box_l = SurroundingRectangle(tex[0].get_rows()[0], color=CS[1])
        box_l0 = SurroundingRectangle(tex[1].get_columns()[0], color=CS[1])
        box_l1 = SurroundingRectangle(tex[1].get_columns()[1], color=CS[1])
        box_r = SurroundingRectangle(tex[2].get_columns()[0], color=CS[0])
        box_r0 = SurroundingRectangle(tex[1].get_rows()[0], color=CS[0])
        box_r1 = SurroundingRectangle(tex[1].get_rows()[1], color=CS[0])
        self.play(
            Write(tex),
            Create(arrow_u),
            Create(arrow_v),
        )
        self.play(
            Create(box_u),
            ReplacementTransform(arrow_u, span_u),
        )
        self.play(
            Write(tex_0),
            Create(angle_uv),
        )
        self.play(*(FadeIn(box) for box in [box_l, box_l0, box_l1]))
        self.play(*(FadeOut(box) for box in [box_l, box_l0, box_l1]))
        self.play(*(FadeIn(box) for box in [box_r, box_r0, box_r1]))
        self.play(*(FadeOut(box) for box in [box_r, box_r0, box_r1]))
        self.play(FadeOut(box_u))
        self.play(
            MoveAlongPath(
                tex[0].get_entries()[0],
                ArcBetweenPoints(tex[0].get_entries()[0].get_center(), tex[2].get_entries()[0].get_center(), angle=PI)),
            MoveAlongPath(
                tex[0].get_entries()[1],
                ArcBetweenPoints(tex[0].get_entries()[1].get_center(), tex[2].get_entries()[1].get_center(), angle=PI)),
            MoveAlongPath(
                tex[2].get_entries()[0],
                ArcBetweenPoints(tex[2].get_entries()[0].get_center(), tex[0].get_entries()[0].get_center(), angle=PI)),
            MoveAlongPath(
                tex[2].get_entries()[1],
                ArcBetweenPoints(tex[2].get_entries()[1].get_center(), tex[0].get_entries()[1].get_center(), angle=PI)),
            tex[1].get_entries()[1].animate.move_to(tex[1].get_entries()[2]),
            tex[1].get_entries()[2].animate.move_to(tex[1].get_entries()[1]),
        )
        for box in [box_l, box_l0, box_l1]: box.set_color(CS[0])
        for box in [box_r, box_r0, box_r1]: box.set_color(CS[1])
        self.play(*(FadeIn(box) for box in [box_l, box_l0, box_l1]))
        self.play(*(FadeOut(box) for box in [box_l, box_l0, box_l1]))
        self.play(*(FadeIn(box) for box in [box_r, box_r0, box_r1]))
        self.play(*(FadeOut(box) for box in [box_r, box_r0, box_r1]))
        self.play(
            Create(box_v),
            ReplacementTransform(arrow_v, span_v),
        )
        self.play(FadeOut(box_v))
        self.play(FadeOut(*(obj for obj in self.mobjects if obj != title)))

        get_grid = lambda color: VGroup(*([
            Line(start=(i, -4, 0), end=(i, 4, 0), color=color, stroke_opacity=0.5) for i in range(-3, 4)
        ] + [
            Line(start=(-4, i, 0), end=(4, i, 0), color=color, stroke_opacity=0.5) for i in range(-3, 4)
        ]))
        space = get_grid(CS[-1])
        self.play(Create(Dot()))
        self.play(Create(space))
        for theta in [PI/3, -PI/5]:
            v = (math.cos(theta), math.sin(theta), 0)
            eigen_space = get_grid(CS[1])
            eigen_space.rotate(angle=PI/2, axis=[-v[1],v[0],0])
            arrow = Arrow(start=(0, 0, 0), end=v, color=CS[0], buff=0)
            hidden_arrow = Arrow(start=(0, 0, 0), end=(-v[1], v[0], 0))
            angle = RightAngle(arrow, hidden_arrow, length=0.2, color=LIGHT_GRAY)
            self.play(Create(arrow))
            self.play(
                Create(angle),
                FadeIn(eigen_space),
            )
            self.play(
                FadeOut(arrow),
                FadeOut(angle),
                FadeOut(space),
            )
            space = get_grid(CS[-1])
            self.play(ReplacementTransform(eigen_space, space))
        arrow_g = Arrow(start=(0, 0, 0), end=(math.cos(PI/4), math.sin(PI/4), 0), color=CS[0], buff=0)
        arrow_r = Arrow(start=(0, 0, 0), end=(math.cos(PI/2+PI/4), math.sin(PI/2+PI/4), 0), color=CS[1], buff=0)
        angle = RightAngle(arrow_g, arrow_r, length=0.2, color=LIGHT_GRAY)
        self.play(
            Create(arrow_g),
            Create(arrow_r),
            Create(angle),
        )
        self.play(FadeOut(*(obj for obj in self.mobjects if obj != title)))

        self.play(FadeIn(self.axes), FadeIn(self.unit_circle))
        tex_e = MathTex("=").move_to(LEFT*7 + DOWN)
        tex_r = Matrix([["r_x","g_x"],["r_y","g_y"]]).next_to(tex_e, RIGHT)
        tex_r.get_columns()[0].set_color(CS[0])
        tex_r.get_columns()[1].set_color(CS[1])
        tex_s = Matrix([["r_s","0"],["0","g_s"]]).next_to(tex_r, RIGHT)
        tex_s.get_entries()[0].set_color(CS[0])
        tex_s.get_entries()[3].set_color(CS[1])
        tex_t = Matrix([["r_x","r_y"],["g_x","g_y"]]).next_to(tex_s, RIGHT)
        tex_t.get_rows()[0].set_color(CS[0])
        tex_t.get_rows()[1].set_color(CS[1])
        tex_a = Matrix([["A_x","A_d"],["A_d","A_y"]]).next_to(tex_s, UP)
        tex_a.get_columns()[0].set_color(CS[-1])
        tex_a.get_columns()[1].set_color(CS[-2])
        a = np.array([[1,0.5],[0.5,1]])
        es, ev = np.linalg.eig(np.array(a))
        lines_a = [
            self.get_line(
                start=(-(x := math.cos(i*PI/16)), -(y := math.sin(i*PI/16))),
                end=(x, y),
                color=CS[-1]*abs(8-i)/8 + CS[-2]*(8-abs(8-i))/8,
            )
            for i in range(16)
        ]
        lines_af = [
            self.get_line(
                start=np.dot(a, (-(x := math.cos(i*PI/16)), -(y := math.sin(i*PI/16)))),
                end=np.dot(a, (x, y)),
                color=CS[-1]*abs(8-i)/8 + CS[-2]*(8-abs(8-i))/8,
            )
            for i in range(16)
        ]
        arrow_r = self.get_arrow((0, 0), ev[1], CS[1])
        arrow_g = self.get_arrow((0, 0), -ev[0], CS[0])
        lines_i = [
            self.get_line(
                start=(-(x := math.cos(i*PI/16)), -(y := math.sin(i*PI/16))),
                end=(x, y),
                color=CS[0]*(abs(np.dot(ev[0],(x,y)))**2) + CS[1]*(abs(np.dot(ev[1],(x,y)))**2),
            )
            for i in range(16)
        ]
        lines_t = [
            self.get_line(
                start=np.dot(ev.T, (line.get_start() - self.origin)[:2]),
                end=np.dot(ev.T, (line.get_end() - self.origin)[:2]),
                color=line.get_color(),
            )
            for line in lines_i
        ]
        arrow_rt = self.get_arrow(start=(0, 0), end=np.dot(ev.T, (arrow_r.get_end() - self.origin)[:2]), color=CS[1])
        arrow_gt = self.get_arrow(start=(0, 0), end=np.dot(ev.T, (arrow_g.get_end() - self.origin)[:2]), color=CS[0])
        lines_s = [
            self.get_line(
                start=np.dot([[es[0],0],[0,es[1]]], (line.get_start() - self.origin)[:2]),
                end=np.dot([[es[0],0],[0,es[1]]], (line.get_end() - self.origin)[:2]),
                color=line.get_color(),
            )
            for line in lines_t
        ]
        lines_r = [
            self.get_line(
                start=np.dot(ev, (line.get_start() - self.origin)[:2]),
                end=np.dot(ev, (line.get_end() - self.origin)[:2]),
                color=line.get_color(),
            )
            for line in lines_s
        ]
        self.play(Write(tex_a))
        self.play(
            *(GrowFromCenter(line) for line in lines_a),
        )
        self.play(
            *(ReplacementTransform(line, line_f) for (line, line_f) in zip(lines_a, lines_af)),
        )
        self.play(
            Create(arrow_g),
            Create(arrow_r),
        )
        self.play(
            *(line.animate.shift(2*UP + 2*LEFT) for line in lines_af),
        )
        self.play(Write(tex_e))
        self.play(Write(tex_r))
        self.play(Write(tex_s))
        self.play(Write(tex_t))
        self.play(
            *(GrowFromCenter(line) for line in lines_i),
        )
        self.play(
            *(ReplacementTransform(line, line_c) for (line, line_c) in zip(lines_i, lines_t)),
            ReplacementTransform(arrow_g, arrow_gt),
            ReplacementTransform(arrow_r, arrow_rt),
        )
        self.play(
            FadeOut(arrow_gt),
            FadeOut(arrow_rt),
        )
        self.play(
            *(ReplacementTransform(line, line_c) for (line, line_c) in zip(lines_t, lines_s)),
        )
        self.play(
            *(ReplacementTransform(line, line_c) for (line, line_c) in zip(lines_s, lines_r)),
        )
        self.play(
            *(line.animate.shift(2*DOWN + 2*RIGHT) for line in lines_af),
        )

    def play_eigenvector_computation(self, title):
        '''
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
        self.play(FadeOut(*(obj for obj in self.mobjects if obj != title)))
        '''

    def play_svd(self, title):
        elliptic_tex = MathTex(
            r"\left(\frac{x}{a}\right)^2 + \left(\frac{y}{b}\right)^2 = 1",
            color=CS[2]).move_to(LEFT*4)
        self.play(Write(elliptic_tex))
        ellipse = Ellipse(color=CS[2], width=4, height=6).move_to(self.origin)
        self.play(ReplacementTransform(self.unit_circle.copy(), ellipse))
        self.play(FadeOut(elliptic_tex), FadeOut(ellipse))

    def construct(self):
        selected_chapter = 0
        Text.set_default(font_size=24)
        MathTex.set_default(font_size=36)
        self.axes = Axes(x_range=[-4, 4, 1], y_range=[-4, 4, 1], x_length=8, y_length=8).move_to(RIGHT*3)
        self.origin = self.axes.c2p(0, 0)
        self.unit_circle = self.get_circle((0, 0), 1, LIGHT_GRAY)
        title_texts, title_arrows = self.get_titles()
        self.add_sound("media/introduction.wav")
        self.play_introduction()
        self.play(
            *(Write(title_text) for title_text in title_texts),
            *(Create(title_arrow) for title_arrow in title_arrows),
        )
        self.play(FadeOut(*(obj for obj in self.mobjects if obj != title_texts[selected_chapter])))
        self.play(title_texts[selected_chapter].animate.scale(1.5).to_edge(UP+LEFT))
        return
        if selected_chapter == 0: self.play_rotation_matrix(title_texts[selected_chapter])
        if selected_chapter == 1: self.play_projection_covector(title_texts[selected_chapter])
        if selected_chapter == 2: self.play_rotation_inverse(title_texts[selected_chapter])
        if selected_chapter == 3: self.play_spectral_theorem(title_texts[selected_chapter])
        if selected_chapter == 4: self.play_eigenvector_computation(title_texts[selected_chapter])
        if selected_chapter == 5: self.play_svd(title_texts[selected_chapter])
        self.play(FadeOut(*(obj for obj in self.mobjects)))


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
