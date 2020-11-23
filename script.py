from skimage import io, feature
from skimage.filters.edges import convolve
import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow
from skimage.transform import resize
from skimage.transform import hough_line
from skimage import morphology
import numpy as np
from numpy import array
import scipy
import math

class point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    def distance(self ,other):
        a=self.x - other.x
        b=self.y - other.y
        return math.sqrt(a*a+b*b)
class shape:
    def __init__(self):
        self.points=[]
        self.NW=point(1000000, 1000000)
        self.center=point()
        self.SE=point(-1,-1)
        self.x_val=0;
        self.y_val=0;
        self.sq_factor=0
    def contains(self, p):
        if(self.NW.x < p.x and self.NW.y < p.y and self.SE.x > p.x and self.SE.y > p.y):
            return True
        return False
    def overlap(self, other):
        if(self.SE.x < other.NW.x or self.NW.x > other.SE.x or self.NW.y > other.SE.y or self.SE.y < other.NW.y):
            return False
        return True

def find_consistent_shapes(img):
    SE = point(len(img[0]), len(img))
    shapes=[]
    for y in range(SE.y):
        for x in range(SE.x):
            stack = [point(x, y)]
            s = shape()
            while(len(stack) > 0):
                p = stack.pop()
                if(p.x < 0 or p.y < 0 or p.x >= SE.x or p.y >= SE.y):
                    continue
                if(img[p.y][p.x] == 1):
                    img[p.y][p.x] = 0
                    s.points.append(p)
                    if(p.x < s.NW.x):
                        s.NW.x = p.x
                    if(p.y < s.NW.y):
                        s.NW.y = p.y
                    if(p.x > s.SE.x):
                        s.SE.x = p.x
                    if(p.y > s.SE.y):
                        s.SE.y = p.y
                    stack.append(point(p.x, p.y-1))
                    stack.append(point(p.x, p.y+1))
                    stack.append(point(p.x-1, p.y))
                    stack.append(point(p.x-1, p.y-1))
                    stack.append(point(p.x-1, p.y+1))
                    stack.append(point(p.x+1, p.y))
                    stack.append(point(p.x+1, p.y-1))
                    stack.append(point(p.x+1, p.y+1))
            if(len(s.points) > 1):
                s.center.x = (s.NW.x + s.SE.x)/2
                s.center.y = (s.NW.y + s.SE.y)/2
                s.x_val=s.SE.x-s.NW.x
                s.y_val=s.SE.y-s.NW.y
                if(s.x_val * s.y_val < 1):
                    continue
                if s.x_val > s.y_val:
                    s.sq_factor = s.y_val/s.x_val
                else:
                    s.sq_factor = s.x_val/s.y_val
                shapes.append(s)
    return shapes

def find_frame(shapes):
    min_badness=1.0;
    result=shape()
    for i in range(len(shapes)):
        pivot = shapes[i]
        insiders = [shapes[j] for j in range(len(shapes)) if i != j and pivot.contains(shapes[j].NW) and pivot.contains(shapes[j].SE)]
        if(len(insiders) == 0):
            continue
        r = (pivot.x_val + pivot.y_val)/4
        badness=0
        for hour in range(12):
            crit_point = point(pivot.center.x+math.cos(hour*math.pi/6)*r, pivot.center.y+math.sin(hour*math.pi/6)*r)
            badness = badness + min([crit_point.distance(insider.center) for insider in insiders])/r
        badness=badness/12
        if(badness < min_badness):
            min_badness = badness
            result = pivot
    return result

def find_tips(shapes, frame):
    tips = shape()
    for s in shapes:
        if s.contains(frame.center) and frame.contains(s.NW) and frame.contains(s.SE):
            tips.points.extend(s.points)
    return tips
    

def paint_shape(img, s, val=(1.0,0,0)):
    for p in s.points:
        img[p.y][p.x] = val
        
def mark_shape(img, s, val=(1.0,0,0)):
    for y in (s.NW.y, s.SE.y):
        for x in range(s.NW.x, s.SE.x):
            img[y][x]=val
    for x in (s.NW.x, s.SE.x):
        for y in range(s.NW.y, s.SE.y):
            img[y][x]=val

imgs=[]
for i in range(1,19):
    imgs.append(io.imread('data/' + str(i) + '.jpg', as_gray=True))

for i in range(len(imgs)):
    imgs[i]=feature.canny(imgs[i], 1, low_threshold = 0.1, high_threshold= 0.3)
    fig = plt.figure(figsize=(len(imgs[i][0])/100,len(imgs[i])/100))
    #imgs[i]=morphology.binary_dilation(imgs[i])
    #imgs[i]=morphology.binary_erosion(imgs[i])
    shapes = find_consistent_shapes(imgs[i].copy())
    #do rgb
    imgs[i] = [[(float(v),float(v),float(v)) for v in line]for line in imgs[i]]
    #for s in shapes:
        #mark_shape(imgs[i], s)
    frame = find_frame(shapes)
    mark_shape(imgs[i], frame)
    tips = find_tips(shapes, frame)
    paint_shape(imgs[i], tips)
    #imshow(np.log(1 + h),
    #         extent=[np.rad2deg(theta[-1]), np.rad2deg(theta[0]), d[-1], d[0]],
    #         cmap='gray', aspect=1/1.5)
    imshow(imgs[i])
    fig.savefig("result/" + str(i)+".png")
