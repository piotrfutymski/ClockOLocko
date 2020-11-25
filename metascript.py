from skimage import io as ios
from hour_computing import calculate_hour
from skimage.transform import rescale
import sys
import io
import copy

def getQuality(times, params = [3.6, 1.59, 1.11, 1.6, 0.225, 0.9, 35, 120, 0.325, 0.175, 0.21, 0.48], scale = 1):
    v = 0
    for i in range(0 , len(times)):
        img = ios.imread("data/"+str(i)+".jpg", as_gray=True)
        img = rescale(img, scale, anti_aliasing=True)
        hour, minutes = calculate_hour(img, params=params)
        #print(str(hour)+":"+str(minutes))
        if(hour == times[i][0] and abs(minutes - times[i][1])<=2):
            v = v + 1000 - abs(minutes - times[i][1])
    return v/len(times)

times = []
for line in io.open("data/info.txt", "r"):
    times.append(tuple(int(x) for x in line.split()))

params = [4.3, 1.7, 1.09, 2.02, 0.24, 1.13, 35, 129, 0.375, 0.175, 0.21, 0.494]
deltas = [0.05, 0.02, 0.02, 0.01, 0.005, 0.03, 1, 1, 0.01, 0.01, 0.001, 0.001]
signs = [1, -1, -1, 1, 1, 1, -1, 1, 1, 1, 1, 1]

old = getQuality(times, params=params)


while(True):
    for i in range (0, len(params)):
        if(i == 5 or i == 7):
            continue
        testparams = copy.copy(params)
        testparams[i] = testparams[i] + deltas[i]*signs[i]
        quality = getQuality(times, testparams)
        if(quality >= old):
            old = quality
            params[i] = testparams[i]
            print(params)
            print(old)
        else:
            signs[i] = signs[i] * (-1)