#!/usr/bin/env python
import argparse as ap
from plyfile import PlyData, PlyElement
import matplotlib.pyplot as mpl
import numpy as np
import random
from timeit import default_timer

import kdtree

g_MaxPts = 8

class quadTree:
    def __init__(self, bound=None, ne=None, se=None, sw=None, nw=None):
        self.bound = bound # also include bounding box
        self.ne = ne
        self.se = se
        self.sw = sw
        self.nw = nw

    def __str__(self):
        return str(self.bound) \
            + "\n├─" + "│ ".join(str(self.ne).splitlines(True)) \
            + "\n├─" + "│ ".join(str(self.se).splitlines(True)) \
            + "\n├─" + "│ ".join(str(self.sw).splitlines(True)) \
            + "\n└─" + "  ".join(str(self.nw).splitlines(True))

class leaf:
    def __init__(self, val=None, bound=None):
        self.val = val
        self.bound = bound

    def __str__(self):
        if self.val is None:
            return "{}"
        return "{" + str(self.val) + "}"

def createQuadTree(X, B=None):
    if len(X) <= g_MaxPts:
        return leaf(X,B)

    # we will usually not do this here
    if not B:
        B = ( (min([x[0] for x in X]), max(x[0] for x in X))
            , (min([x[1] for x in X]), max(x[1] for x in X))
            )

    xsplit = (B[0][0]+B[0][1])/2
    ysplit = (B[1][0]+B[1][1])/2

    ne = []
    se = []
    sw = []
    nw = []

    for x in X:
        ise = x[0] >= xsplit
        isn = x[1] >= ysplit
        if isn and ise:
            ne.append(x)
        if isn and not ise:
            nw.append(x)
        if not isn and ise:
            se.append(x)
        if not isn and not ise:
            sw.append(x)

    # descend into the four subregions
    tNE = createQuadTree(ne, ((xsplit, B[0][1]), (ysplit, B[1][1])))
    tSE = createQuadTree(se, ((xsplit, B[0][1]), (B[1][0], ysplit)))
    tSW = createQuadTree(sw, ((B[0][0], xsplit), (B[1][0], ysplit)))
    tNW = createQuadTree(nw, ((B[0][0], xsplit), (ysplit, B[1][1])))
    return quadTree(bound=B, ne=tNE, se=tSE, sw=tSW, nw=tNW)

def findNearest(x, T, dist=np.inf, best=None, trace=None):
    # check if dist radius intersects current region
    B = T.bound
    if x[0]+dist < B[0][0] \
            or x[0]-dist > B[0][1] \
            or x[1]+dist < B[1][0] \
            or x[1]-dist > B[1][1]:
                return (best, dist)

    if trace is not None:
        trace.append(B)

    if isinstance(T, quadTree):
        # search in the children
        for t in [T.ne, T.se, T.sw, T.nw]:
            (best, dist) = findNearest(x, t, dist, best, trace)

    if isinstance(T, leaf):
        for v in T.val:
            d = dist2d(x, v)
            if d < dist:
                best = v
                dist = d

    return (best, dist)

def dist2d(x,y):
    return np.linalg.norm(np.subtract(x, y))

def parseInput(filename):
    if filename:
        try:
            plydata = PlyData.read(filename)
            return plydata['vertex']
        except FileNotFoundError:
            print("Parse: invalid filename")
            quit()
    else:
        # this cannot happen
        return np.array([])

def plotPoints(points, fmt):
    X = []
    Y = []
    for p in points:
        X.append(p[0])
        Y.append(p[1])
    mpl.plot(X, Y, fmt)

if __name__ == '__main__':
    # command input
    parser = ap.ArgumentParser(description="compute convex hull of input")
    parser.add_argument("-i", "--input",
                        type=str,
                        help="filename of input data",
                        required=True)
    parser.add_argument("-t", "--timing",
                        action="store_true",
                        help="time both methods")
    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="print construcetd kd-tree for debug purposes")

    args = parser.parse_args()

    # explicitly convert to tuples
    points = [ (p[0], p[1]) for p in parseInput(args.input) ]

    epsilon = 0.75
    bounds_x = ( min([p[0] for p in points])
               , max([p[0] for p in points])
               )
    bounds_y = ( min([p[1] for p in points])
               , max([p[1] for p in points])
               )

    # generate random point
    x = ( random.uniform(bounds_x[0]-epsilon, bounds_x[1]+epsilon)
        , random.uniform(bounds_y[0]-epsilon, bounds_y[1]+epsilon)
        )

    print("Using random point", x)

    if args.timing:
        t_naive = default_timer()
    nearest_naive = min(points, key = lambda p: dist2d(x,p))
    if args.timing:
        t_naive = default_timer() - t_naive

    T = createQuadTree(points, B=(bounds_x, bounds_y))
    K = kdtree.listToKdTree(points)
    if args.debug:
        print(T)

    if args.timing:
        t_kd = default_timer()
    (nearest_kd, dist) = kdtree.findNearest(x, K)
    if args.timing:
        t_kd = default_timer() - t_kd

    if args.timing:
        t_tree = default_timer()
    trace = []
    (nearest_tree, dist) = findNearest(x, T, trace=trace)
    if args.timing:
        t_tree = default_timer() - t_tree

    if args.timing:
        print("Time per Method:")
        print("naive:              ", 1000*t_naive, "ms")
        print("kd-tree:            ", 1000*t_kd,    "ms")
        print("quadtree:           ", 1000*t_tree,  "ms")
        print("Speedup (to naive): ", t_naive/t_tree)
        print("Speedup (to kd):    ", t_kd/t_tree)

    if nearest_naive != nearest_tree:
        print("Warning: Results do not match!")
    else:
        print("Both methods found same nearest point!")

    plotPoints(points, 'b.')
    plotPoints([x], 'g.')
    plotPoints([nearest_tree], 'r.')
    if trace is not None:
        for B in trace:
            plotPoints([(B[0][0],B[1][1]), (B[0][1],B[1][1]), (B[0][1],B[1][0]), (B[0][0],B[1][0]), (B[0][0],B[1][1])], 'k-')
    mpl.show()
