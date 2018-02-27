# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 23:37:22 2018

@author: GUARIND
"""

import cv2
import numpy as np 
import time
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter, medfilt
from sklearn.decomposition import PCA



st = time.time()

#read gray image
path_frames = r'C:\Users\GUARIND\Videos\Basler\test1'
image1 = 'Basler acA800-510uc (22501173)_20171212_190308266_0015.tiff'
frame =  cv2.imread(path_frames + '/' + image1, 0)
#frame[frame>90]=255
h,w = frame.shape

#dilate to remove whiskers and other small objects
kernel = np.ones((11,11), np.uint8)
im1 = cv2.dilate(frame,kernel,iterations=1)
#apply threshold so that only the face is selected. I used the mean brightness value
th,_,_,_ = cv2.mean(im1)
im1[im1>np.ceil(th)] = 255
im1[im1<255] = 0 

#now we have an image on 255 (white) and 0 (black) with the face countour, all small details where removed 
#apply a LARGE Gaussian filter to "smooth" the transition between face/no-face
im1 = cv2.GaussianBlur(im1,(13,13),0)

#apply canny filter to detect edges
edges = cv2.Canny(im1,50,100)

#now work on each side of the image 
#start with the right and then left 
center = [400,320]

right = frame.copy()
right = right[:,0:center[0]]
edges_right = edges.copy()
edges_right = edges_right[:,0:center[0]]

#move the edge away from the face so that small hairs are not detected

newEdges = np.zeros(edges_right.shape,dtype = np.uint8)
newEdges[:,0:-18] = edges_right[:,18:]
#newEdges[:,18:] = edges_right[:,0:-18]
cv2.imshow("image",right | newEdges)



##now, treat the facial edges as a time series, the top-left corner of the image is (0,0). 'y' increases down and 'x' increases to the right
##find the position of the edge for each value of 'y'
ED_right = np.zeros([h,2])
for k in range(0,h):
    temp =np.where(newEdges[k,:]==255)[0] #find the 'x' position of the edge for each value of 'y'. If there is no edge then this function returns and empty vector
    if temp.size:
        if temp[0] == 0:
            k=k-1
            break
        else:
            ED_right[k,0] = temp[0]
    else:
        k=k-1
        break
            
###now smooth the edge, this will help to eliminate large gaps in the edge
###i'll use the Savitzky–Golay filter, that computes a polynomial using a sub-set of points in the data set 
##ED_right[0:k,0] = savgol_filter(ED_right[0:k,0],9,3,0)
###as a bonus, comput the first derivative of the edge using the same procedure 
##ED_right[0:k,1] = savgol_filter(ED_right[0:k,0],7,3,1)

EDGES = np.where(newEdges == 255);
#find the image pixel intensity around the selected face edge
#yval = EDGES[0]
yval = range(0,k)
yval = yval[::-1]
#round the numbers to its nearest int so that it can be used in the image
#xval = EDGES[1]#
xval = ED_right[0:k,0].astype(np.int)
xval = xval[::-1]
intensity = np.zeros([len(yval)])
new_EDGE = np.zeros(frame.shape,dtype = np.uint8)
for m in range(0,len(intensity)):
    intensity[m] = frame[yval[m],xval[m]]
    new_EDGE[yval[m],xval[m]]= 255
    
#plt.plot(range(0,len(intensity)),intensity)
#plot results
#cv2.namedWindow("Video3", cv2.WINDOW_NORMAL+cv2.WINDOW_KEEPRATIO)
#cv2.imshow("Video3",frame | new_EDGE)

#find possible places where a whisker crosses the edge, this is done by finding the pixels around the edge with intensity 
#lower than certain threshold. These pixels are called seeds and will be tested for the presence of a whisker. 
#We don't need to find all the whisker, but we need to make sure that every whisker detected is actually a whisker 
th_intensity = 95
seeds = np.where(intensity<th_intensity)[0] #this will be unnecesary if we properly remove the background
#remove the last 5 to 10 seeds, there probably won't be any whiskers at the end of the frame
seeds = seeds[0:-int(len(seeds)/4)]
#remove seeds that are too close to each other 
#seeds=[]  
#k=0  
#while k<len(temp)-1:
#    if abs(temp[k]-temp[k+1]) > 1:
#        seeds.append(temp[k])
#        k+=1
#    else:
#        k+=1
#get ride of seeds that are too close to each other, this is done selectively. 
#if there are three consecutive seeds, then choose the seed in the middle
#groups of three
ll=[]
m=0
while m < len(seeds)-2:
    group=[seeds[m], seeds[m+1], seeds[m+2]]
    if abs(group[0]-group[2]) == 2:
        ll.append(seeds[m+1])
        m+=3
    else:
        ll.append(seeds[m])
        m+=1

seeds = ll
#if there are two consecutive seeds, then choose one of them
ll=[]
m=0
while m < len(seeds)-1:
    group=[seeds[m], seeds[m+1]]
    if abs(group[0]-group[1]) == 1:
        ll.append(seeds[m+1])
        m+=2
    else:
        ll.append(seeds[m])
        m+=1
        
seeds = np.array([ll])
seeds= np.reshape(seeds, seeds.T.shape)

    
#now, every seed needs to be tested for the presence of a whisker, this will be done by selecting a 7x7
#matrix centered on the seed. Then, the local minima from every row and every column will be localized, if there is 
#a whisker then these local minimina should resemble a line, if not then they won't. The line-like quality of the 
#local minima will be quantified using a Pricipal-Component-Decomposition (PCA) of the dots. If the local 
#minima does resemble a line, then the principal axis of the data will be resemble an ellipse with a very small excentricity (>0.98)
m_size =7

#initialize the PCA object, this is rather slow...
pca = PCA(n_components=2)
framo = right.copy()
whiskers=[]
used_seeds = []
for seed in seeds:
    seed = seed[0]
    selected_area = frame[yval[seed]-int(m_size/2):yval[seed]+int(m_size/2)+1,xval[seed]-int(m_size/2):xval[seed]+int(m_size/2)+1].copy()
    
    
    #search for minima in each row, this will detect whiskers that are not horizontal (we don't care about horizonal whiskers, they don't add anything to the 
    #mean angle estimation)
    min_position = np.zeros([m_size])
    for m in range(0,m_size):
        min_position[m] = np.argmin(selected_area[m,:])
        
    if abs(min_position[int(m_size/2)]-int(m_size/2)) > 1:
        pass
    else:
    
        Data = np.c_[min_position-int(m_size/2),np.linspace(int(m_size/2),-int(m_size/2),m_size)]
        pca.fit(Data)
        
        
        c1 = pca.explained_variance_[0]
        c2 = pca.explained_variance_[1]
        if c1>=c2:
            major_axis = c1# np.sqrt(c1)
            minor_axis = c2#np.sqrt(c2)
        else:
            major_axis = c2#np.sqrt(c2)
            minor_axis = c1#np.sqrt(c1)
        
        exc= np.sqrt(1-(minor_axis/major_axis))
        
        vector = pca.components_[0]
        print(pca.mean_, pca.mean_+vector)
    
            
        angle = np.arctan(vector[1]/vector[0])
        print(angle*180/np.pi)
        #print(exc,vector,angle*180/np.pi)
        
        temp = int((vector[1]/vector[0])*yval[seed]+int(m_size/2))
        #print((xval[seed],yval[seed]),(temp,yval[seed]+int(m_size/2)))
        print(np.floor(major_axis*vector[1]))
        print((xval[seed],yval[seed]),(xval[seed],yval[seed])+(int(major_axis*vector[0]),int(major_axis*vector[1])) )
        cv2.imshow("Video3",selected_area)
        cv2.waitKey(0)
        
        
        if exc > 0.98: #we think this migth be a whisker, extend the search area to include a larger portion of the possible whisker 
            
            new_c = [int(xval[seed]+Data[-1,0]), int(yval[seed]+int(m_size/2))]
            new_area = frame[new_c[1]-int(m_size/2):new_c[1]+int(m_size/2)+1,new_c[0]-int(m_size/2):new_c[0]+int(m_size/2)+1].copy()
            min_position = np.zeros([m_size])
            for m in range(0,m_size):
                min_position[m] = np.argmin(new_area[m,:])
                
            Data2 = np.c_[min_position-int(m_size/2),np.linspace(int(m_size/2),-int(m_size/2),m_size)]
            pca.fit(Data2)
            
            
            c1 = pca.explained_variance_[0]
            c2 = pca.explained_variance_[1]
            if c1>=c2:
                major_axis = c1# np.sqrt(c1)
                minor_axis = c2#np.sqrt(c2)
            else:
                major_axis = c2#np.sqrt(c2)
                minor_axis = c1#np.sqrt(c1)
            
            exc2= np.sqrt(1-(minor_axis/major_axis))
            
            vector = pca.components_[0]
    
            
            angle = np.arctan(vector[1]/vector[0])
            print(2,angle*180/np.pi)
            
            if exc2 > 0.98: #this is a whisker :) Store its information 
                whiskers.append([[int(xval[seed]+Data[0,0]), int(yval[seed]-int(m_size/2))],[int(xval[seed]),
                                  int(yval[seed])],new_c,[int(new_c[0]+Data2[-1,0]), int(new_c[1]+int(m_size/2))]])
                used_seeds.append([seed])
    
                framo= cv2.line(framo, tuple(whiskers[-1][0]), tuple(whiskers[-1][-1]),[255,255,255],1)
                
            
            #print(exc)
#
##remove used seeds from list of seeds                
#used_seeds_index =   np.where(np.in1d(seeds,np.array([used_seeds])))
#seeds = np.delete(seeds,used_seeds_index)  
#for seed in seeds:
#    seed = seed
#    selected_area = frame[yval[seed]-int(m_size/2):yval[seed]+int(m_size/2)+1,xval[seed]-int(m_size/2):xval[seed]+int(m_size/2)+1].copy()
#    
#    
#    #search for minima in each row, this will detect whiskers that are not horizontal (we don't care about horizonal whiskers, they don't add anything to the 
#    #mean angle estimation)
#    min_position = np.zeros([m_size])
#    for m in range(0,m_size):
#        min_position[m] = np.argmin(selected_area[:,m])
#        
#    if abs(min_position[int(m_size/2)]-int(m_size/2)) > 1:
#        pass
#    else:
#    
#        Data = np.c_[np.linspace(int(m_size/2),-int(m_size/2),m_size), min_position-int(m_size/2)]
#        pca.fit(Data)
#        
#        
#        c1 = pca.explained_variance_[0]
#        c2 = pca.explained_variance_[1]
#        if c1>=c2:
#            major_axis = c1# np.sqrt(c1)
#            minor_axis = c2#np.sqrt(c2)
#        else:
#            major_axis = c2#np.sqrt(c2)
#            minor_axis = c1#np.sqrt(c1)
#        
#        exc= np.sqrt(1-(minor_axis/major_axis))
#        
#        #vector = pca.components_[0]
#    
#            
#        #angle = np.arctan(vector[1]/vector[0])
#        #print(Data)
#        #print(exc,vector,angle*180/np.pi)
#        #cv2.imshow("Video3",selected_area)
#        #cv2.waitKey(0)
#        
#        if exc > 0.98: #we think this migth be a whisker, extend the search area to include a larger portion of the possible whisker 
#            
#            new_c = [int(xval[seed]+Data[-1,0]), int(yval[seed]+int(m_size/2))]
#            new_area = frame[new_c[1]-int(m_size/2):new_c[1]+int(m_size/2)+1,new_c[0]-int(m_size/2):new_c[0]+int(m_size/2)+1].copy()
#            min_position = np.zeros([m_size])
#            for m in range(0,m_size):
#                min_position[m] = np.argmin(new_area[:,m])
#                
#            Data2 = np.c_[np.linspace(int(m_size/2),-int(m_size/2),m_size),min_position-int(m_size/2)]
#            pca.fit(Data2)
#            
#            
#            c1 = pca.explained_variance_[0]
#            c2 = pca.explained_variance_[1]
#            if c1>=c2:
#                major_axis = c1# np.sqrt(c1)
#                minor_axis = c2#np.sqrt(c2)
#            else:
#                major_axis = c2#np.sqrt(c2)
#                minor_axis = c1#np.sqrt(c1)
#            
#            exc2= np.sqrt(1-(minor_axis/major_axis))
#            
#            if exc2 > 0.98: #this is a whisker :) Store its information 
#                whiskers.append([[int(xval[seed]+Data[0,0]), int(yval[seed]-int(m_size/2))],[int(xval[seed]),
#                                  int(yval[seed])],new_c,[int(new_c[0]+Data2[-1,0]), int(new_c[1]+int(m_size/2))]])
#                #used_seeds.append([seed])
#    
#                framo= cv2.line(framo, tuple(whiskers[-1][0]), tuple(whiskers[-1][-1]),[255,255,255],1)
#              
#
#            
        
print('time = ',time.time()-st)
cv2.imshow("Video3",framo)
