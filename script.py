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
import copy

def paint_pixel(img, x, y, val):
    SE = point(len(img[0]), len(img))
    if(x - 1 >=0 and y-1 >=0 and x+1 < SE.x and y+1 < SE.y):
        img[y][x] = val

class point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def distance(self ,other):
        a=self.x - other.x
        b=self.y - other.y
        return math.sqrt(a*a+b*b)

    def paint(self, img, val=(0,1.0,0), master = 1):
        for offx in (-1,0,1):
            for offy in (-1,0,1):
                paint_pixel(img, int(self.x)+offx, int(self.y)+offy, val)

class rectangle:
    def __init__(self):
        self.NW=point(1000000, 1000000)
        self.center=point()
        self.SE=point(-1,-1)
        self.x_val=0
        self.y_val=0
    
    def contains(self, p):
        if(self.NW.x < p.x and self.NW.y < p.y and self.SE.x > p.x and self.SE.y > p.y):
            return True
        return False 

    def resize(self, prop):
        w = prop * (self.SE.x - self.NW.x)/2
        h = prop * (self.SE.y - self.NW.y)/2
        self.NW.x = self.center.x - w
        self.NW.y = self.center.y - h
        self.SE.x = self.center.x + w
        self.SE.y = self.center.y + h
        self.center = self.center
        self.x_val = 2*w
        self.y_val = 2*h


    def paint(self, img, val=(1.0,0,0)):
        for y in (int(self.NW.y), int(self.NW.y)-1, int(self.SE.y), int(self.SE.y)-1):
            for x in range(int(self.NW.x), int(self.SE.x)):
                paint_pixel(img, x, y, val)
        for x in (int(self.NW.x), int(self.NW.x)-1, int(self.SE.x), int(self.SE.x)-1):
            for y in range(int(self.NW.y), int(self.SE.y)):
                paint_pixel(img, x, y, val)


class shape:
    def __init__(self):
        self.points = []
        self.frame = rectangle()
        self.masscenter = point()
        self.square = False

    def any_in(self, other):       # self - shape other - rectangle
        for p in self.points:
            if(other.contains(p)):
                return True
        return False  
    
    def update(self):
        self.square = False
        self.frame.NW=point(1000000, 1000000)
        self.frame.SE=point(-1,-1)
        sumX = 0
        sumY = 0
        for p in self.points:
            sumX += p.x
            sumY += p.y
            if(p.x < self.frame.NW.x):
                self.frame.NW.x = p.x
            if(p.y < self.frame.NW.y):
                self.frame.NW.y = p.y
            if(p.x > self.frame.SE.x):
                self.frame.SE.x = p.x
            if(p.y > self.frame.SE.y):
                self.frame.SE.y = p.y

        self.masscenter.x = sumX/len(self.points)
        self.masscenter.y = sumY/len(self.points)

        self.frame.center.x = (self.frame.NW.x + self.frame.SE.x)/2
        self.frame.center.y = (self.frame.NW.y + self.frame.SE.y)/2
        self.frame.x_val=self.frame.SE.x-self.frame.NW.x
        self.frame.y_val=self.frame.SE.y-self.frame.NW.y

    def paint(self, img, val=(1.0,0,0)):
        for p in self.points:
            img[p.y][p.x] = val


def find_consistent_shapes(img):
    img = copy.deepcopy(img)
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
                    stack.append(point(p.x, p.y-1))
                    stack.append(point(p.x, p.y+1))
                    stack.append(point(p.x-1, p.y))
                    stack.append(point(p.x-1, p.y-1))
                    stack.append(point(p.x-1, p.y+1))
                    stack.append(point(p.x+1, p.y))
                    stack.append(point(p.x+1, p.y-1))
                    stack.append(point(p.x+1, p.y+1))
            if(len(s.points) > 10):
                s.update()
                if(s.frame.x_val * s.frame.y_val > 0.005 * SE.x * SE.y):
                    makeSquare(s, SE)
                shapes.append(s)  
    return shapes

def makeSquare(s, SE):
    if s.frame.x_val > s.frame.y_val:
        d = s.frame.x_val - s.frame.y_val
        if(s.masscenter.y < s.frame.center.y):
            s.frame.SE.y = min(s.frame.SE.y + d, SE.y-1)
        else:
            s.frame.NW.y = max(s.frame.NW.y - d, 0)
        s.frame.center.y = (s.frame.NW.y + s.frame.SE.y)/2
    else:
        d = s.frame.y_val - s.frame.x_val
        if(s.masscenter.x < s.frame.center.x):
            s.frame.SE.x = min(s.frame.SE.x + d, SE.x-1)
        else:
            s.frame.NW.x = max(s.frame.NW.x - d, 0)
        s.frame.center.x = (s.frame.NW.x + s.frame.SE.x)/2
    s.frame.x_val=s.frame.SE.x-s.frame.NW.x
    s.frame.y_val=s.frame.SE.y-s.frame.NW.y
    s.square = True    


def find_clock(shapes):
    min_badness=1.0
    result=shape()
    for i in range(len(shapes)):
        pivot = shapes[i]
        insiders = [shapes[j] for j in range(len(shapes)) if i != j and pivot.frame.contains(shapes[j].frame.NW) and pivot.frame.contains(shapes[j].frame.SE)]
        if(len(insiders) == 0):
            continue
        r = (pivot.frame.x_val + pivot.frame.y_val)/4
        badness=0
        for hour in range(12):
            crit_point = point(pivot.frame.center.x+math.cos(hour*math.pi/6)*r, pivot.frame.center.y+math.sin(hour*math.pi/6)*r)
            badness = badness + min([crit_point.distance(insider.frame.center) for insider in insiders])/r
        badness=badness/12
        if(badness < min_badness):
            min_badness = badness
            result = copy.deepcopy(pivot)
    if(len(result.points) == 0):
        raise Exception('Nie znaleziono tarczy!')
    return result

