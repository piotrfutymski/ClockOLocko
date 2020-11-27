from skimage import io as ios
from hour_computing import calculate_hour
from skimage.transform import rescale
import sys
import io
import copy

def getQuality(times):
    v = 0
    for i in range(0 , len(times)):
        img = ios.imread("data/"+str(i)+".jpg", as_gray=True)
        hour, minutes = calculate_hour(img)
        print(str(hour)+":"+str(minutes)+"\ttrue: "+ str(times[i][0])+":"+ str(times[i][1]))
        if(hour == times[i][0] and abs(minutes - times[i][1])<=2):
            v = v + 1
    return v*100/len(times)

times = []
for line in io.open("data/info.txt", "r"):
    times.append(tuple(int(x) for x in line.split()))

old = getQuality(times)
print(old)

