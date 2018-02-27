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
from sklearn.decomposition import PCA

def test_line_like_ness(frame, pos, m_size=None):
    #now, every seed needs to be tested for the presence of a whisker, this will be done by selecting a 7x7
    #matrix centered on the seed. Then, the local minima from every row and every column will be localized, if there is 
    #a whisker then these local minimina should resemble a line, if not then they won't. The line-like quality of the 
    #local minima will be quantified using a Pricipal-Component-Decomposition (PCA) of the dots. If the local 
    #minima does resemble a line, then the principal axis of the data will be resemble an ellipse with a very small excentricity (>0.98)
   
    #frame -> image
    #pos -> [y,x] position of central pixel 
    #msize -> size of selected rectangular area, default 7
    if m_size is None:
        m_size =7
    
    #initialize the PCA object, this is rather slow...
    pca = PCA(n_components=2)

    selected_area = frame[pos[0]-int(m_size/2):pos[0]+int(m_size/2)+1,pos[1]-int(m_size/2):pos[1]+int(m_size/2)+1]
    
    
    #search for minima in each row, this will detect whiskers that are not horizontal
    min_position = np.zeros([m_size])
    for m in range(0,m_size):
        min_position[m] = np.argmin(selected_area[m,:])
        
    if abs(min_position[int(m_size/2)]-int(m_size/2)) > 1:        
        pass  
        exc_v = 0      
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
        
        exc_v= np.sqrt(1-(minor_axis/major_axis))
        
    
    if exc_v < 0.95:
        #search for minima in each column, this will detect whiskers that are horizontal
        min_position = np.zeros([m_size])
        for m in range(0,m_size):
            min_position[m] = np.argmin(selected_area[:,m])
            
        if abs(min_position[int(m_size/2)]-int(m_size/2)) > 1:        
            pass  
            exc_v = 0      
        else:
        
            Data = np.c_[np.linspace(int(m_size/2),-int(m_size/2),m_size),min_position-int(m_size/2)]
            pca.fit(Data)       
            
            c1 = pca.explained_variance_[0]
            c2 = pca.explained_variance_[1]
            if c1>=c2:
                major_axis = c1# np.sqrt(c1)
                minor_axis = c2#np.sqrt(c2)
            else:
                major_axis = c2#np.sqrt(c2)
                minor_axis = c1#np.sqrt(c1)
            
            exc_v= np.sqrt(1-(minor_axis/major_axis))
        
    return exc_v
         
        



#read gray image
path_frames = r'C:\Users\GUARIND\Videos\Basler\test1'
image1 = 'Basler acA800-510uc (22501173)_20171212_190308266_0020.tiff'
frame =  cv2.imread(path_frames + '/' + image1, 0)
#frame[frame>90]=255
st = time.time()
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
center = [400,310]

where_at_center = np.where(edges[:,center[0]]==255)
dist_face_center = where_at_center[0][0]-center[1]

mask = np.zeros(frame.shape, dtype = np.uint8)
mask = cv2.circle(mask, tuple(center), int(dist_face_center*1.25), [255,255,255])

mask = cv2.line(mask, (0,310),(800,310),[255,255,255])
mask = cv2.line(mask, (400,0),(400,600),[255,255,255])
#cv2.imshow("image",frame| mask | edges)

coinc = np.where(np.multiply(edges,mask)!= 0)
st_right = [coinc[1][0], coinc[0][0]]
st_left = [coinc[1][1], coinc[0][1]]



right = frame.copy()
right = right[:,0:center[0]]
right_mask = mask.copy()
right_mask = right_mask[:,0:center[0]]

mask_position = np.where(right_mask == 255) #pixels in the circle
cross_ = np.where(mask_position[0]>st_right[1]+10) 
y_position = mask_position[0][cross_[0][0]:]
x_position = mask_position[1][cross_[0][0]:]
intensity = np.zeros([len(y_position)])
for m in range(0,len(y_position)):
    intensity[m] = right[y_position[m],x_position[m]]
    
whisker_shadows_right = np.where(intensity < 100);
new_mask_right = np.zeros(frame.shape, dtype = np.uint8)
k=0
while True:
   pp = test_line_like_ness(frame,[y_position[whisker_shadows_right[0][k]],x_position[whisker_shadows_right[0][k]]] , m_size=7) 
   if pp>0.98:
       break
   k+=1

new_mask_right[y_position[whisker_shadows_right[0][k]],x_position[whisker_shadows_right[0][k]]]  = 255

mask = cv2.line(mask,tuple(center),tuple([x_position[whisker_shadows_right[0][k]],y_position[whisker_shadows_right[0][k]]]),[255,255,255])
    
print(np.arctan((y_position[whisker_shadows_right[0][k]]-320)/(400-x_position[whisker_shadows_right[0][k]]))*180/np.pi)
k = len(whisker_shadows_right[0])-1
while True:
    pp = test_line_like_ness(frame,[y_position[whisker_shadows_right[0][k]],x_position[whisker_shadows_right[0][k]]] , m_size=7) 
    if pp>0.98:
       break
    k-=1
new_mask_right[y_position[whisker_shadows_right[0][k]],x_position[whisker_shadows_right[0][k]]] = 255

mask = cv2.line(mask,tuple(center),tuple([x_position[whisker_shadows_right[0][k]],y_position[whisker_shadows_right[0][k]]]),[255,255,255])

print(np.arctan((y_position[whisker_shadows_right[0][k]]-320)/(400-x_position[whisker_shadows_right[0][k]]))*180/np.pi)

cv2.imshow("image",frame| new_mask_right |mask)

#%%
left = frame.copy()
left = left[:,center[0]:]
left_mask = mask.copy()
left_mask = left_mask[:,center[0]:]

mask_position= np.where(left_mask ==255)
cross_ = np.where(mask_position[0]>st_left[1]+10)
y_position = mask_position[0][cross_[0][0]:]
x_position = mask_position[1][cross_[0][0]:]
intensity = np.zeros([len(y_position)])
for m in range(0,len(y_position)):
    intensity[m] = left[y_position[m],x_position[m]]
    
whisker_shadows_left = np.where(intensity < 96);

new_mask_left = np.zeros(frame.shape, dtype = np.uint8)
new_mask_left[y_position[whisker_shadows_left[0][0]],x_position[whisker_shadows_left[0][0]]+center[0]] = 255
new_mask_left[y_position[whisker_shadows_left[0][-1]],x_position[whisker_shadows_left[0][-1]] + center[0]] = 255

pp = test_line_like_ness(frame,[y_position[whisker_shadows_left[0][0]],x_position[whisker_shadows_left[0][0]]+center[0]] , m_size=7)
print(pp)
pp = test_line_like_ness(frame,[y_position[whisker_shadows_left[0][-1]],x_position[whisker_shadows_left[0][-1]] + center[0]]  , m_size=7)
print(pp)

print('time = ',time.time()-st)
cv2.imshow("image_circ", frame|mask|edges)
cv2.imshow("image",frame| new_mask_right |mask)
mask = cv2.line(mask,tuple(center),tuple())



            