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

from multiprocessing import Pool

#from pathos.multiprocessing import ProcessingPool as Pool
from functools import partial

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QPushButton, QDialog, QProgressBar
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
    foldername, center, RightROI, LeftROI, threshold, angles, Side = zip(*ExtraInfo)   
    
    
    foldername = foldername[0]  
    center = center[0]
    RightROI = RightROI[0]
    LeftROI = LeftROI[0]
    threshold = threshold[0]

    Side = Side[0]
    angles = angles[0]

    zero_pos = np.where(angles == 0)[0]

    angles_neg = angles[0:int(zero_pos[0])+1]

    angles_pos = angles[int(zero_pos[0]):-1] 
    
    
    #read first image in gray scale
    image = cv2.imread(os.path.join(foldername,ListofFiles[0]),0)  #last 0 means gray scale
    
    #remove the first element from the list
    ListofFiles = np.delete(ListofFiles,[0])
    
    h_orig, w_orig = image.shape #original shape 
    #we have to do different operation depending on what side 
    if Side == 'Right':
        ROI = RightROI
        image = image[:,0:center[0]] #take right side
    else:
        ROI = LeftROI
        ROI = [2*center[0],0]-ROI  #mirror the left ROI to the right 
        ROI[:,1]=abs(ROI[:,1])  #correct the minus sign in the y column
        image = cv2.flip(image,1) #mirror it
        image = image[:,0:w_orig-center[0]]  #take left side
    
    
    #apply threshold
    image[image>threshold] = 255
    #invert image to improve results
    image = cv2.bitwise_not(image)

    
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
            
            if Side == 'Right':
                image = image[:,0:center[0]] #take right side
            else:
                image = cv2.flip(image,1) #mirror it
                image = image[:,0:w_orig-center[0]]  #take left side
                

            #apply threshold
            image[image>threshold] = 255
            #invert image to improve results
            image = cv2.bitwise_not(image)
            
            #start the process ...
            
            #apply the mask to select ROI in the previous frame
            old_temp = np.zeros([h,w], np.uint8)     
            cv2.bitwise_and(old_image,mask,old_temp) 
            
            if counter == 0:
                #first run using all angles 
                res = np.zeros((len(angles),1),dtype = np.float64)

                
                old_small_image= cv2.resize(old_temp,(0,0),fx=scale,fy=scale)
                
                
                for index,angle in enumerate(angles):
                    
                    #rotate the image by angles
                    M = cv2.getRotationMatrix2D(tuple(center), angle, 1.0)
                    rotated = cv2.warpAffine(image, M, (w, h))
                    #apply the mask to selected ROI in rotated image 
                    temp = np.zeros([h,w], np.uint8)     
                    cv2.bitwise_and(rotated,mask,temp) 
    
                    #find the correlation between the previous frame and the rotate version of the current frame                                                     
                    correl = cv2.matchTemplate(old_small_image, cv2.resize(temp,(0,0),fx=scale,fy=scale), cv2.TM_CCORR_NORMED)  
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
                    
                    old_small_image = cv2.resize(old_temp,(0,0),fx=0.5,fy=0.5)
                    
                    for index,angle in enumerate(angles_neg):
                        
                        #rotate the frame
                        M = cv2.getRotationMatrix2D(tuple(center), angle, 1.0)
                        rotated = cv2.warpAffine(image, M, (w, h))
                        
                        #apply the mask to selected ROI in rotated image 
                        temp = np.zeros([h,w], np.uint8)     
                        cv2.bitwise_and(rotated,mask,temp) 
                       
        
                        #find the correlation between the previous frame and the rotate version of the current frame                                                     
                        correl = cv2.matchTemplate(old_small_image, cv2.resize(temp,(0,0),fx=scale,fy=scale), cv2.TM_CCORR_NORMED)  
                        
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
                    
                    old_small_image = cv2.resize(old_temp,(0,0),fx=0.5,fy=0.5)
                    
                    for index,angle in enumerate(angles_pos):
                        
                        #rotate the frame
                        M = cv2.getRotationMatrix2D(tuple(center), angle, 1.0)
                        rotated = cv2.warpAffine(image, M, (w, h))
                        
                        #apply the mask to selected ROI in rotated image 
                        temp = np.zeros([h,w], np.uint8)     
                        cv2.bitwise_and(rotated,mask,temp) 
                       
        
                        #find the correlation between the previous frame and the rotate version of the current frame                                                     
                        correl = cv2.matchTemplate(old_small_image, cv2.resize(temp,(0,0),fx=scale,fy=scale), cv2.TM_CCORR_NORMED)  
                        
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
                    
                    old_small_image = cv2.resize(old_temp,(0,0),fx=0.5,fy=0.5)
                    
                    for index,angle in enumerate(angles):
                        
                        #rotate the frame
                        M = cv2.getRotationMatrix2D(tuple(center), angle, 1.0)
                        rotated = cv2.warpAffine(image, M, (w, h))
                        
                        #apply the mask to selected ROI in rotated image 
                        temp = np.zeros([h,w], np.uint8)     
                        cv2.bitwise_and(rotated,mask,temp) 
                       
        
                        #find the correlation between the previous frame and the rotate version of the current frame                                                     
                        correl = cv2.matchTemplate(old_small_image, cv2.resize(temp,(0,0),fx=scale,fy=scale), cv2.TM_CCORR_NORMED)  
                        
                        #store the results 
                        res[index,0] = correl    
                        
                    #select the angle that provided the largest correlation     
                    select_val = angles[np.argmax(res)]
                    
                    #store the results 
                    results = np.append(results, select_val) 
                    #print('thus')
                    
    #return the angles 
    return results    

        
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
                
        self.Processing= True
        
        self._results = None
        self._duration = 0
    
        self.initUI()
        
    def initUI(self):
        
        self.setWindowTitle('Whisking Angle Estimation')
        scriptDir = os.getcwd()
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'face_icon.ico'))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() |
                              QtCore.Qt.WindowSystemMenuHint |
                              QtCore.Qt.WindowMinMaxButtonsHint)
        
        
        self.main_Widget = QtWidgets.QWidget(self)
        
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
        self._label2.setFont(newfont)
        self._label2.setFixedWidth(300)
        self._label2.setAlignment(QtCore.Qt.AlignCenter)
        
        self._label3 = QLabel('')
        self._label3.setFont(QtGui.QFont("Times", 20))
        self._label3.setFixedWidth(300)
        self._label3.setAlignment(QtCore.Qt.AlignCenter)
        
        
        
        self._ContinueButton = QPushButton('&Continue', self)
        self._ContinueButton.setFixedWidth(100)
        self._ContinueButton.setFont(newfont)
        self._ContinueButton.clicked.connect(self.Continue)
            
        self._CancelButton = QPushButton('&Cancel', self)
        self._CancelButton.setFixedWidth(100)
        self._CancelButton.setFont(newfont)
        self._CancelButton.clicked.connect(self.Cancel)
        
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self._ContinueButton)
        buttonLayout.addWidget(self._CancelButton)
        
        
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._label1)
        layout.addWidget(self._label2)
        layout.addWidget(self._label3)
        layout.addWidget(spacerv)
        layout.addLayout(buttonLayout)
        

        
        self.setLayout(layout)

        #fix the size, the user cannot change it 
        self.resize(self.sizeHint())
        self.setFixedSize(self.size())
        
        
        
        
        #self.show()
        
    def Continue(self):
        if self.Processing:
            self.ProcessFrames()
        else:
            self.close()    
        
    def UpdateProgressBar(self):
        
        if self.Processing:
            read = self._label3.text()
            if read =='':           
                self._label3.setText('.  ')
            elif read == '.  ':
                self._label3.setText('.. ')
            elif read == '.. ':
                self._label3.setText('...')
            elif read == '...':
                self._label3.setText('')
                
                
        else:
            self._label3a.setText('DONE')
            self._label3.setFont(QtGui.QFont("Times", 12))
            self._label3.setText('Computation lasted for: {0}s'.format(self._duration))
            
        
            self._ContinueButton.setText('Close')
            self._CancelButton.setEnabled(False)

    def ProcessFrames(self):

        Files = self._List
        Files = Files[self._ResultsInfo._InitFrame-1:self._ResultsInfo._EndFrame:self._ResultsInfo._subSampling]        
        
        
        #is the processing going to happen in parallel?
        if self._Parallel._MultiProcessor:
            agents = self._Parallel._NumAgents
        else:
            agents = None
        
        
       
        #if doing it in parallel then split the list of files to analize so 
        #that it can be run in different processors at the same time 
        if agents is not None:
            div_number = int(np.floor(len(Files)/agents))  #this tells in how many list the original list can be divided
            if div_number <= 1: #if div_number <=1 then parallel processing is not worthed
                agents = None

        if agents is not None:
            #use parallel processing if the user requested it and if the list can be divided in more that one
            

            if div_number*agents == len(Files):
            
                FilesforProcessing = np.reshape(Files,(div_number, agents))
                
            else:
                
                FilesforProcessing = np.reshape(Files[0:div_number*agents],(agents,div_number)).T
                extra = [None]*div_number
                extra[0:len(Files)-div_number*agents] = Files[div_number*agents-len(Files):]
                
                FilesforProcessing = np.column_stack((FilesforProcessing,extra))
                FilesforProcessing = np.row_stack((FilesforProcessing,[None]*(agents+1))) 
                
                for k in range(0,agents):
                    FilesforProcessing[-1,k] = FilesforProcessing[0,k+1]
                    
            #right side                        
            
            #run this in parallel 
            #create a new variable that zips everything that needs to be sent to
            #the function that will be run in parallel, this is to avoid some 
            #limitations with the parallel processing tool

            ExtraInformation_right = zip([self._folder], [self._FaceCenter], 
                            [self._RightROI], [self._LeftROI],
                            [self._threshold], [self._angles], ['Right'])

            ExtraInformation_left = zip([self._folder], [self._FaceCenter], 
                            [self._RightROI], [self._LeftROI],
                            [self._threshold], [self._angles], ['Left'])

            st_time = time.time()  
            pool = Pool(processes=agents)
            it_right = pool.imap(partial(rot_estimation, ExtraInfo = ExtraInformation_right),FilesforProcessing.T)
            it_left = pool.imap(partial(rot_estimation, ExtraInfo = ExtraInformation_left),FilesforProcessing.T)
            res_right= []
            res_left= []
            for x in it_right:
                res_right.append(x)
            for y in it_left:
                res_left.append(y)
                
            pool.terminate()    
            self._duration = time.time()-st_time    
            
            print('Right_p')
            results_right = np.zeros((1,1),dtype = np.float64)
            for k in range(0,len(res_right)):
                temp = res_right[k]
                results_right = np.append(results_right,temp[1:]) 
  
                
            print('Left_p')
            results_left = np.zeros((1,1),dtype = np.float64)
            for k in range(0,len(res_left)):
                temp = res_left[k]
                results_left = np.append(results_left,temp[1:])   

           

        else: #no parallel processing... seriously!!!
            FilesforProcessing = Files
            #Right          
            ExtraInformation = zip([self._folder], [self._FaceCenter], 
                            [self._RightROI], [self._LeftROI],
                            [self._threshold], [self._angles], ['Right'])
            results_right = rot_estimation(FilesforProcessing, ExtraInformation)
            #left
            
            ExtraInformation = zip([self._folder], [self._FaceCenter], 
                            [self._RightROI], [self._LeftROI],
                            [self._threshold], [self._angles], ['Left'])
            
            results_left = rot_estimation(FilesforProcessing, ExtraInformation)
                                               
        self._results= np.c_[results_right, results_left]
        
        if self._results:
            self.Processing = False
            self.updateProgressBar()
       

    def Cancel(self):
        
        self._Continue = False
        
#        if self.FrameAna is not None:
#            self.FrameAna.cap.release()
#        if self.thread_frames.isRunning():
#            self.thread_frames.quit

            
        self.close()  

       
    def closeEvent(self, event):

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
    

