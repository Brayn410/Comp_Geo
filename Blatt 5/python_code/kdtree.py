#!/usr/bin/env python
import argparse as ap
from plyfile import PlyData, PlyElement
import matplotlib.pyplot as mpl
import numpy as np
import random
from timeit import default_timer

class kdTree:
    def __init__(self, val = None, l = None, r = None):
        self.val = val
        self.l   = l
        self.r   = r

    def __str__(self):
        return str(self.val) \
            + "\n├─" + "│ ".join(str(self.l).splitlines(True)) \
            + "\n└─" + "  ".join(str(self.r).splitlines(True))

class kdLeaf:
    def __init__(self, val = None):
        self.val = val

    def __str__(self):
        if self.val is None:
            return "{}"
        return "{" + str(self.val) + "}"

def listToKdTree(P):
    X = sorted(P)
    Y = sorted(P, key = lambda p: (p[1], p[0]))
    return createBalanced(X, Y)

def createBalanced(X, Y, depth=0):
    if len(X) == 0:
        return kdLeaf()
    if len(X) == 1:
        return kdLeaf(X[0])

    # round up
    m = len(X) - len(X)//2
    T = kdTree()
    if depth%2 == 0:
        Xl = X[0:m]
        Xr = X[m:]
        # hopefully stable
        Yl = [ y for y in Y if y in Xl ]
        Yr = [ y for y in Y if y in Xr ]
        T.val = X[m-1]
    else:
        Yl = Y[0:m]
        Yr = Y[m:]
        Xl = [ x for x in X if x in Yl ]
        Xr = [ x for x in X if x in Yr ]
        T.val = Y[m-1]

    T.l = createBalanced(Xl, Yl, depth+1)
    T.r = createBalanced(Xr, Yr, depth+1)
    return T

def findNearest(x, T, depth=0, dist=np.inf, best=None, trace=None):
    if isinstance(T, kdTree):
        d = dist2d(x, T.val)

        if d < dist:
            best = T.val
            dist = d
        if trace is not None:
            trace.append(T.val)

        axis = depth % 2
        # determine execution order:
        # if point is left of splitting axis, it makes more sense to search
        # left first and vice versa
        if x[axis] <= T.val[axis]:
            # nearest point might be to the left of splitting value
            if x[axis] - dist <= T.val[axis]:
                (best, dist) = findNearest(x, T.l, depth+1, dist, best, trace)
            # nearest point might be to the right of splitting value
            if x[axis] + dist  > T.val[axis]:
                (best, dist) = findNearest(x, T.r, depth+1, dist, best, trace)
        else:
            # search in reverse order
            if x[axis] + dist  > T.val[axis]:
                (best, dist) = findNearest(x, T.r, depth+1, dist, best, trace)
            if x[axis] - dist <= T.val[axis]:
                (best, dist) = findNearest(x, T.l, depth+1, dist, best, trace)

    if isinstance(T, kdLeaf):
        d = dist2d(x, T.val)
        if d < dist:
            best = T.val
            dist = d
        if trace is not None:
            trace.append(T.val)

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
    parser.add_argument("-T", "--trace",
                        action="store_true",
                        help="trace choices of best point during execution of findNearest")

    args = parser.parse_args()

    # explicitly convert to tuples
    points = [ (p[0], p[1]) for p in parseInput(args.input) ]

    epsilon = 0.75
    bounds_x = [ min([p[0] for p in points]) - epsilon
               , max([p[0] for p in points]) + epsilon
               ]
    bounds_y = [ min([p[1] for p in points]) - epsilon
               , max([p[1] for p in points]) + epsilon
               ]

    # generate random point
    x = ( random.uniform(bounds_x[0], bounds_x[1])
        , random.uniform(bounds_y[0], bounds_y[1])
        )

    print("Using random point", x)

    if args.timing:
        t_naive = default_timer()
    nearest_naive = min(points, key = lambda p: dist2d(x,p))
    if args.timing:
        t_naive = default_timer() - t_naive

    T = listToKdTree(points)
    if args.debug:
        print(T)

    if args.timing:
        t_tree = default_timer()
    if args.trace:
        tr = []
        (nearest_tree, dist) = findNearest(x, T, trace=tr)
    else:
        (nearest_tree, dist) = findNearest(x, T)
    if args.timing:
        t_tree = default_timer() - t_tree

    if args.timing:
        print("Time per Method:")
        print("naive:  ", t_naive*1000, "ms")
        print("kdtree: ", t_tree*1000,  "ms")
        print("Speedup:", t_naive/t_tree)

    if nearest_naive != nearest_tree:
        print("Warning: Results do not match!")
    else:
        print("Both methods found same nearest point!")

    plotPoints(points, 'b.')
    if args.trace:
        plotPoints(tr, 'y.-')
    plotPoints([x], 'g.')
    plotPoints([nearest_tree], 'r.')
    mpl.show()
