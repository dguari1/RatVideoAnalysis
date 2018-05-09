# -*- coding: utf-8 -*-
"""
Created on Tue May  8 14:48:49 2018

@author: guarind
"""

import cv2
import numpy as np

def find_center_whiskerpad(image):
    
    if len(image.shape) == 3: #if image is color, then convert it to gray scale
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
    
    #define kernels (only once). This works fine with current images (720x500), might need to be changed if image size changes
    Kernel_dilat1 = np.ones((11,11), np.uint8)
    kernel_erode1 = np.ones((5,5), np.uint8)
    kernel_dilat2 = np.ones((21,21), np.uint8)
        
    #dilate original image to remove small objects
    face = cv2.dilate(image,Kernel_dilat1,iterations=1)
    
    
    #apply threshold so that only the face is selected. I used the mean brightness value
    th,_,_,_ = cv2.mean(face)
    face[face>np.ceil(th)] = 255
    face[face<255] = 0 
    
    #apply canny filter to detect edges
    edges = cv2.Canny(face,50,100)  
    #this image should contain the face contour only. Plot it to verify results 
    #cv2.namedWindow('facial_contour',cv2.WINDOW_NORMAL)
    #cv2.imshow("facial_contour", edges)
    
    #remove everything from the original image except the rat face
    face = cv2.bitwise_not(face)
    face[face==255] = 1
    
    only_face = np.multiply(image, face)
    
    #find how many pixels are inside the rat face and their position pixels in the face
    position = np.where(face == 1)
    #find the average pixel intensity inside the face. Eyes will be of lower intensity that rest of the face
    th_face = np.sum(only_face[position[0],position[1]])/len(position[0])
        
    #apply threshold to the image to remove everything that is lighther than half of the average face pixel intensity. This works well with our images 
    #and should still work in better lighting conditions. It might not work is image is too dark 
    only_eyes = only_face.copy()
    only_eyes[only_eyes>th_face//2] = 0
    only_eyes[only_eyes!= 0] = 255
    
    #apply erosion and dilatation to remove small objects (noise) and combine large pieces together (eyes might be divided by fur, we don't want that)
    #the used kernels work fine for the images under analysis, they might need to be changes for different image size
    only_eyes =  cv2.erode(only_eyes,kernel_erode1,iterations=1)
    only_eyes =  cv2.dilate(only_eyes,kernel_dilat2,iterations=1)
    #this image should contain the eyes and other big dark areas in the face. Plot it to verify results 
#    cv2.namedWindow('Eyes_contour',cv2.WINDOW_NORMAL)
#    cv2.imshow('Eyes_contour', only_eyes)
    
    
    #use cv2 to detect the different contours in the binary image, some of these contours should be the eyes (if they are open)
    _,contours,hierarchy = cv2.findContours(only_eyes, cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    
    #now apply a set of steps to discard the different contours in the image that are not eyes
    Eyes_Found  = False #this variable will inform if eyes cannot be found
    selected_contours = []
    for cnt in contours:
        contact_border = np.where(cnt==0)[0] #is the countour touching the border? If yes then is not an eye 
        if contact_border.size == 0 :
            x,y,w,h = cv2.boundingRect(cnt)
            aspect_ratio = float(w)/h

            
            if aspect_ratio < 0.95: #verify if the bounding box is not squared, if is square then is not an eye 
                selected_contours.append(cnt)
    
    #the remainder contours are not squares and don't touch the borders. Apply a similarity index between 
    Eyes = []
    if len(selected_contours) == 2: #if there are only two contours then they are probably the eyes.... let's roll with it 
        Eyes = selected_contours 
        Eyes_Found = True
        
    else: #if there are more than two contours then we have to find what countours are eyes (if any)

        #compute a similarity matrix between contours, this computes the Hu moments of each contour and generates a similarity index between contours
        #Hu moments are invariant for rotation and translation so they should be able to detect two ellipses with different rotations 
        #0 means equal contours, 1 means complete un-equal contours
        Contours_Comp = np.zeros((len(selected_contours),len(selected_contours)), dtype = np.double)   
        for k,cnt1 in enumerate(selected_contours):
            for j,cnt2 in enumerate(selected_contours):
                ret = cv2.matchShapes(cnt1,cnt2,3,0.0)
                Contours_Comp[j,k] = ret

        #go row by row looking for contours that are similar, I define two similar contours if their similarity is less than 0.1
        for k in range(0,len(Contours_Comp)):            
            values = Contours_Comp[k]
            match = min(np.delete(values,k))
            if match < 0.1: #if two similar contours are found then stop, these are probably the eyes
                j = np.where(values == match)[0][0]
                Eyes_Found = True
                break
           
        
        if Eyes_Found is True:
            Eyes.append(selected_contours[k])
            Eyes.append(selected_contours[j])
   
          
    
    if Eyes_Found is True: # Eyes found, continue...        
        #find the center of mass of each contour that represents the eye
        info_eyes =[]
        for eye in Eyes:
            M = cv2.moments(eye)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            info_eyes.append((cx,cy))
        
        
        if info_eyes[0][0] < info_eyes[1][0]:
            right_eye = info_eyes[0] 
            left_eye = info_eyes[1]
        else:
            right_eye = info_eyes[1] 
            left_eye = info_eyes[0]
            
        #find the mid-point between eyes
        mid_face =((left_eye[0]-right_eye[0])//2 + right_eye[0], (left_eye[1]+right_eye[1])//2 )
        
        #find where this mid-eye location projects to the snout. For this I use generete a mask that simply contains a line 
        #between the mid-eye center and the end of the image, and multiply this by the image tha contains only the face edge. 
        #Then i find where these two images intersept, this provides a point in the snout (not the center of the snout)
        mask = np.zeros(image.shape,dtype = np.uint8)
        cv2.line(mask, mid_face, (mid_face[0],mask.shape[1]),(255,255,255))
        TEMP_snout = np.where(np.multiply(edges, mask) != 0)
        temp_snout=(TEMP_snout[1][0],TEMP_snout[0][0])
        
        distance = np.sqrt((temp_snout[1]-mid_face[1])**2+(temp_snout[0]-mid_face[0])**2)

        TEMP = 255*face[temp_snout[1]-int(distance/2):temp_snout[1]+int(distance/2),temp_snout[0]-int(distance/3):temp_snout[0]+int(distance/3)]
        _,contours_snout,_= cv2.findContours(TEMP, cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        (x,y),radius = cv2.minEnclosingCircle(contours_snout[0])
        
        
        snout=(x+temp_snout[0]-distance/3,temp_snout[1])

        eyes_to_snout = np.sqrt((snout[1]-mid_face[1])**2  + (snout[0]-mid_face[0])**2)
        
        angle = np.arctan((snout[0]-mid_face[0])/(snout[1]-mid_face[1]))
        adj = (2/3)*eyes_to_snout
        opp = np.sin(angle)*adj
        
        center_pad = (mid_face[0]+int(round(opp)), mid_face[1]+int(round(adj)))
                
    
        return center_pad,snout, mid_face, Eyes_Found 
            
    else: #Eyes not found, return error 
        
        return (0,0),(0,0),(0,0),Eyes_Found
        