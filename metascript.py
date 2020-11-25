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
            v = v + 1
    return v/len(times)

times = []
for line in io.open("data/info.txt", "r"):
    times.append(tuple(int(x) for x in line.split()))

params = [3.6, 1.59, 1.11, 1.6, 0.225, 0.9, 35, 120, 0.325, 0.175, 0.21, 0.48]
deltas = [0.2, 0.1, 0.1, 0.1, 0.02, 0.05, 3, 3, 0.02, 0.02, 0.01, 0.02]
bests = []

old = getQuality(times)

for i in range (6, len(params)):
    n = 5
    maxi = old
    for j in range(0,11):
        if(j != 5):
            value = params[i]+(j-5)*deltas[i]
            testparams = copy.copy(params)
            quality = getQuality(times, testparams)
            print("Param no. " + str(i) + " test value: " + str(value) +"  result: "+str(quality))
            if(quality > maxi):
                n = j
                maxi = quality
    bests.append(params[i]+(n-5)*deltas[i])

print(bests)