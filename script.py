from skimage import io, feature
from skimage.filters.edges import convolve
import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow
from skimage.transform import resize
from skimage.transform import hough_line
import numpy as np
from numpy import array
import scipy
import math
from PIL import Image, ImageDraw

def dfs(img, stack, lightpiexels):
    maxX = len(img[0])
    maxY = len(img)

    while(len(stack) > 0):
        P = stack.pop()
        img[P[1]][P[0]] = 0
        lightpiexels.append(P)
        if(P[0] - 1 > 0):
            if(img[P[1]][P[0]-1] >= 0.5):
                stack.append([P[0]-1,P[1]])         
        if(P[1] - 1 > 0):
            if(img[P[1]-1][P[0]] >= 0.5):
                stack.append([P[0],P[1]-1])
        if(P[0] + 1 < maxX):
            if(img[P[1]][P[0]+1] >= 0.5):
                stack.append([P[0]+1,P[1]])
        if(P[1] + 1 < maxY):
            if(img[P[1]+1][P[0]] >= 0.5):
                stack.append([P[0],P[1]+1])
        if(P[0] - 1 > 0 and P[1] - 1 > 0):
            if(img[P[1]-1][P[0]-1] >= 0.5):
                stack.append([P[0]-1,P[1]-1])         
        if(P[0] - 1 > 0 and P[1] + 1 < maxY):
            if(img[P[1]+1][P[0]-1] >= 0.5):
                stack.append([P[0]-1,P[1]+1]) 
        if(P[0] + 1 < maxX and P[1] - 1 > 0):
            if(img[P[1]-1][P[0]+1] >= 0.5):
                stack.append([P[0]+1,P[1]-1])
        if(P[0] + 1 < maxX and P[1] + 1 < maxY):
            if(img[P[1]+1][P[0]+1] >= 0.5):
                stack.append([P[0]+1,P[1]+1])        





def smallObjects(img):
    res = []
    maxX = len(img[0])
    maxY = len(img)
    i = 0
    pointerX = i % maxX
    pointerY = i // maxX
    while(i < maxX * maxY):
        while(i < maxX * maxY and img[pointerY][pointerX] < 0.5):
            pointerX = i % maxX
            pointerY = i // maxX
            i = i+1
        lightpiexels = []
        stack = []
        stack.append([pointerX, pointerY])
        dfs(img, stack, lightpiexels)
        Xs = np.transpose(lightpiexels)[0]
        Ys = np.transpose(lightpiexels)[1]

        if(len(Xs) > 10 * len(img) or max(Xs)-min(Xs) > maxX / 10 or max(Ys)-min(Ys) > maxY / 10):
           continue
        res.append([np.median(Xs), np.median(Ys)])
    return res

def minimalizationPoint(points, sizeX, sizeY, step = 10):
    di = {}

    Xs = np.transpose(points)[0]
    Ys = np.transpose(points)[1]

    XM = np.median(Xs)
    YM = np.median(Ys)

    points = sorted(points, key= lambda ele: (ele[0]-XM)**2 + (ele[1]-YM)**2)
    points = points[:(len(points)*9)//10]

    for radius in range(int(min(sizeX, sizeY)/8), int(min(sizeX, sizeY)/2), step):
        for i in range(0, sizeX, step):
            for j in range(0, sizeY, step):
                v = 0
                for p in points:
                    odl = math.sqrt((i-p[0])*(i-p[0]) + (j-p[1])*(j-p[1]))
                    if(odl > radius*0.2 and odl < radius):
                        v+=1
                if(v > 0.7 * len(points)):        
                    di[v/radius**2] = (np.array([i,j]), radius)

    di = sorted(di.items(), key = lambda ele: ele[0], reverse=True)
    return di[0][1]


imgs=[]
for i in range(1,15):
    imgs.append(io.imread('data/' + str(i) + '.jpg', as_gray=True))

for i in range(len(imgs)):
    imgs[i]=feature.canny(imgs[i], 1, low_threshold = 0.25, high_threshold= 0.75)

    fig = plt.figure(figsize=(16,16))
    
    imgs[i]=[[float(pixel) for pixel in line] for line in imgs[i]]
    #imgs[i]=scipy.ndimage.gaussian_filter(imgs[i], sigma=1)
    points = smallObjects(imgs[i])



    #for P in points:
    #    imgs[i][int(P[1])][int(P[0])] = 1.0
    
    pos, r = minimalizationPoint(points, len(imgs[0][0]), len(imgs[0]), 20)
    xx, yy = np.mgrid[:len(imgs[0][0]), :len(imgs[0])]

    imgs[i] = io.imread('data/' + str(i+1) + '.jpg', as_gray=True)
    imgs[i]=feature.canny(imgs[i], 1, low_threshold = 0.25, high_threshold= 0.75)
    imgs[i]=[[float(pixel) for pixel in line] for line in imgs[i]]
    #imgs[i]=scipy.ndimage.gaussian_filter(imgs[i], sigma=1)

    circle = (xx - pos[0]) ** 2 + (yy - pos[1]) ** 2

    for a in range(len(imgs[0][0])):
        for b in range(len(imgs[0])):
            if(circle[a][b] < (r/4)**2 and circle[a][b] > (r/5)**2):
                imgs[i][b][a] = 1.0

    for a in range(pos[0],pos[0]+20):
        for b in range(pos[1], pos[1]+20):
            imgs[i][b][a] = 0
  
    imshow(imgs[i], cmap='gray')
    fig.savefig(str(i)+".png")








#h, theta, d = hough_line(imgs[i])

#imgs[i]=scipy.ndimage.gaussian_filter(imgs[i], sigma=5)
#res=[[ lol(imgs[i], (x,y)) for x in range(0,len(imgs[i][0]),5)] for y in range(0,len(imgs[i]),5)]