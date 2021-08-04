# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A Simple Random Fractal Tree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import numpy as np
import sys

try:
    import cairocffi as cairo
except ImportError:
    import cairo

ITERATIONS = 16  # total number of iterations
ROOT_COLOR = np.array([0.15, 0.075, 0.0])  # root branch color
TRUNK_LEN = 200  # initial length of the trunk
TRUNK_RAD = 10.0  # initial radius of the trunk
GRASS_LEN = 4 # initial length of the grass
GRASS_RAD = 0.6 # initial radius of the grass
GRASS_COLOR = [0.4, 0.7, 0] # initial color of grass
THETA = np.pi / 2  # initial angle of the branch
ANGLE = np.pi / 2  # angle between branches in the same level
PERTURB = 5.0  # perturb the angle a little to make the tree look random
RATIO = 0.8  # contraction factor between successive trunks

TREE_COUNT = 200
GRASS_LOWER_COUNT = 15000

WIDTH = 5040
HEIGHT = 2160

import argparse
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

def grass(ctx, root, width_init, length_init):
    for i in range(int(np.random.random() * 4 + 2)):
        x0, y0 = root
        angle1 = np.random.normal(loc=(np.pi / 2), scale=0.3)
        angle2 = angle1 + np.random.random() * (angle1 - np.pi / 2)

        length = np.random.normal(loc=(length_init * (1 / (np.abs(angle1 - np.pi / 2) * 4 + 1))),
                                  scale=length_init / 2)
        length = max(0, length) ** 1.5
        width = (np.random.random() + 0.5) * width_init
        color = np.array([GRASS_COLOR[0] + (np.random.random() - 0.5) * 0.6, 
                          GRASS_COLOR[1] + (np.random.random() - 0.5) * 0.25, GRASS_COLOR[2]])

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


def get_color(level, leaf_color):
    """
    Return an interpolation of the two colors `ROOT_COLOR` and `leaf_color`.
    """
    a = float(level) / ITERATIONS
    return a * ROOT_COLOR + (1 - a) * leaf_color


def get_line_width(level, trunk_rad):
    """Return the line width of a given level."""
    return max(1, (trunk_rad / ((ITERATIONS - level) / 2 + 1)))


def fractal_tree(ctx,         # a cairo context to draw on
                 level,       # current level in the iterations
                 start,       # (x, y) coordinates of the start of this trunk
                 t,           # current trunk length
                 leaf_color,  # leaf color
                 trunk_rad,   # initial trunk radius
                 r,           # factor to contract the trunk in each iteration
                 theta,       # orientation of current trunk
                 angle,       # angle between branches in the same level
                 perturb,     # perturb the angle
                 ):
    if level == 0:
        return

    x0, y0 = start

    randt  = min(1, (np.random.random() + (level / (ITERATIONS * 5))))
    randt *= 1 / (1 + np.abs(np.pi / 2 - theta) / 6)
    randt *= t
    randt *= 1.5 if level == ITERATIONS else 1
    x, y = x0 + randt * np.cos(theta), y0 - randt * np.sin(theta)

    color = get_color(level, leaf_color)
    ctx.move_to(x0, y0)
    ctx.line_to(x, y)
    ctx.set_line_width(get_line_width(level, trunk_rad))
    ctx.set_source_rgb(*color)
    ctx.stroke()

    theta1 = theta + np.random.random() * (perturb / (level * 1.1)) * angle
    theta2 = theta - np.random.random() * (perturb / (level * 1.1)) * angle

    if level > ITERATIONS / 2:
        theta1 = max((-np.pi / 8), min((9 * np.pi / 8), theta1))
        theta2 = max((-np.pi / 8), min((9 * np.pi / 8), theta2))

    # recursively draw the next branches
    fractal_tree(ctx, level - 1, (x, y), t * r, leaf_color, trunk_rad,
                 r, theta1, angle, perturb)
    fractal_tree(ctx, level - 1, (x, y), t * r, leaf_color, trunk_rad,
                 r, theta2, angle, perturb)


def main():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    for i in range(TREE_COUNT):
        sys.stdout.write(f"{i} / {TREE_COUNT} \r")
        root_x = (np.random.random() - 0.5) * (WIDTH - 50)
        root = (ROOT[0] + root_x, ROOT[1])
        leaf_color = np.array([1.0 - np.random.random() * 0.2,
                               1.0 - np.random.random() * 0.2, 0.2])
        trunk_rad = TRUNK_RAD + ((np.random.random() - 0.5) * (TRUNK_RAD / 4))
        trunk_len = TRUNK_LEN + ((np.random.random() - 0.5) * (TRUNK_LEN / 4))
        fractal_tree(ctx, ITERATIONS, root, trunk_len, leaf_color, trunk_rad,
                     RATIO, THETA, ANGLE, PERTURB)

    print("\nTrees done")

    for i in range(GRASS_LOWER_COUNT):
        root_x = (np.random.random() - 0.5) * (WIDTH - 5)
        root = (ROOT[0] + root_x, ROOT[1])
        grass(ctx, root, GRASS_RAD, GRASS_LEN)

    surface.write_to_png("random_fractal_tree.png")


if __name__ == "__main__":
    main()
