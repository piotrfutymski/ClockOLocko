from skimage import io, feature
import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow
from skimage.transform import resize
import numpy as np
import scipy
import math
import copy
import sys
import hour_computing

for i in range(1, len(sys.argv)):
    print('ZEGAR ' + sys.argv[i])
    img = io.imread(sys.argv[i], as_gray=True)
    succes = False
    state = 0
    while(succes == False):        
        emg = []
        if(state == 0):
            emg = feature.canny(img, 1, low_threshold = 0.18, high_threshold= 0.4)
        else:
            emg = feature.canny(img, 1, low_threshold = 0.11, high_threshold= 0.18)
        
        fig = plt.figure(figsize=(len(emg[0])/100,len(emg)/100))
        shapes = hour_computing.find_consistent_shapes(emg)
        emg = [[(float(v),float(v),float(v)) for v in line]for line in emg]
        try:
            clock = hour_computing.find_clock(shapes)
            tips = hour_computing.find_tips(shapes, clock)
            center = hour_computing.find_center(tips, clock)
            angles =  hour_computing.find_angles(tips, center, clock.frame.x_val)
            hour, mintues = hour_computing.get_hour(angles)
            print(str(hour)+":"+str(mintues))
            clock.frame.paint(emg)
            tips.paint(emg)
            center.paint(emg)

            imshow(emg)
            fig.savefig("result/" + str(i)+".png")
            succes = True
        except Exception as e:
            print(e)
            if(state == 0):
                print("Ponawiam próbę")
                state = 1
            else:
                print("Nie wykryto zegara, kończenie")
                state = 0
                succes = True
