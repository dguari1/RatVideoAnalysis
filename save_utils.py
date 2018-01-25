# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 16:29:42 2018

@author: guarind
"""

import numpy as np
import os

def SaveTXT(name = None, RightROI=None, LeftROI=None, FaceCenter=None, threshold = None):
    
    head,tail = os.path.split(name)  
    #print(RightROI, LeftROI,FaceCenter,threshold)
    #tempfiles    
    nameFaceCenter = os.path.join(head, 'temp_FaceCenter.txt')
    np.savetxt(nameFaceCenter, np.array([FaceCenter]), delimiter=',',fmt='%i', newline='\r\n')
    
    nameThreshold = os.path.join(head, 'temp_Threshold.txt')
    if threshold is not None:       
        np.savetxt(nameThreshold, np.array([threshold]), delimiter=',',fmt='%i', newline='\r\n')
    else:
        np.savetxt(nameThreshold, np.array([0]), delimiter=',',fmt='%i', newline='\r\n')
    
    nameRightROI = os.path.join(head, 'temp_RightROI.txt')
    np.savetxt(nameRightROI, RightROI, delimiter=',',fmt='%i', newline='\r\n')
    
    nameLeftROI = os.path.join(head, 'temp_LeftROI.txt')
    np.savetxt(nameLeftROI, LeftROI, delimiter=',',fmt='%i', newline='\r\n')
    
    #if the file exists then remove it -- sorry
    if os.path.isfile(name):
        os.remove(name)
    
    
    with open(name,'a') as f:
        #start writing content in the file 
        #(\n indicates new line), (# indicates that the line will be ignored)
        f.write('# Face Center [x,y] { \n')
        with open(nameFaceCenter,'r') as temp_f:
            f.write(temp_f.read())
        f.write('# } \n')
                
        f.write('# Threshold { \n')
        with open(nameThreshold,'r') as temp_f:
            f.write(temp_f.read())
        f.write('# } \n')   
                
        f.write('# Right ROI { \n')
        with open(nameRightROI,'r') as temp_f:
            f.write(temp_f.read())
        f.write('# } \n') 
                
        f.write('# Left ROI { \n')
        with open(nameLeftROI,'r') as temp_f:
            f.write(temp_f.read())
        f.write('# } \n')
    
    
    os.remove(nameFaceCenter)
    os.remove(nameThreshold)
    os.remove(nameRightROI)
    os.remove(nameLeftROI)
    
    
def ReadTXT(name):
 
    elements_to_locate=['Face Center', 'Threshold', 'Right ROI', 'Left ROI']
    findCenter = False
    findThreshold = False
    findRightROI = False
    findLeftROI = False
    
    FaceCenter = np.zeros((1,2),dtype=int)
    Threshold = np.zeros((1,1),dtype=int)
    RightROI=[]
    LeftROI=[]
    
    
    with open(name, 'r') as file:
        for line in file:  
            if line[0] =='#':
                for k,element in enumerate(elements_to_locate):
                    if element in line:
                        if k == 0 :
                            findCenter = True
                            findThreshold = False
                            findRightROI = False
                            findLeftROI = False
                        elif k == 1:
                            findCenter = False
                            findThreshold = True
                            findRightROI = False
                            findLeftROI = False
                        elif k == 2:
                            findCenter = False
                            findThreshold = False
                            findRightROI = True
                            findLeftROI = False
                        elif k == 3:
                            findCenter = False
                            findThreshold = False
                            findRightROI = False
                            findLeftROI = True
                            
                        break
                    else:
                        findCenter = False
                        findThreshold = False
                        findRightROI = False
                        findLeftROI = False 
                        
     
            if findCenter and line[0] != '#':
                temp=(line[:]).split(',')
                FaceCenter[0,0]=int(temp[0])
                FaceCenter[0,1]=int(temp[1])
    
            
            if findThreshold and line[0] != '#':
                if int(line) == 0:
                    Threshold = None
                else:
                    Threshold = int(line)
                
            if findRightROI and line[0] != '#':
                temp=(line[:]).split(',')
                RightROI.append([int(temp[0]),int(temp[1])])
                
            if findLeftROI and line[0] != '#':
                temp=(line[:]).split(',')
                LeftROI.append([int(temp[0]),int(temp[1])])
         
    
    RightROI = np.asarray(RightROI)
    LeftROI = np.asarray(LeftROI)     

    return FaceCenter, Threshold, RightROI, LeftROI                  

            
            
        