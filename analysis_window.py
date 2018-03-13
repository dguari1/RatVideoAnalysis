# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 12:54:17 2017

@author: Diego L.Guarin -- diego_guarin at meei.harvard.edu
"""

import os
import sys
import cv2
import time
import numpy as np
from scipy import signal 
from sklearn.decomposition import PCA



from multiprocessing import Pool
from functools import partial

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QPushButton, QDialog
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
"""

This window takes care of all the processing, it does it in a new thread so that 
the main GUI will no freeze during execution. It will inform the user that work 
is beeing done by a small animation. 

Work to do: Create a % bar that indicates the state of things

"""

def rot_estimation(ListofFiles,ExtraInfo):  

    scale = 0.5
    
    #function that takes care of computing the angular rotation between frames in ListofFiles
    
    #this is the list of files to be analized, 
    ListofFiles = ListofFiles
    
    #'unzip' all the aditional parameters that where passed
    foldername, center, RightROI, LeftROI, threshold, angles, Side, rotation_angle = zip(*ExtraInfo)  

    
    
    foldername = foldername[0]  
    center = center[0]
    RightROI = RightROI[0]
    LeftROI = LeftROI[0]
    threshold = threshold[0]
    rotation_angle = rotation_angle[0]
    Side = Side[0]
    angles = angles[0]

    zero_pos = np.where(angles == 0)[0]

    angles_neg = angles[0:int(zero_pos[0])+1]

    angles_pos = angles[int(zero_pos[0]):-1] 
#    nann=str(time.time())
#    with open(os.path.join(foldername,nann+'.txt'), 'w') as f:
#        for item in ListofFiles:
#            f.write("%s\n" % str(item))

    #np.savetxt(os.path.join(foldername,'tt.txt'), np.array([ ListofFiles]), delimiter=',') 
    
    #read first image in gray scale
    image = cv2.imread(os.path.join(foldername,ListofFiles[0]),0)  #last 0 means gray scale
    
    #################
    #dilate to remove whiskers and other small objects
    kernel = np.ones((11,11), np.uint8)
    face_edge = cv2.dilate(image,kernel,iterations=1)

    #apply threshold so that only the face is selected. I used the mean brightness value
    th,_,_,_ = cv2.mean(face_edge)
    face_edge[face_edge>np.ceil(th)] = 255
    face_edge[face_edge<255] = 0 
    face_edge[face_edge==255] = 1
    #face_edge is 1 for the face and 0 for everything else 
    
    ######################

    #remove the first element from the list
    ListofFiles = np.delete(ListofFiles,[0])
    
    h_orig, w_orig = image.shape #original shape 
    
    if rotation_angle is not None: #rotate
        M_overall = cv2.getRotationMatrix2D(tuple(int(w_orig/2),int(h_orig/2)), rotation_angle, 1.0)
        image = cv2.warpAffine(image, M_overall, (w_orig, h_orig))
    
    #we have to do different operation depending on what side 
    if Side == 'Right':
        ROI = RightROI
        image = image[:,0:center[0]] #take right side
        face_edge = face_edge[:,0:center[0]]
    else:
        ROI = LeftROI
        ROI = [2*center[0],0]-ROI  #mirror the left ROI to the right 
        ROI[:,1]=abs(ROI[:,1])  #correct the minus sign in the y column
        image = cv2.flip(image,1) #mirror it
        image = image[:,0:w_orig-center[0]]  #take left side
        
        face_edge = cv2.flip(face_edge,1)
        face_edge = face_edge[:,0:w_orig-center[0]]

    #print(Side)
    
    lims_x=[min(ROI[:,0])-10, max(ROI[:,0])+10]
    if lims_x[0]<0:
        lims_x[0]=0
    if lims_x[1]>center[0]:
        lims_x[1]=center[0]
        
    lims_y=[min(ROI[:,1])-10, max(ROI[:,1])+10]
    if lims_y[0]<0:
        lims_y[0]=0
    if lims_y[1]>h_orig:
        lims_y[1]=h_orig    
    #print(lims_x,lims_y)
    if isinstance(threshold, int):  #remove background by thresholding
        bc = 'threshold'
        #apply threshold
        image[image>threshold] = 255
        #invert image to improve results
        image = cv2.bitwise_not(image)
        #multiply by the image of the face
        image = np.multiply(image,face_edge).astype(np.uint8)
        image[image>10] = 255
        
    else:
        print(threshold.shape)
        image = cv2.subtract(threshold, image).astype(np.uint8)
        image[image<10]=0
        image = np.multiply(image,face_edge).astype(np.uint8)
    
    #create the mask that will cover only the whiskers in left and right sides of the face
    mask = np.zeros(image.shape, np.uint8)    
    cv2.fillConvexPoly(mask, ROI, (255,255,255))

    
    results= np.zeros((1,1),dtype = np.float64) #this vector will take care of storing the results
   
    h,w=image.shape
    #here is where the processing starts 
    for counter, file in enumerate(ListofFiles):
        #print(counter)
        #keep the previous frame in memory to compare with the next frame
        old_image = image.copy()
        #old_left = left.copy()
        
        if file is not None:
            #load a new image in gray scale
            image = cv2.imread(os.path.join(foldername,file),0) 
            ############
            #image = np.multiply(image,face_edge).astype(np.uint8)
            #############
            if rotation_angle is not None: #rotate      
                image = cv2.warpAffine(image, M_overall, (w_orig, h_orig))
            
            if Side == 'Right':
                image = image[:,0:center[0]] #take right side
            else:
                image = cv2.flip(image,1) #mirror it
                image = image[:,0:w_orig-center[0]]  #take left side
                
            if bc == 'threshold':  #remove background by thresholding 
                #apply threshold
                image[image>threshold] = 255
                #invert image to improve results
                image = cv2.bitwise_not(image)
                image = np.multiply(image,face_edge).astype(np.uint8)
                image[image>10] = 255
            else:
                image = cv2.subtract(threshold, image).astype(np.uint8)
                image[image<10]=0
                image = np.multiply(image,face_edge).astype(np.uint8)
            
            #start the process ...
            
            #apply the mask to select ROI in the previous frame
            old_temp = np.zeros([h,w], np.uint8)     
            cv2.bitwise_and(old_image,mask,old_temp) 
            
            if counter == 0:
                #first run using all angles 
                res = np.zeros((len(angles),1),dtype = np.float64)

                
                old_small_image= cv2.resize(old_temp[lims_y[0]:lims_y[1],lims_x[0]:lims_x[1]],(0,0),fx=scale,fy=scale)
                
                for index,angle in enumerate(angles):
                    
                    #rotate the image by angles
                    M = cv2.getRotationMatrix2D(tuple(center), angle, 1.0)
                    rotated = cv2.warpAffine(image, M, (w, h))
                    #apply the mask to selected ROI in rotated image 
                    temp = np.zeros([h,w], np.uint8)     
                    cv2.bitwise_and(rotated,mask,temp) 
    
                    #find the correlation between the previous frame and the rotate version of the current frame                                                     
                    correl = cv2.matchTemplate(old_small_image, cv2.resize(temp[lims_y[0]:lims_y[1],lims_x[0]:lims_x[1]],(0,0),fx=scale,fy=scale), cv2.TM_CCORR_NORMED)  
                    #store the results 
                    res[index,0] = correl
                    
                #select the angle that provided the largest correlation     
                select_val= angles[np.argmax(res)]
                
                #store the results 
                results = np.append(results, select_val) 
                #print('thas')
            else: 
                #now from the third frame we can strat secting weather to use only positive or negative angles 
                 
                #if the sign is negative in two consecutive samples, and the angle is less than 15% of the largest negative angle
                #then the movement will still be in the same direction
                #print(results[counter])
                if (results[counter] < 0 and results[counter-1] < 0) and results[counter]<angles[0]*0.15: 
                    res = np.zeros((len(angles_neg),1),dtype = np.float64)
                    
                    old_small_image = cv2.resize(old_temp[lims_y[0]:lims_y[1],lims_x[0]:lims_x[1]],(0,0),fx=0.5,fy=0.5)
                    
                    for index,angle in enumerate(angles_neg):
                        
                        #rotate the frame
                        M = cv2.getRotationMatrix2D(tuple(center), angle, 1.0)
                        rotated = cv2.warpAffine(image, M, (w, h))
                        
                        #apply the mask to selected ROI in rotated image 
                        temp = np.zeros([h,w], np.uint8)     
                        cv2.bitwise_and(rotated,mask,temp) 
                       
        
                        #find the correlation between the previous frame and the rotate version of the current frame                                                     
                        correl = cv2.matchTemplate(old_small_image, cv2.resize(temp[lims_y[0]:lims_y[1],lims_x[0]:lims_x[1]],(0,0),fx=scale,fy=scale), cv2.TM_CCORR_NORMED)  
                        
                        #store the results 
                        res[index,0] = correl    
                        
                    #select the angle that provided the largest correlation     
                    select_val = angles_neg[np.argmax(res)]
                    
                    #store the results 
                    results = np.append(results, select_val) 
                    #print('this')
                #if the sign is positive in two consecutive samples, and the angle is less than 15% of the largest positive angle 
                #then the movement will still be in the same direction
                elif (results[counter] > 0 and results[counter-1] > 0) and results[counter]>angles[-1]*0.15: 
                    res = np.zeros((len(angles_pos),1),dtype = np.float64)
                    
                    old_small_image = cv2.resize(old_temp[lims_y[0]:lims_y[1],lims_x[0]:lims_x[1]],(0,0),fx=0.5,fy=0.5)
                    
                    for index,angle in enumerate(angles_pos):
                        
                        #rotate the frame
                        M = cv2.getRotationMatrix2D(tuple(center), angle, 1.0)
                        rotated = cv2.warpAffine(image, M, (w, h))
                        
                        #apply the mask to selected ROI in rotated image 
                        temp = np.zeros([h,w], np.uint8)     
                        cv2.bitwise_and(rotated,mask,temp) 
                       
        
                        #find the correlation between the previous frame and the rotate version of the current frame                                                     
                        correl = cv2.matchTemplate(old_small_image, cv2.resize(temp[lims_y[0]:lims_y[1],lims_x[0]:lims_x[1]],(0,0),fx=scale,fy=scale), cv2.TM_CCORR_NORMED)  
                        
                        #store the results 
                        res[index,0] = correl    
                        
                    #select the angle that provided the largest correlation     
                    select_val = angles_pos[np.argmax(res)]
                    
                    #store the results 
                    results = np.append(results, select_val) 
                    #print('thos')
                #if there is change in the sign then the whisker is changing direction, we have to analize all angles 
                else: 
                    
                    res = np.zeros((len(angles),1),dtype = np.float64)
                    
                    old_small_image = cv2.resize(old_temp[lims_y[0]:lims_y[1],lims_x[0]:lims_x[1]],(0,0),fx=0.5,fy=0.5)
                    
                    for index,angle in enumerate(angles):
                        
                        #rotate the frame
                        M = cv2.getRotationMatrix2D(tuple(center), angle, 1.0)
                        rotated = cv2.warpAffine(image, M, (w, h))
                        
                        #apply the mask to selected ROI in rotated image 
                        temp = np.zeros([h,w], np.uint8)     
                        cv2.bitwise_and(rotated,mask,temp) 
                       
        
                        #find the correlation between the previous frame and the rotate version of the current frame                                                     
                        correl = cv2.matchTemplate(old_small_image, cv2.resize(temp[lims_y[0]:lims_y[1],lims_x[0]:lims_x[1]],(0,0),fx=scale,fy=scale), cv2.TM_CCORR_NORMED)  
                        
                        #store the results 
                        res[index,0] = correl    
                        
                    #select the angle that provided the largest correlation     
                    select_val = angles[np.argmax(res)]
                    
                    #store the results 
                    results = np.append(results, select_val) 
                    #print('thus')
                    
    #return the angles 
    return results    


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


def initial_conditions(ListofFiles,foldername, FaceCenter, threshold):
    
    #reaf first image of the list to estimate initial conditions
    image = cv2.imread(os.path.join(foldername,ListofFiles[0]),0)  #last 0 means gray scale
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
    #in the right
    st_right = [coinc[1][0], coinc[0][0]]
    #and left
    st_left = [coinc[1][1], coinc[0][1]]
    
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
    
#    l_bar = FaceCenter[1]*0.75
#    dy_right= l_bar*np.tan(angle_right)
#    
#    print(FaceCenter,[p,q],FaceCenter[0]-l_bar, FaceCenter[1]-dy_right)
    
    
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
    
#    l_bar = FaceCenter[1]*0.75
#    dy_left= l_bar*np.tan(angle_left)
#    
#    print(FaceCenter,[p,q],FaceCenter[0]+l_bar, FaceCenter[1]-dy_left)
    
    return np.array([angle_right, angle_left])


class FramesAnalysis(QObject):
    
    finished = pyqtSignal()
    Results = pyqtSignal(object, object, float, int)
    
    def __init__(self,pool,folder_name,ListofFiles, FaceCenter, RightROI, LeftROI, threshold, angles, parallel, resultsInfo):
        super(FramesAnalysis, self).__init__()
        
        self._foldername = folder_name
        self._ListofFiles = ListofFiles
        self._FaceCenter = FaceCenter
        self._RightROI = RightROI
        self._LeftROI = LeftROI
        self._threshold = threshold
        self._angles = angles
        self._parallel = parallel
        self._resultsInfo = resultsInfo
        self._Pool = pool
        


    @pyqtSlot()
    def ProcessFrames(self):
        st_time = time.time()  
        Files = self._ListofFiles   
        

        #compute initial conditions on left and right sides
        init_cond = initial_conditions(Files, self._foldername, self._FaceCenter, self._threshold)

        rotation_angle = self._resultsInfo._rotation_angle  #get the desired rotation angle 
        
        #is the processing going to happen in parallel?
        if self._parallel._MultiProcessor:
            agents = self._parallel._NumAgents
        else:
            agents = None
         
       
        #if doing it in parallel then split the list of files to analize so 
        #that it can be run in different processors at the same time 
        if agents is not None:
            div_number = int(np.ceil(len(Files)/agents))  #this tells in how many sub-list the original list can be divided
            if div_number <= 1: #if div_number <=1 then parallel processing is not needed
                agents = None
       
        if agents is not None:
            #use parallel processing if the user requested it and if the list can be divided in more that one
            
            #split the number of elements according to the number of agents 
            if div_number*agents == len(Files):
                #if the number of files can be divided into exact number of splits then do it
                FilesforProcessing = np.reshape(Files,(agents,div_number))                          
            else:
                #if not, then add 'None' to the list until in can be divided 
                #redefine the number of agents...
                agents = int(np.ceil(len(Files)/div_number))
                extra = [None]*(div_number*agents - len(Files))
                Files.extend(extra)
                FilesforProcessing = np.reshape(Files,(agents,div_number))

      
            #now we need to append the first element of each split to the tail of the 
            #previous split. This will allow us to concatenate all the angles betwee
            #frames. 
            FilesforProcessing = np.c_[FilesforProcessing,np.zeros([agents,1])]                
            for k in range(0,agents-1):
                FilesforProcessing[k,-1] = FilesforProcessing[k+1,0]
            FilesforProcessing[agents-1,-1] = FilesforProcessing[agents-1,-2] 

            #print(FilesforProcessing) 
            #print(agents)
                    
            #right side                        
            
            #run this in parallel 
            #create a new variable that zips everything that needs to be sent to
            #the function that will be run in parallel, this is to avoid some 
            #limitations with the parallel processing tool
            
            
            pool = self._Pool #Make a local copy Pool(processes=agents)

            if self._resultsInfo._AnalizeResults == 'Both': #analize both sides of the face
            
                
                it_right = pool.imap(partial(rot_estimation, ExtraInfo = zip([self._foldername], [self._FaceCenter], 
                                [self._RightROI], [self._LeftROI],
                                [self._threshold], [self._angles], ['Right'], [rotation_angle])),FilesforProcessing)
                
                it_left = pool.imap(partial(rot_estimation, ExtraInfo = zip([self._foldername], [self._FaceCenter], 
                                [self._RightROI], [self._LeftROI],
                                [self._threshold], [self._angles], ['Left'], [rotation_angle])),FilesforProcessing)
                res_right= []
                res_left= []
                for x in it_right:
                    res_right.append(x)
                for y in it_left:
                    res_left.append(y)
                               
                pool.terminate()
                pool.join()   
                duration = time.time()-st_time  
                
                results_right = np.zeros((1,1),dtype = np.float64)
                for k in range(0,len(res_right)):
                    temp = res_right[k]
                    results_right = np.append(results_right,temp[1:]) 
                  
                      
                results_left = np.zeros((1,1),dtype = np.float64)
                for k in range(0,len(res_left)):
                    temp = res_left[k]
                    results_left = np.append(results_left,temp[1:]) 
                      
                #put everythin togehter 
                results= np.c_[results_right, results_left]  
                
            elif self._resultsInfo._AnalizeResults == 'Right': #only analize the right side of the face 
                
                it_right = pool.imap(partial(rot_estimation, ExtraInfo = zip([self._foldername], [self._FaceCenter], 
                                [self._RightROI], [self._LeftROI],
                                [self._threshold], [self._angles], ['Right'], [rotation_angle])),FilesforProcessing)

                res_right= []
                for x in it_right:
                    res_right.append(x)
                               
                pool.terminate()
                pool.join()   
                duration = time.time()-st_time  
                
                results_right = np.zeros((1,1),dtype = np.float64)
                for k in range(0,len(res_right)):
                    temp = res_right[k]
                    results_right = np.append(results_right,temp[1:]) 
                    
    
                #put everythin togehter 
                results= np.c_[results_right, np.zeros(results_right.shape)]
                
            elif self._resultsInfo._AnalizeResults == 'Left': #analize the left side of the face
                            
                it_left = pool.imap(partial(rot_estimation, ExtraInfo = zip([self._foldername], [self._FaceCenter], 
                                [self._RightROI], [self._LeftROI],
                                [self._threshold], [self._angles], ['Left'], [rotation_angle])),FilesforProcessing)
                res_left= []
                for y in it_left:
                    res_left.append(y)
                               
                pool.terminate()
                pool.join()   
                duration = time.time()-st_time  
                                 
                results_left = np.zeros((1,1),dtype = np.float64)
                for k in range(0,len(res_left)):
                    temp = res_left[k]
                    results_left = np.append(results_left,temp[1:])   
                    
    
                #put everythin togehter 
                results= np.c_[np.zeros(results_left.shape), results_left]  
                
            #remove last element which is zero
            results = results[:-1]   
                

        else: #no parallel processing... seriously!!!
            agents = 1
            st_time = time.time()  
            FilesforProcessing = Files
            if self._resultsInfo._AnalizeResults == 'Both': #analize both sides of the face
                
                results_right = rot_estimation(FilesforProcessing, zip([self._foldername], [self._FaceCenter], 
                                [self._RightROI], [self._LeftROI],
                                [self._threshold], [self._angles], ['Right'], [rotation_angle]))
                #print('Right_np')
                
                
                results_left = rot_estimation(FilesforProcessing, zip([self._foldername], [self._FaceCenter], 
                                [self._RightROI], [self._LeftROI],
                                [self._threshold], [self._angles], ['Left'], [rotation_angle]))
                
                #print('Left_np')
                duration = time.time()-st_time 
                
                #put everythin togehter 
                results= np.c_[results_right, results_left] 
                
            elif self._resultsInfo._AnalizeResults == 'Right': #only analize the right side of the face
                
                results_right = rot_estimation(FilesforProcessing, zip([self._foldername], [self._FaceCenter], 
                                [self._RightROI], [self._LeftROI],
                                [self._threshold], [self._angles], ['Right'], [rotation_angle]))
                

                duration = time.time()-st_time 
                
                #put everythin togehter 
                results= np.c_[results_right, np.zeros(results_right.shape)]
                
            elif self._resultsInfo._AnalizeResults == 'Left': #analize the left side of the face
                
                results_left = rot_estimation(FilesforProcessing, zip([self._foldername], [self._FaceCenter], 
                                [self._RightROI], [self._LeftROI],
                                [self._threshold], [self._angles], ['Left'], [rotation_angle]))
                
                #print('Left_np')
                duration = time.time()-st_time 
                
                #put everythin togehter 
                results= np.c_[np.zeros(results_left.shape), results_left]
        
                                                                                            
        #submit results to the main window 
        self.Results.emit(results, init_cond, duration, agents)
        #now inform that is over
        self.finished.emit()
        
    
        
class AnalysisWindow(QDialog):
        
        
    def __init__(self, List=None, folder= None, RightROI=None, LeftROI=None, FaceCenter=None, threshold = None, angles = None, Parallel= None, SaveInfo=None, ResultsInfo= None):
        super(AnalysisWindow, self).__init__()
        
        #take all the info and store it locally. 
        self._List= List
        self._folder = folder
        self._FaceCenter = FaceCenter
        self._RightROI = RightROI
        self._LeftROI = LeftROI
        self._threshold = threshold
        self._angles = angles
        self._Parallel = Parallel
        self._SaveInfo = SaveInfo
        self._ResultsInfo = ResultsInfo
        

         # create Thread  to take care of video processing    
        self.thread_frames = QtCore.QThread()  # no parent!

        self.Canceled = True #informs if the operation was canceled
        
        self.FrameAna = None #this is what takes care of the processing
        
        self._Pool = 0 #this is the processor pool, if no parallel process then is just 0
        
        self.Processing = True #controls the poor's man "progress bar"
        
        self.Canceled = True #informs if the operation was canceled
        
        self._duration = 0
        self._agents = 1 
        self._results = None
        self._init_cond = None
        self._hasAngle = None #variable that will inform if there is angle information for a particular frame

        self.initUI()
        
    def initUI(self):
        
        self.setWindowTitle('Whisking Angle Estimation')
        scriptDir = os.getcwd()
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'face_icon.ico'))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() |
                              QtCore.Qt.WindowSystemMenuHint |
                              QtCore.Qt.WindowMinMaxButtonsHint)
        
        
        #self.main_Widget = QtWidgets.QWidget(self)
        
        spacerh = QtWidgets.QWidget(self)
        spacerh.setFixedSize(20,0)
        
        spacerv = QtWidgets.QWidget(self)
        spacerv.setFixedSize(0,20)
        
        
        
        
        
        
        newfont = QtGui.QFont("Times", 12)
        
        self._label1 = QLabel('Processing, this might take a few minutes')
        self._label1.setFont(newfont)
        self._label1.setFixedWidth(300)
        self._label1.setAlignment(QtCore.Qt.AlignCenter)

        self._label2 = QLabel('')
        self._label2.setFont(QtGui.QFont("Times", 25))
        self._label2.setFixedWidth(300)
        self._label2.setAlignment(QtCore.Qt.AlignCenter)
        
        self._label3 = QLabel('')
        self._label3.setFont(newfont)
        self._label3.setFixedWidth(300)
        self._label3.setAlignment(QtCore.Qt.AlignCenter)
            
        self._CancelButton = QPushButton('&Cancel', self)
        self._CancelButton.setFixedWidth(100)
        self._CancelButton.setFont(newfont)
        self._CancelButton.clicked.connect(self.Cancel)
        
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self._CancelButton)
        
        
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._label1)
        layout.addWidget(self._label2)
        layout.addWidget(self._label3)
        layout.addLayout(buttonLayout)
        

        
        self.setLayout(layout)

        #fix the size, the user cannot change it 
        self.resize(self.sizeHint())
        self.setFixedSize(self.size())
        
        self.initializition()
        self.Done()
        
        #self.show()


    def initializition(self):
        #initialize some elements that will be submited to the additional thread
        self._selectedList = self._List[self._ResultsInfo._InitFrame-1:self._ResultsInfo._EndFrame:self._ResultsInfo._subSampling]
        agents = None
        if self._Parallel._MultiProcessor:
            agents = self._Parallel._NumAgents
            if agents is not None:
                div_number = int(np.ceil(len(self._selectedList)/agents))  #this tells in how many sub-list the original list can be divided
            if div_number <= 1: #if div_number <=1 then parallel processing is not needed
                agents = None
       
        if agents is not None:
            #use parallel processing if the user requested it and if the list can be divided in more that one
            
            #split the number of elements according to the number of agents 
            if div_number*agents == len(self._selectedList):
                agents = agents                          
            else:
                #if not, then add 'None' to the list until in can be divided 
                #redefine the number of agents...
                #This needs to be improved at some point so that it doesn't change the number of agents!!!
                agents = int(np.ceil(len(self._selectedList)/div_number))

            #initianlize the Pool of processors
            self._Pool = Pool(processes=agents)
            
        return 
            

    def Done(self):
        #move the frames processing to another thread 
        self.FrameAna = FramesAnalysis(self._Pool, self._folder, self._selectedList, self._FaceCenter, self._RightROI, self._LeftROI, self._threshold, self._angles, self._Parallel, self._ResultsInfo)
        #move worker to new thread
        self.FrameAna.moveToThread(self.thread_frames)
        #start the new thread where the landmark processing will be performed
        self.thread_frames.start() 
        #Connect Thread started signal to Worker operational slot method
        self.thread_frames.started.connect(self.FrameAna.ProcessFrames)
        #connect signal emmited by landmarks to a function
        self.FrameAna.Results.connect(self.GetResultsFromProcess)
        #define the end of the thread
        self.FrameAna.finished.connect(self.thread_frames.quit)
        
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.UpdateProgressBar)
        self.timer.start(250)
        
        return 


    def GetResultsFromProcess(self, results, init_cond, duration, agents):
        self._agents = agents
        self._results = results
        self._init_cond = init_cond
        self._duration = duration
        
        
        #if finilized then do signal analysis 
        self.SignalAnalysis()
             
        return
    
    def SignalAnalysis(self):
        FPS = self._ResultsInfo._camera_fps
        SubSampling = self._ResultsInfo._subSampling
        

        Fs= (FPS)/SubSampling #Sampling Frequency 
        Niq_Fs = Fs/2 #Niquist Frequency (Half of sampling Frequency)
        
        low_pass_frequency = Niq_Fs/2 - Niq_Fs*0.1 #low-pass filter at half the niquist frequency minus 10% to remove high-frequency noise 
        
        high_pass_frequency = Niq_Fs*0.002  #high-pass filter at 0.2% of the niquist frequency to remove tren added by the numerical integration
        
        
        #filters
        b, a = signal.butter(2, low_pass_frequency/Niq_Fs, btype = 'low')
        c, d = signal.butter(2, high_pass_frequency/Niq_Fs, btype = 'high')
        if self._ResultsInfo._AnalizeResults == 'Both':            
            #Right Side
            temp = None
            temp = signal.lfilter(b, a, self._results[:,0]) #low pass to remove noise
            temp =  np.cumsum(temp) #cumsum to compute overall angle change
            self._results[:,0] = signal.lfilter(c, d, temp) #high pass to remove trend 
            #Left Side
            temp = None
            temp = signal.lfilter(b, a, self._results[:,1])#low pass to remove noise
            temp =  np.cumsum(temp) #cumsum to compute overall angle change
            self._results[:,1] =  signal.lfilter(c, d, temp) #high pass to remove trend
            
        elif self._ResultsInfo._AnalizeResults == 'Right':
            #Right Side
            temp = None
            temp = signal.lfilter(b, a, self._results[:,0]) #low pass to remove noise
            temp =  np.cumsum(temp) #cumsum to compute overall angle change
            self._results[:,0] = signal.lfilter(c, d, temp) #high pass to remove trend 
       
        elif self._ResultsInfo._AnalizeResults == 'Left':
            #Left Side
            temp = None
            temp = signal.lfilter(b, a, self._results[:,1])#low pass to remove noise
            temp =  np.cumsum(temp) #cumsum to compute overall angle change
            self._results[:,1] =  signal.lfilter(c, d, temp) #high pass to remove trend 
        
        
        #if requested, then save data in a csv file
        #3/11/2018 -> changed self._ResultsInfo._InitFrame-1 to self._ResultsInfo._InitFrame, i don't know if that will work....
        time_vector = np.linspace(self._ResultsInfo._InitFrame, self._ResultsInfo._EndFrame-1, len(self._results))# np.arange(self._ResultsInfo._InitFrame-1,self._ResultsInfo._InitFrame+len(self.results),self._ResultsInfo._subSampling)
        self._results = np.c_[time_vector*(1/Fs), self._results+self._init_cond]
    
    
        #we need to inform to the main program what frames have been processed and what frames haven't 
        #this will simplify presentation of results
        self._hasAngle = [None]*len(self._List) 
        self._hasAngle[self._ResultsInfo._InitFrame-1:self._ResultsInfo._EndFrame:self._ResultsInfo._subSampling] = self._results
            
        self.Processing = False
        #update progress bar one last time and ask user to close it 
        self.UpdateProgressBar()     

        
        return
        

        
        

        
    def UpdateProgressBar(self):
        
        if self.Processing:
            read = self._label2.text()
            if read =='':           
                self._label2.setText('.  ')
            elif read == '.  ':
                self._label2.setText('.. ')
            elif read == '.. ':
                self._label2.setText('...')
            elif read == '...':
                self._label2.setText('')
                
                
        else:
            self._label1.setText('DONE')           
            self._label2.setFont(QtGui.QFont("Times", 12))            
            if self._agents > 1: 
                self._label2.setText('Processing {a} frames using {b} agents'.format(a=len(self._results),b=self._agents))
            else:
                self._label2.setText('Processing {a} frames using {b} agent'.format(a=len(self._results),b=self._agents))
                    
            self._label3.setText('took {b} s'.format( b=np.round(self._duration,3)))

            self._CancelButton.setText('Close')
#
#        

    def Cancel(self):
        #terminate the processors pool and the extra thread (this will prevent the program from crashing--I hope...) 
        if self._Pool:
            self._Pool.terminate()
            self._Pool.join() 
            self._Pool = None
        if self.thread_frames.isRunning():
            self.thread_frames.quit            
            
        self.close()  

       
    def closeEvent(self, event):
        
        if self.Processing is False:
            self.Canceled = False #process ended normaly, wasn't canceled by the user
        else:
            self.Canceled = True #process was canceled by the user
            
        #before closing this window, terminate the processors pool and the extra thread (this will prevent the program from crashing--I hope...) 
        if self._Pool:
            self._Pool.terminate()
            self._Pool.join() 
        if self.thread_frames.isRunning():
            self.thread_frames.quit

        event.accept()

        
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
#    if not QtWidgets.QApplication.instance():
#        app = QtWidgets.QApplication(sys.argv)
#    else:
#        app = QtWidgets.QApplication.instance()
       
    GUI = AnalysisWindow()
    GUI.show()
    app.exec_()
    

