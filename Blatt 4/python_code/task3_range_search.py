import os
import random
import numpy as np
import matplotlib.pyplot as plt
import time

from plyfile import PlyData


cur_dir = os.getcwd()
print(cur_dir)
data_dir = str(cur_dir) + "\\data"


plydata1 = PlyData.read(data_dir + '\\points_1.ply')
plydata2 = PlyData.read(data_dir + '\\points_2.ply')
plydata3 = PlyData.read(data_dir + '\\points_3.ply')
plydata4 = PlyData.read(data_dir + '\\points_4.ply')

used_dataset = plydata4

all_points = list(used_dataset.elements[0])

min_x = int(np.sort(all_points, order='x')[0]['x'])
max_x = int(np.sort(all_points, order='x')[len(all_points)-1]['x'])
min_y = int(np.sort(all_points, order='y')[0]['y'])
max_y = int(np.sort(all_points, order='y')[len(all_points)-1]['y'])

print("")
print("Edges:")
print("(Xmin, Xmax), (Ymin, Ymax)")
print((min_x, max_x), (min_y, max_y))

raw_input("Press Enter to start");
print("")

quarter_x = (max_x - min_x) / 4
quarter_y = (max_y - min_y) / 4

rec_left = random.randint(min_x, max_x-quarter_x)
rec_right = random.randint(max(min_x+quarter_x, rec_left+1), max_x)
rec_bottom = random.randint(min_y, max_y-quarter_y)
rec_top = random.randint(max(rec_bottom+quarter_y, rec_bottom+1), max_y)

rec = ((rec_left, rec_right), (rec_bottom, rec_top))

print("Random Rectangle:")
print("(left, right), (bottom, top)")
print(rec)
print("")

#Naive approach
start_naive = time.time()
naive_result = []
for p in all_points:
    if rec_left <= p['x'] and rec_right >= p['x']:
        if rec_bottom <= p['y'] and rec_top >= p['y']:
            naive_result.append(p)
end_naive = time.time()
print("Naive result in " + str((end_naive-start_naive)) + " seconds")

#KDTree classes
class kdNode(object):
    def __init__(self):
        self.value = None
        self.left = None
        self.right = None

class kdLeaf(object):
    def __init__(self):
        self.value = None

#function for splitting list into left and right
def splitList(full_list, median, axis):
    left = []
    right = []
    
    middle = -1
    full_list = np.sort(full_list, order=axis)
    for e in range(len(full_list)):
        if full_list[e][axis] >= median:
            middle = e
            break
    
    if middle is -1:
        print("Did not find a split point for list")
    else:
        left = full_list[0:middle]
        right = full_list[middle:len(full_list)]
    
    return (left, right)

#given k = 2
k = 2
#function for building a KDTree
def kdTree(points, level=0):
    dim = level % k
    axis = points[0].dtype.names[dim]
    median = (np.sort(points, order=axis)[len(points)-1][axis] +
              np.sort(points, order=axis)[0][axis]) / 2
    node = kdNode()
    node.value = median
    split_list = splitList(points, median, axis)
    left_points = split_list[0]
    if len(left_points) == 1:
        node.left = kdLeaf()
        node.left.value = left_points[0]
    else:
        node.left = kdTree(left_points, level+1)
    right_points = split_list[1]
    if len(right_points) == 1:
        node.right = kdLeaf()
        node.right.value = right_points[0]
    else:
        node.right = kdTree(right_points, level+1)
    
    return node

tree = kdTree(all_points)

#range search implementation
looked_at = []
def rangeSearch(node, rec, level=0):
    result = []
    dim = level % k
    
    if type(node) is kdLeaf:
        looked_at.append(node.value)
        if rec[0][0] <= node.value['x'] and rec[0][1] >= node.value['x']:
            if rec[1][0] <= node.value['y'] and rec[1][1] >= node.value['y']:
                result.append(node.value)
    else:
        if node.value > rec[dim][1]:
            left = rangeSearch(node.left, rec, level+1)
            for e in left:
                result.append(e)
        elif node.value < rec[dim][0]:
            right = rangeSearch(node.right, rec, level+1)
            for e in right:
                result.append(e)
        else:
            left = rangeSearch(node.left, rec, level+1)
            right = rangeSearch(node.right, rec, level+1)
            for e in left:
                result.append(e)
            for e in right:
                result.append(e)
    
    return result

start_kd = time.time()
kd_result = rangeSearch(tree, rec)
end_kd = time.time()
print("KDTree result in " + str((end_kd-start_kd)) + " seconds")

speedup = (end_naive-start_naive) / (end_kd-start_kd)
print("")
print("The kd-approach is " + str(speedup) + " times faster!")
print("")

#print("naive result:")
#print(naive_result)

#print("kd result:")
#print(kd_result)

#check if results are the same
same = True
naive_result = np.sort(naive_result)
kd_result = np.sort(kd_result)
if len(kd_result) == len(naive_result):
    for i in range(len(kd_result)):
        if kd_result[i][0] != naive_result[i][0]:
            same = False
            break
        if kd_result[i][1] != naive_result[i][1]:
            same = False
            break
else:
    same = False
if same:
    print("The results are the same!")
else:
    print("There is a difference between the two results...")

px_values = []
py_values = []
for p in all_points:
        px_values.append(p[0])
        py_values.append(p[1])

looked_x = []
looked_y = []
for p in looked_at:
    looked_x.append(p[0])
    looked_y.append(p[1])

result_x = []
result_y = []
for p in kd_result:
    result_x.append(p[0])
    result_y.append(p[1])

plt.scatter(px_values, py_values, c='blue', s=80, zorder=10)
plt.scatter(looked_x, looked_y, c='yellow', s=80, zorder=10)
plt.scatter(result_x, result_y, c='green', s=80, zorder=10)
plt.plot([rec[0][0], rec[0][1], rec[0][1], rec[0][0], rec[0][0]],
         [rec[1][0], rec[1][0], rec[1][1], rec[1][1], rec[1][0]], 'red')

#test for dataset3
#plt.plot([232,232], [-300, 1000], 'orange')
#plt.plot([232,700], [361, 361], 'green')#right
#plt.plot([-200,232], [345, 345], 'green')#left
#plt.plot([502,502], [361, 1000], 'brown')#right-right
#plt.plot([462,462], [-300, 361], 'brown')#right-left
#plt.plot([32,32], [345, 1000], 'brown')#left-right
#plt.plot([232,462], [72, 72], 'yellow')#right-left-left
#plt.plot([32,232], [762, 762], 'yellow')#left-right-right
#plt.plot([-200,32], [722, 722], 'yellow')#left-right-left
