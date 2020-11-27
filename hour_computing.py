from skimage import io, feature
import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow
from skimage.transform import resize
import numpy as np
import scipy
import math
import copy
import sys

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
        insiders = [shapes[j] for j in range(len(shapes)) if i != j and pivot.frame.contains(shapes[j].frame.NW) and pivot.frame.contains(shapes[j].frame.SE) and len(shapes[j].points) > pivot.frame.x_val/10]
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
def find_tips(shapes, clock, p0 = 0.175):
    tips = shape()
    a = copy.deepcopy(clock.frame)
    a.resize(p0)
    for s in shapes:
        if s.any_in(a):        
            tips.points.extend(s.points)

    if(len(tips.points) > 0):       
        tips.update()
    else:
        raise Exception('Nie znaleziono wskazowek!')
    return tips
    
def find_center(tips, clock, p0 = 0.325):
    return clock.frame.center

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
def find_angles(tips, C, A, step = 6, p0 =0.22, p1=35):
    di = {}
    angles = []
    for tt in range(0, 360, step):
        di[tt] = 0

    for t in tips.points:
        for tt in range(0, 360, step):
            theta = tt *math.pi/180
            beta = abs(theta - alfa_cp(C, t))
            odl = C.distance(t)
            odch = abs(odl*math.sin(beta))          
            if(beta < math.pi/2 and (odl > A*p0  and odch < A/p1)):
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

def get_hour(angles, p0=4.6, p1=1.7, p2=1.09):
    di = []

    for i in range(len(angles)):
        prM = angles[i]/12
        for j in range(len(angles)):
            if(i == j):
                continue
            od = (angles[j] - int(angles[j]) - prM)
            k = 0.5 - abs(abs(od) - 0.5)
            k = p0 * k + i*p1 + j*p2
            hours = int(angles[j])
            if(od > 0.5):
                hours = hours + 1
            elif(od < -0.5):
                hours = hours - 1
            if(hours == -1):
                hours = 11
            if(hours == 0):
                hours = 12
            minutes = int(angles[i]*5)         
            di.append((hours, minutes, k))
    
    di.sort(key= lambda el: el[2])

    if(len(di) == 0):
        raise Exception('Nie znaleziono kątów wskazówek!')

    return di[0][0], di[0][1]


def calculate_hour(img):
    state = 0
    while(True):
        emg = []
        if(state == 0):
            emg = feature.canny(img, 1, low_threshold = 0.21, high_threshold= 0.494)
        else:
            emg = feature.canny(img, 1, low_threshold = 0.11, high_threshold= 0.18)
        shapes = find_consistent_shapes(emg)        
        try:
            clock = find_clock(shapes)
            tips = find_tips(shapes, clock)
            center = find_center(tips, clock)
            angles =  find_angles(tips, center, clock.frame.x_val)
            hour, mintues = get_hour(angles)
            return hour, mintues
        except Exception as e:
            if(state == 0):
                state = 1
            else:
                return -1, 0