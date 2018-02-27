# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 23:37:22 2018

@author: GUARIND
"""
#%%
import cv2
import numpy as np 
import time
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from sklearn.decomposition import PCA

#read gray image
path_frames = r'C:\Users\GUARIND\Videos\Basler\test1'
image1 = 'Basler acA800-510uc (22501173)_20171212_190308266_0015.tiff'
frame =  cv2.imread(path_frames + '/' + image1, 0)

#increase size, this will allow to detect the face countour separated form the actual face countour. 
new_frame = cv2.resize(frame, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_LINEAR)
h,w = frame.shape
n_h,n_w = new_frame.shape
delta_h = int((n_h-h)/2)
delta_w = int((n_w-w)/2)

#reshape the image to have the original size. The resulting image is the rat face with some magnification. 
temp = new_frame[delta_h:h+delta_h,delta_w:w+delta_w]


#dilate to remove whiskers and other small objects
kernel = np.ones((9,9), np.uint8)
im1 = cv2.dilate(temp,kernel,iterations=1)
#apply threshold so that only the face is selected. I used the mean brightness value
th,_,_,_ = cv2.mean(im1)
im1[im1>np.ceil(th)] = 255
im1[im1<255] = 0 

#now we have an image on 255 (white) and 0 (black) with the face countour, all small details where removed 
#apply canny filter to detect edges
edges = cv2.Canny(im1,50,100)

#plot results
cv2.namedWindow("Video3", cv2.WINDOW_NORMAL+cv2.WINDOW_KEEPRATIO)
cv2.imshow("Video3",frame | edges)

#now work on each side of the image 
#start with the right and then left 
center = [400,320]

right = frame.copy()
right = right[:,0:center[0]]
edges_right = edges.copy()
edges_right = edges_right[:,0:center[0]]

#now, treat the facial edges as a time series, the top-left corner of the image is (0,0). 'y' increases down and 'x' increases to the right
#find the position of the edge for each value of 'y'
ED_right = np.zeros([h,2])
for k in range(0,h):
    temp =np.where(edges[k,:]==255)[0] #find the 'x' position of the edge for each value of 'y'. If there is no edge then this function returns and empty vector
    if temp.size:
        if temp[0] == 0:
            k=k-1
            break
        else:
            ED_right[k,0] = np.where(edges[k,:]==255)[0][0]
    else:
        k=k-1
        break
            
#now smooth the edge, this will help to eliminate large gaps in the edge
#i'll use the Savitzky–Golay filter, that computes a polynomial using a sub-set of points in the data set 
ED_right[0:k,0] = savgol_filter(ED_right[0:k,0],7,3,0)
#as a bonus, comput the first derivative of the edge using the same procedure 
ED_right[0:k,1] = savgol_filter(ED_right[0:k,0],7,3,1)
plt.plot(range(0,h),ED_right)
