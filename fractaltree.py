# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A Simple Random Fractal Tree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import argparse
import numpy as np
import sys

try:
    import cairocffi as cairo
except ImportError:
    import cairo

ITERATIONS = 16  # total number of iterations
ROOT_COLOR = np.array([0.15, 0.075, 0.0])  # root branch color
LEAF_COLOR = [1.0, 1.0, 0.2]
LEAF_COLOR_WEIGHTS = [0.2, 0.2, 0.2]
TRUNK_LEN = 200  # initial length of the trunk
TRUNK_RAD = 10.0  # initial radius of the trunk
GRASS_LEN = 4  # initial length of the grass
GRASS_RAD = 0.6  # initial radius of the grass
GRASS_COLOR = [0.4, 0.7, 0]  # initial color of grass
GRASS_COLOR_WEIGHTS = [0.6, 0.25, 0]
THETA = np.pi / 2  # initial angle of the branch
ANGLE = np.pi / 2  # angle between branches in the same level
PERTURB = 5.0  # perturb the angle a little to make the tree look random
RATIO = 0.8  # contraction factor between successive trunks

PEAK_COUNT = 16
MOUNTAIN_DEPTH = 18
MOUNTAIN_HEIGHT = 1000
MOUNTAIN_BASE_COLOR = 0.6

TRUNK_BOOST = 1.5  # boosting factor of trunk length
GRASS_ANGLE_SD = 0.3  # grass angle standard deviation

TREE_COUNT = 200
GRASS_LOWER_COUNT = 15000

WIDTH = 5040
HEIGHT = 2160

parser = argparse.ArgumentParser()
parser.add_argument("--mode", type=str)
args = parser.parse_args()

if args.mode == "debug_grass":
    TREE_COUNT = 0
    GRASS_LOWER_COUNT = 1

    WIDTH = 400
    HEIGHT = 800

    GRASS_LEN = 20
    GRASS_RAD = 3.0

ROOT = (WIDTH / 2.0, HEIGHT)


# Return an interpolation of the two colors `ROOT_COLOR` and `leaf_color`
def get_color(level, max_iter, leaf_color):
    a = float(level) / max_iter
    return a * ROOT_COLOR + (1 - a) * leaf_color


# Return random leaf color
def get_random_leaf_color():
    return np.array([LEAF_COLOR[i] - np.random.random() * LEAF_COLOR_WEIGHTS[i] for i in range(3)])


# Return the line width of a given level.
def get_line_width(level, max_iter, trunk_rad):
    return max(1, (trunk_rad / ((max_iter - level) / 2 + 1)))


# Return a random branch length depending on level and angle
def get_random_branch_length(level, max_iter, angle, t):
    randt  = min(1, (np.random.random() + (level / (max_iter * 5))))
    randt *= 1 / (1 + np.abs(np.pi / 2 - angle) / 6)
    randt *= t
    randt *= TRUNK_BOOST if level == max_iter else 1
    return randt


# Return a random grass length
def get_random_grass_length(length_init, angle):
    length = np.random.normal(
        loc=(length_init * (1 / (np.abs(angle - np.pi / 2) * 4 + 1))),
        scale=length_init / 2
    )
    return max(0, length) ** 1.5


# Return a random grass color
def get_random_grass_color():
    return np.array([GRASS_COLOR[i] + (np.random.random() - 0.5) * GRASS_COLOR_WEIGHTS[i] for i in range(3)])