def find_tips(shapes, clock):
    tips = shape()
    a = copy.deepcopy(clock.frame)
    a.resize(0.2)
    for s in shapes:
        if s.any_in(a):        
            tips.points.extend(s.points)

    if(len(tips.points) > 0):       
        tips.update()
    else:
        raise Exception('Nie znaleziono wskazowek!')
    return tips
    

def find_center(tips, clock):
    region = copy.deepcopy(clock.frame)
    region.resize(0.3)

    tips_center = [t for t in tips.points if region.contains(t)]
    
    current_approx = clock.frame.center
    prev_approx= point()
    prev_val=0
    for t in tips_center:
        w = (current_approx.x - t.x)
        h = (current_approx.y - t.y)
        prev_val += w*w + h*h
    
    while (current_approx.x != prev_approx.x) or (current_approx.y != prev_approx.y):
        prev_approx = copy.deepcopy(current_approx)
        for direction in (point(1,0), point(-1,0), point(0,1), point(0, -1)):
            tmp =prev_approx
            tmp.x = tmp.x + direction.x
            tmp.y = tmp.y + direction.y
            if(not region.contains(tmp)):
                continue
            current_val=0
            for t in tips_center:
                w = (tmp.x - t.x)
                h = (tmp.y - t.y)
                current_val = current_val + w*w + h*h
            if(current_val < prev_val):
                prev_val = current_val
                current_approx = copy.deepcopy(tmp)
    return current_approx
        
        


def alfa_cp(C, P):
    if(C.x == P.x):
        if(P.y > C.y):
            return math.pi
        else:
            return 0
    elif(C.y == P.y):
        if(P.x > C.x):
            return math.pi/2
        else:
            return 3*math.pi/2
    else:
        W = abs(P.x - C.x)
        H = abs(P.y - C.y)
        if(P.x > C.x and P.y < C.y):
            return math.atan(W/H)
        elif(P.x > C.x and P.y > C.y):
            return math.pi/2 + math.atan(H/W)
        elif(P.x < C.x and P.y > C.y):
            return math.pi + math.atan(W/H)
        else:
            return 3*math.pi/2 + math.atan(H/W)

def find_angles(tips, C, A, step = 3):
    di = {}
    angles = []
    for tt in range(0, 360, step):
        di[tt] = 0

    for t in tips.points:
        for tt in range(0, 360, step):
            theta = tt *math.pi/180
            beta = abs(theta - alfa_cp(C, t))
            if(beta < math.pi/2 and C.distance(t) > A*0.2 and C.distance(t)*math.sin(beta) < A/40):
                di[tt] += 1

    last = -1
    nextt = True

    for tt in range(0, 360, step):
        if(di[tt] > last):
            last = di[tt]
            nextt = True
        else:
            if(nextt == True):
                angles.append((tt-step))
                nextt = False
            last = di[tt]

    angles.sort( key = lambda el: di[el], reverse=True)
    for i in range(min(len(angles),5)):
        angles[i] = angles[i]/30
    return angles[0:min(len(angles),5)]

def get_hour(angles):
    di = []

    for i in range(len(angles)):
        prM = angles[i]/12
        n = -1
        h = 100000
        for j in range(len(angles)):
            if(i == j):
                continue
            od = (angles[j] - int(angles[j]) - prM)*(j+1)**5
            if(abs(od) < abs(h) ):
                h = od
                n = j
        di.append((n, i, h/(n+1)**5))
    
    di.sort(key= lambda el: el[0]+el[1])
    hours = int(angles[di[0][0]])
    #print(di[0][2])
    if( di[0][2] > 0.5):
        hours = hours + 1
    elif(di[0][2] < -0.5):
        hours = hours - 1
    
    if(hours == -1):
        hours = 11
    if(hours == 0):
        hours = 12

    return hours, int(angles[di[0][1]]*5)
        



imgs=[]
for i in range(1,19):
    imgs.append(io.imread('data/' + str(i) + '.jpg', as_gray=True))

for i in range(len(imgs)):
    print('ZEGAR ' + str(i))
    imgs[i]=feature.canny(imgs[i], 1, low_threshold = 0.15, high_threshold= 0.3)
    fig = plt.figure(figsize=(len(imgs[i][0])/100,len(imgs[i])/100))

    shapes = find_consistent_shapes(imgs[i])
    #do rgb
    imgs[i] = [[(float(v),float(v),float(v)) for v in line]for line in imgs[i]]
    try:
        clock = find_clock(shapes)
        tips = find_tips(shapes, clock)
    except Exception as e:
        print(e)
        continue
    center = find_center(tips, clock)

    angles =  find_angles(tips, center, clock.frame.x_val)
    #for angle in angles:
       #print(str(i) + ":\t" + str(angle))

    hour, mintues = get_hour(angles)
    print(str(hour)+":"+str(mintues))
    print()
    
    clock.frame.paint(imgs[i])
    tips.paint(imgs[i])
    center.paint(imgs[i])

    imshow(imgs[i])
    fig.savefig("result/" + str(i)+".png")
