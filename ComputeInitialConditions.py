# -*- coding: utf-8 -*-
"""
Created on Fri Dec 14 21:58:02 2018

@author: GUARIND
"""

import os
import cv2
import numpy as np
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
        
    
    if exc_v < 0.985:
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


def initial_conditions(ListofFiles,foldername, FaceCenter, threshold, InitFrame = 0):
        
    if isinstance(threshold, int):  #remove background by thresholding
        #reaf first image of the list to estimate initial conditions
        image = cv2.imread(os.path.join(foldername,ListofFiles[InitFrame]),0)  #last 0 means gray scale
        #find its shape
        h,w = image.shape
        
        #dilate to remove whiskers and other small objects
        kernel = np.ones((11,11), np.uint8)
        im = cv2.dilate(image,kernel,iterations=1)
        #apply threshold so that only the face is selected. I used the mean brightness value
        th,_,_,_ = cv2.mean(im)
        im[im>np.ceil(th)] = 255
        im[im<255] = 0 
        
        #now we have an image on 255 (white) and 0 (black) with the face countour, all small details where removed 
        #apply a LARGE Gaussian filter to "smooth" the transition between face/no-face
        im = cv2.GaussianBlur(im,(11,11),0)
       
        #apply canny filter to detect edges
        edges = cv2.Canny(im,50,100) 
        
        
        #find how far is the selected Face Center from the snout
        where_at_center = np.where(edges[FaceCenter[1],:]==255)
        dist_face_center = FaceCenter[0] - where_at_center[0][0]
        
        #create a mask with a circle centered at the FaceCenter and radius 1.25 the distance between FaceCenter and the snout
        mask = np.zeros((h,w), dtype = np.uint8)
        mask = cv2.circle(mask, tuple(FaceCenter), int(dist_face_center*1.5), [255,255,255])
        
        #find where the mask and the edges coincide 
        coinc = np.where(np.multiply(edges,mask)!= 0)
        if coinc[1][0]<FaceCenter[0]:
            #in the right
            st_right = [coinc[1][0], coinc[0][0]]
            #and left
            st_left = [coinc[1][1], coinc[0][1]]
        else:
            #in the right
            st_right = [coinc[1][1], coinc[0][1]]
            #and left
            st_left = [coinc[1][0], coinc[0][0]] 
        
        #take the right side of the image
        right = image.copy()
        right = right[:,0:FaceCenter[0]]
        right_mask = mask.copy()
        right_mask = right_mask[:,0:FaceCenter[0]]
        #find the pixels where the circle was drawn 
        mask_position = np.where(right_mask == 255) #pixels in the circle
        
        #find pixels in the semi-circle that do no coincide with the face and are at least 10 pixels (in y) apart from the face 
        cross_ = np.where(mask_position[0]>st_right[1]+15) 
        y_position = mask_position[0][cross_[0][0]:]
        x_position = mask_position[1][cross_[0][0]:]
        intensity = np.zeros([len(y_position)])
        #find the pixel intensity around the semi-circle (this will not include the face)
        for m in range(0,len(y_position)):
            intensity[m] = right[y_position[m],x_position[m]]   
            
        whisker_shadows_right = np.where(intensity < threshold) #determine what are whiskers based on threshold selected by the user
        
        #test the possible whisker to see if there actually whiskers. We only need the most caudal and most rostal whiskers 
        k=0
        while True:
            pp = test_line_like_ness(image,[y_position[whisker_shadows_right[0][k]],x_position[whisker_shadows_right[0][k]]] , m_size=7) 
            if pp>0.985:
                break
            k+=1
            
        cauldal_right = [x_position[whisker_shadows_right[0][k]], y_position[whisker_shadows_right[0][k]]]
    
        k = len(whisker_shadows_right[0])-1
        while True:
            pp = test_line_like_ness(image,[y_position[whisker_shadows_right[0][k]],x_position[whisker_shadows_right[0][k]]] , m_size=7) 
            if pp>0.985:
                break
            k-=1    
            
        rostal_right = [x_position[whisker_shadows_right[0][k]], y_position[whisker_shadows_right[0][k]]]
        
        #find the angle between the most rostal and most caudal whiskers
        x1 = FaceCenter[0]-cauldal_right[0]
        y1 = FaceCenter[1]-cauldal_right[1]
        
        x2 = FaceCenter[0]-rostal_right[0]
        y2 = FaceCenter[1]-rostal_right[1]
        rad = np.sqrt(x1**2 + y1**2)
        p = rad*(x1+x2)/(np.sqrt((x1+x2)**2 + (y1+y2)**2))
        q = ((y1+y2)/(x1+x2))*p
        
        angle_right = np.arctan(q/p)*180/np.pi
        
        
        #take the left side of the image
        left = image.copy()
        left = left[:,FaceCenter[0]:]
        left_mask = mask.copy()
        left_mask = left_mask[:,FaceCenter[0]:]
        
        mask_position= np.where(left_mask ==255)
        cross_ = np.where(mask_position[0]>st_left[1]+15)
        y_position = mask_position[0][cross_[0][0]:]
        x_position = mask_position[1][cross_[0][0]:]
        intensity = np.zeros([len(y_position)])
        for m in range(0,len(y_position)):
            intensity[m] = left[y_position[m],x_position[m]]
        
    
        whisker_shadows_left = np.where(intensity < threshold)
        #test the possible whisker to see if there actually whiskers. We only need the most caudal and most rostal whiskers 
        k=0
        while True:
            pp = test_line_like_ness(image,[y_position[whisker_shadows_left[0][k]],x_position[whisker_shadows_left[0][k]] + FaceCenter[0]] , m_size=7) 
            if pp>0.985:
                break
            k+=1
    
        cauldal_left = [x_position[whisker_shadows_left[0][k]]+FaceCenter[0], y_position[whisker_shadows_left[0][k]]]
    
        k = len(whisker_shadows_left[0])-1
        while True:
            pp = test_line_like_ness(image,[y_position[whisker_shadows_left[0][k]],x_position[whisker_shadows_left[0][k]] + FaceCenter[0]] , m_size=7) 
            if pp>0.985:
                break
            k-=1    
            
        rostal_left = [x_position[whisker_shadows_left[0][k]]+FaceCenter[0], y_position[whisker_shadows_left[0][k]]]
        
        
        #find the angle between the most rostal and most caudal whiskers
        x1 = cauldal_left[0]-FaceCenter[0]
        y1 = FaceCenter[1]-cauldal_left[1]
        
        x2 = rostal_left[0]-FaceCenter[0]
        y2 = FaceCenter[1]-rostal_left[1]
        rad = np.sqrt(x1**2 + y1**2)
        p = rad*(x1+x2)/(np.sqrt((x1+x2)**2 + (y1+y2)**2))
        q = ((y1+y2)/(x1+x2))*p
        
        angle_left = np.arctan(q/p)*180/np.pi
        
    else: #remove background by subtraction 

        #read first image of the list to estimate initial conditions
        image = cv2.imread(os.path.join(foldername,ListofFiles[InitFrame]),0)  #last 0 means gray scale
        #find its shape
        h,w = image.shape
        
        #dilate to remove whiskers and other small objects
        kernel = np.ones((11,11), np.uint8)
        face = cv2.dilate(image,kernel,iterations=1)
        
        
        #apply threshold so that only the face is selected. I used the mean brightness value
        th,_,_,_ = cv2.mean(face)
        face[face>np.ceil(th)] = 255
        face[face<255] = 0 
        
        
        #apply canny filter to detect edges
        edges = cv2.Canny(face,50,100) 
        #cv2.imshow("",edges)
        
        #face[face==255] =1
        
        #removing background 
        
        im = cv2.subtract(threshold,image).astype(np.uint8)
        im[im<10]=0
        im = np.multiply(im,face).astype(np.uint8)
        im[im>0]=255
 
        
        #find how far is the selected Face Center from the snout
        where_at_center = np.where(edges[FaceCenter[1],:]==255)
        dist_face_center = FaceCenter[0] - where_at_center[0][0]
        
        #create a mask with a circle centered at the FaceCenter and radius 1.25 the distance between FaceCenter and the snout
        mask = np.zeros((h,w), dtype = np.uint8)
        mask = cv2.circle(mask, tuple(FaceCenter), int(dist_face_center*1.5), [255,255,255])
        
        #find where the mask and the edges coincide 
        coinc = np.where(np.multiply(edges,mask)!= 0)
        if coinc[1][0]<FaceCenter[0]:
            #in the right
            st_right = [coinc[1][0], coinc[0][0]]
            #and left
            st_left = [coinc[1][1], coinc[0][1]]
        else:
            #in the right
            st_right = [coinc[1][1], coinc[0][1]]
            #and left
            st_left = [coinc[1][0], coinc[0][0]] 
        
        #take the right side of the image
        right = im.copy()
        right = right[:,0:FaceCenter[0]]
        right_mask = mask.copy()
        right_mask = right_mask[:,0:FaceCenter[0]]
        #find the pixels where the circle was drawn 
        mask_position = np.where(right_mask == 255) #pixels in the circle
   
        #find pixels in the semi-circle that do no coincide with the face and are at least 10 pixels (in y) apart from the face 
        cross_ = np.where(mask_position[0]>st_right[1]+15) 
        y_position = mask_position[0][cross_[0][0]:]
        x_position = mask_position[1][cross_[0][0]:]
        intensity = np.zeros([len(y_position)])
        #find the pixel intensity around the semi-circle (this will not include the face)
        for m in range(0,len(y_position)):
            intensity[m] = right[y_position[m],x_position[m]]   
            
        whisker_shadows_right = np.where(intensity > 0) #determine what are whiskers based on threshold selected by the user
 
        #test the possible whisker to see if there actually whiskers. We only need the most caudal and most rostal whiskers 
        k=0
        while True:
            pp = test_line_like_ness(image,[y_position[whisker_shadows_right[0][k]],x_position[whisker_shadows_right[0][k]]] , m_size=7) 
            if pp>0.985:
                break
            k+=1
            
        cauldal_right = [x_position[whisker_shadows_right[0][k]], y_position[whisker_shadows_right[0][k]]]
        
        k = len(whisker_shadows_right[0])-1
        while True:
            pp = test_line_like_ness(image,[y_position[whisker_shadows_right[0][k]],x_position[whisker_shadows_right[0][k]]] , m_size=7) 
            if pp>0.985:
                break
            k-=1    
            
        rostal_right = [x_position[whisker_shadows_right[0][k]], y_position[whisker_shadows_right[0][k]]]
        
        #find the angle between the most rostal and most caudal whiskers
        x1 = FaceCenter[0]-cauldal_right[0]
        y1 = FaceCenter[1]-cauldal_right[1]
        
        x2 = FaceCenter[0]-rostal_right[0]
        y2 = FaceCenter[1]-rostal_right[1]
        rad = np.sqrt(x1**2 + y1**2)
        p = rad*(x1+x2)/(np.sqrt((x1+x2)**2 + (y1+y2)**2))
        q = ((y1+y2)/(x1+x2))*p
        
        angle_right = np.arctan(q/p)*180/np.pi

        #take the left side of the image
        left = image.copy()
        left = left[:,FaceCenter[0]:]
        left_mask = mask.copy()
        left_mask = left_mask[:,FaceCenter[0]:]

        mask_position= np.where(left_mask ==255)
        cross_ = np.where(mask_position[0]>st_left[1]+15)
        y_position = mask_position[0][cross_[0][0]:]
        x_position = mask_position[1][cross_[0][0]:]
        intensity = np.zeros([len(y_position)])
        for m in range(0,len(y_position)):
            intensity[m] = left[y_position[m],x_position[m]]

        
        whisker_shadows_left = np.where(intensity > 0)
        #test the possible whisker to see if there actually whiskers. We only need the most caudal and most rostal whiskers 
        k=0
        while True:
            pp = test_line_like_ness(image,[y_position[whisker_shadows_left[0][k]],x_position[whisker_shadows_left[0][k]] + FaceCenter[0]] , m_size=7) 
            if pp>0.985:
                break
            k+=1

        cauldal_left = [x_position[whisker_shadows_left[0][k]]+FaceCenter[0], y_position[whisker_shadows_left[0][k]]]
        
        k = len(whisker_shadows_left[0])-1
        while True:
            pp = test_line_like_ness(image,[y_position[whisker_shadows_left[0][k]],x_position[whisker_shadows_left[0][k]] + FaceCenter[0]] , m_size=7) 
            if pp>0.985:
                break
            k-=1    
            
        rostal_left = [x_position[whisker_shadows_left[0][k]]+FaceCenter[0], y_position[whisker_shadows_left[0][k]]]
        

        #find the angle between the most rostal and most caudal whiskers
        x1 = cauldal_left[0]-FaceCenter[0]
        y1 = FaceCenter[1]-cauldal_left[1]
        
        x2 = rostal_left[0]-FaceCenter[0]
        y2 = FaceCenter[1]-rostal_left[1]
        rad = np.sqrt(x1**2 + y1**2)
        p = rad*(x1+x2)/(np.sqrt((x1+x2)**2 + (y1+y2)**2))
        q = ((y1+y2)/(x1+x2))*p
        
        angle_left = np.arctan(q/p)*180/np.pi

    return np.array([angle_right, angle_left])