# Generate and draw a mountain
def mountains(ctx, height, base, root, base_color, level):
    if level <= 0:
        return

    rootx, rooty = root

    ctx.set_line_width(0)
    color  = base_color * (0.93 ** (MOUNTAIN_DEPTH - level))
    color *= ((HEIGHT - rooty) / HEIGHT - 0.45) * 2 + 2
    ctx.set_source_rgb(color, color, color)
    ctx.move_to(rootx - base, rooty)
    ctx.line_to(rootx, rooty - height)
    ctx.line_to(rootx + base, rooty)
    ctx.line_to(rootx - base, rooty)
    ctx.fill()

    if np.random.random() < (level / MOUNTAIN_DEPTH) * 1.15: mountains(ctx, height // 2, base // 2, (rootx + base // 2, rooty), base_color, level - 1)
    if np.random.random() < (level / MOUNTAIN_DEPTH) * 1.15: mountains(ctx, height // 2, base // 2, (rootx - base // 2, rooty), base_color, level - 1)
    if np.random.random() < (level / MOUNTAIN_DEPTH) * 0.95: mountains(ctx, height // 2, base // 2, (rootx, rooty - height // 2), base_color, level - 1)
    if np.random.random() < (level / MOUNTAIN_DEPTH) * 0.95: mountains(ctx, height // -2, base // 2, (rootx, rooty - height // 2), base_color, level - 1)


# Generate and draw a bunch of grass
def grass(ctx, root, width_init, length_init):
    for i in range(int(np.random.random() * 4 + 2)):
        x0, y0 = root
        angle1 = np.random.normal(loc=(np.pi / 2), scale=0.3)
        angle2 = angle1 + np.random.random() * (angle1 - np.pi / 2)

        length = get_random_grass_length(length_init, angle1)
        width = (np.random.random() + 0.5) * width_init
        color = get_random_grass_color()

        x1, y1 = x0 + length * np.cos(angle1), y0 - length * np.sin(angle1)
        x2, y2 = x1 + length * np.cos(angle2), y1 - length * np.sin(angle2)

        ctx.set_line_width(width)
        ctx.set_source_rgb(*color)
        ctx.move_to(x0, y0)
        ctx.line_to(x1, y1)
        ctx.stroke()
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.stroke()


# Generate and draw a fractal tree
def fractal_tree(ctx, max_iter, level, start, t, leaf_color, trunk_rad, r, theta, angle, perturb):
    if level == 0:
        return

    x0, y0 = start
    randt = get_random_branch_length(level, max_iter, theta, t)
    x, y = x0 + randt * np.cos(theta), y0 - randt * np.sin(theta)

    color = get_color(level, max_iter, leaf_color)
    ctx.move_to(x0, y0)
    ctx.line_to(x, y)
    ctx.set_line_width(get_line_width(level, max_iter, trunk_rad))
    ctx.set_source_rgb(*color)
    ctx.stroke()

    theta1 = theta + np.random.random() * (perturb / (level * 1.1)) * angle
    theta2 = theta - np.random.random() * (perturb / (level * 1.1)) * angle

    if level > ITERATIONS / 2:
        theta1 = max((-np.pi / 8), min((9 * np.pi / 8), theta1))
        theta2 = max((-np.pi / 8), min((9 * np.pi / 8), theta2))

    # recursively draw the next branches
    fractal_tree(ctx, max_iter, level - 1, (x, y), t * r, leaf_color, trunk_rad,
                 r, theta1, angle, perturb)
    fractal_tree(ctx, max_iter, level - 1, (x, y), t * r, leaf_color, trunk_rad,
                 r, theta2, angle, perturb)


# Wrapper function to kick off recursive tree generation
def fractal_tree_outer(ctx, iters, rad_init, len_init):
    root_x = (np.random.random() - 0.5) * (WIDTH - 100)
    root = (ROOT[0] + root_x, ROOT[1])
    leaf_color = get_random_leaf_color()
    trunk_rad = rad_init + ((np.random.random() - 0.5) * (rad_init / 4))
    trunk_len = len_init + ((np.random.random() - 0.5) * (len_init / 4))
    fractal_tree(ctx, iters, iters, root, trunk_len, leaf_color, trunk_rad,
                 RATIO, THETA, ANGLE, PERTURB)


# Wrapper function to kick off recursive mountain generation
def mountain_outer(ctx, base_color):
    base = np.random.normal(loc=MOUNTAIN_HEIGHT, scale=400)
    height = np.random.normal(loc=base, scale=10)
    root_x = (np.random.random() - 0.5) * (WIDTH + 500)
    root = (ROOT[0] + root_x, ROOT[1])
    mountains(ctx, height, base, root, base_color, MOUNTAIN_DEPTH)


def main():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgb(0.5, 0.75, 1)
    ctx.paint()

    for fac in [1, 2][::-1]:
        for i in range(PEAK_COUNT):
            sys.stdout.write(f"{i + 1} / {PEAK_COUNT} \r")
            mountain_outer(ctx, MOUNTAIN_BASE_COLOR / fac)

        print(f"\nMountains factor {fac} done.")

    for fac in [1, 1.5, 2, 2.5, 3, 4][::-1]:
        for i in range(TREE_COUNT):
            sys.stdout.write(f"{i + 1} / {TREE_COUNT} \r")
            fractal_tree_outer(ctx, ITERATIONS // np.sqrt(fac), TRUNK_RAD / fac, TRUNK_LEN / fac)

        print(f"\nTrees factor {fac} done.")

    for i in range(GRASS_LOWER_COUNT):
        sys.stdout.write(f"{i + 1} / {GRASS_LOWER_COUNT} \r")
        root_x = (np.random.random() - 0.5) * (WIDTH - 5)
        root = (ROOT[0] + root_x, ROOT[1])
        grass(ctx, root, GRASS_RAD, GRASS_LEN)

    print("\nGrass done")

    surface.write_to_png("random_fractal_tree.png")


if __name__ == "__main__":
    main()
