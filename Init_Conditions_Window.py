# -*- coding: utf-8 -*-
"""
Created on Fri Dec 14 15:42:50 2018

@author: GUARIND
"""

import os
import sys
import cv2
import numpy as np


from ImageViewer import ImageViewer

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtWidgets import QLabel, QPushButton, QDialog, QSpinBox, QCheckBox,QLineEdit, QToolButton,QPlainTextEdit
#from PyQt5.QtCore import pyqtSlot
#from PyQt5.QtCore import QFile, QTextStream

from center_detection import find_center_whiskerpad
from center_detection import find_center_eyes_with_click
from ComputeInitialConditions import initial_conditions

        
class InitConditionsWindow(QDialog):
        
    
    def __init__(self, Image=None, FileList = None, Folder = None, FaceCenter =  None, InitFrame =  None, threshold = None, EyesCenter = None):
        super(InitConditionsWindow, self).__init__()
        
#        self._scene = QtWidgets.QGraphicsScene(self)
#        self.setScene(self._scene)
        
        #FileList = ['Basler acA800-510uc (22501173)_20180523_154539113_0001.tiff', 'Basler acA800-510uc (22501173)_20180523_154539113_0002.tiff', 'Basler acA800-510uc (22501173)_20180523_154539113_0003.tiff', 'Basler acA800-510uc (22501173)_20180523_154539113_0004.tiff', 'Basler acA800-510uc (22501173)_20180523_154539113_0005.tiff', 'Basler acA800-510uc (22501173)_20180523_154539113_0006.tiff', 'Basler acA800-510uc (22501173)_20180523_154539113_0007.tiff',  'Basler acA800-510uc (22501173)_20180523_154539113_0008.tiff', 'Basler acA800-510uc (22501173)_20180523_154539113_0009.tiff']
        #Folder = r'G:\VideoForWhisking\test'
#        RightROI = np.array([[368,387],[324,329],[299,261],[230,157],[196,78],[ 21,77],[16,581],[373,585]])
#        LeftROI = np.array([[440,387],[484,329],[509,261],[578,157],[612,78],[787,77],[792,581],[435,585]])
        #FaceCenter = np.array([404,302])
        #InitFrame = 1
        #ff = r'G:\VideoForWhisking\2018_05_23\background\Basler acA800-510uc (22501173)_20180523_145714943_0001.tiff'
        #threshold = cv2.imread(ff,0)
        
        self._Folder = Folder
        self._FileList = FileList
        self._InitFrame = 1  
        self._FaceCenter = FaceCenter
        self._EyesCenter = EyesCenter
        self._threshold = threshold 
        
        self._Image = Image
        
        self._RightEyePosition = []
        self._LeftEyePosition = []
        self._SnoutPosition = []
        self._rad = []
        
        self._hasAngleTempRight = [[False],[False]] #a temporary version of the variable self._hasAngle
        self._hasAngleTempLeft = [[False],[False]]  #a temporary version of the variable self._hasAngle
        self._temp_storage_right = [[None],[None]]
        self._temp_storage_left = [[None],[None]]
        
        self._rightAngle = None
        self._leftAngle = None
        self._Initial_Conditions = np.array([None, None])
        
        self.initUI()
        

        
    def initUI(self):
        
        self.setWindowTitle('Visualize Initial Conditions')
        scriptDir = os.getcwd()
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'face_icon.ico'))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() |
                              QtCore.Qt.WindowSystemMenuHint |
                              QtCore.Qt.WindowMinMaxButtonsHint)
                
        #Top part
        newfont = QtGui.QFont("Times", 12)
        
        self.label1 = QLabel('Initial Frame:')
        self.label1.setFont(newfont)
        self.label1.setFixedWidth(250)
        
        self._FramestoAnalizeInitEdit = QLineEdit(self)
        self._FramestoAnalizeInitEdit.setText(str(self._InitFrame)) 
        self._FramestoAnalizeInitEdit.setFont(newfont)
        self._FramestoAnalizeInitEdit.setFixedWidth(75)   
        validator = QtGui.QIntValidator(1, len(self._FileList))
        self._FramestoAnalizeInitEdit.setValidator(validator)
    

       
        #buttons       
        
        DoneButton = QPushButton('&Find Face Center', self)
        DoneButton.setFixedWidth(250)
        DoneButton.setFont(newfont)
        DoneButton.clicked.connect(self.Start)
        
        self.InitConditionsButton = QPushButton('&Compute Initial Conditions', self)
        self.InitConditionsButton.setFixedWidth(250)
        self.InitConditionsButton.setFont(newfont)
        self.InitConditionsButton.clicked.connect(self.Init_Conditions)
        self.InitConditionsButton.setEnabled(False)
        
        
        
        TopLayout = QtWidgets.QGridLayout()
        TopLayout.addWidget(self.label1, 0 , 0 ,1 ,1 )
        TopLayout.addWidget(self._FramestoAnalizeInitEdit, 0 , 1, 1, 1)
        TopLayout.addWidget(DoneButton, 1 , 0, 1,1)
        TopLayout.addWidget(self.InitConditionsButton, 2 , 0, 1,1)
        
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(DoneButton)
        
        self.RightEyeButton = QPushButton('&Right Eye', self)
        self.RightEyeButton.setFixedWidth(150)
        self.RightEyeButton.setFont(newfont)
        self.RightEyeButton.clicked.connect(self.Locate_Right_Eye)
        
        self.LeftEyeButton = QPushButton('&Left Eye', self)
        self.LeftEyeButton.setFixedWidth(150)
        self.LeftEyeButton.setFont(newfont)
        self.LeftEyeButton.clicked.connect(self.Locate_Left_Eye)
        self.LeftEyeButton.setEnabled(False)
        
        self.SnoutButton = QPushButton('&Snout', self)
        self.SnoutButton.setFixedWidth(150)
        self.SnoutButton.setFont(newfont)
        self.SnoutButton.clicked.connect(self.Locate_Snout)
        self.SnoutButton.setEnabled(False)
        

        
        ButtonBox = QtWidgets.QGroupBox('')
        ButtonBox.setFixedWidth(170)
        ButtonBox.setFixedHeight(120)
        ButtonBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        
        
        ButtonLayout = QtWidgets.QVBoxLayout()
        ButtonLayout.addWidget(self.RightEyeButton)
        ButtonLayout.addWidget(self.LeftEyeButton)
        ButtonLayout.addWidget(self.SnoutButton)
        #ButtonLayout.addWidget(self.WhiskersButton)
        ButtonLayout.addStretch(1)
        ButtonBox.setLayout(ButtonLayout)
        
        
        DoneButton = QPushButton('&Close', self)
        DoneButton.setFixedWidth(150)
        DoneButton.setFont(newfont)
        DoneButton.clicked.connect(self.Done)
        DoneButton.setEnabled(True)
        
        DoneButtonBox = QtWidgets.QGroupBox('')
        DoneButtonBox.setFixedWidth(170)
        DoneButtonBox.setFixedHeight(55)
        DoneButtonBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        DoneButtonLayout = QtWidgets.QVBoxLayout()
        DoneButtonLayout.addWidget(DoneButton)
        #ButtonLayout.addWidget(self.WhiskersButton)
        DoneButtonLayout.addStretch(1)
        DoneButtonBox.setLayout(DoneButtonLayout)
        
        
        
        ViewLayout = QtWidgets.QHBoxLayout()
        self.displayImage = ImageViewer()
        color = self.palette().color(QtGui.QPalette.Background)
        self.displayImage.setBackgroundBrush(color)
        
        ViewLayout.addWidget(self.displayImage)
        
        #layout = QtWidgets.QVBoxLayout()
        layout = QtWidgets.QGridLayout()
        layout.addLayout(TopLayout,0,0,1,3)
        #layout.addLayout(buttonLayout,1,1,1,1)
        layout.addWidget(ButtonBox,1,0,1,1)
        layout.addWidget(DoneButtonBox, 2,0,1,1)
        layout.addLayout(ViewLayout,1,1,3,3)
        #layout.addLayout(ButtonBox)

        
        self.setLayout(layout)

        

        #fix the size, the user cannot change it 
        #self.resize(self.sizeHint())
        #self.setFixedSize(self.size())
        
        self.setGeometry(100,100,300,300)
        self.show()   
        
        
    def Start(self):        
        #verify if the image viwer is empty. If then clean the image viwer
        if self._Image is not None:
            #remove all lines in the graph
            for item in self.displayImage._scene.items():
                if isinstance(item, QtWidgets.QGraphicsLineItem):
                    self.displayImage._scene.removeItem(item)
                if isinstance(item, QtWidgets.QGraphicsEllipseItem):
                    self.displayImage._scene.removeItem(item)
#        
        #Frames to analize
        Init_Frame =  int(self._FramestoAnalizeInitEdit.text())
        if Init_Frame == 0:
            QtWidgets.QMessageBox.warning(self, 'Error','Frame number must be larger than 0')
            return

        #read images from memory in gray format
        temp_image  = cv2.imread(os.path.join(self._Folder,self._FileList[Init_Frame-1]))
        temp_image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
        self._Image = cv2.cvtColor(temp_image , cv2.COLOR_BGR2GRAY)
        
        image = self._Image.copy()       
        image = image.astype(np.uint8)
            
        height, width = image.shape
        bytesPerLine = 1 * width
        #img_Qt = QtGui.QImage(self._ImageDos.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
        img_Qt = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_Indexed8)
        img_show = QtGui.QPixmap.fromImage(img_Qt) 
        self.setGeometry(self.geometry().topLeft().x(),self.geometry().topLeft().y(),width+200,height+200)
        
        #show the photo
        
        if self._FaceCenter is not None:
            self.displayImage._FaceCenter = self._FaceCenter 
            self.InitConditionsButton.setEnabled(True)
            self.displayImage.setPhotoFirstTime(img_show)
        else:
            face_center,snout,_,isFaceCenter = find_center_whiskerpad(self._Image)
            if isFaceCenter is True:
                self._FaceCenter = face_center
                self.displayImage._FaceCenter = face_center
                self.InitConditionsButton.setEnabled(True)
                self.displayImage.setPhotoFirstTime(img_show) 
                self.displayImage.draw_circle(np.array([snout[0],snout[1],int((0.5/100)*width)]))
                
            else:
                
                self.displayImage.setPhotoFirstTime(img_show)     
         
        
        
        #self.displayImage.setPhoto(img_show)


    def Init_Conditions(self):
        if self._FaceCenter is not None:
            Init_Frame =  int(self._FramestoAnalizeInitEdit.text())-1
            init_cond = initial_conditions(self._FileList, self._Folder, self._FaceCenter, self._threshold, Init_Frame)
            
            self._rightAngle = init_cond[0]
            self._leftAngle = init_cond[1]
        
            image = self._Image.copy()       
            image = image.astype(np.uint8)
                
            height, width = image.shape
            bytesPerLine = 1 * width
            #img_Qt = QtGui.QImage(self._ImageDos.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
            img_Qt = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_Indexed8)
            img_show = QtGui.QPixmap.fromImage(img_Qt)
            self.displayImage.setPhoto(img_show, init_cond)       
        
    
    def Locate_Right_Eye(self):
        
        #doing nothin at the moment, inform the display 
        self.displayImage._isManualEstimation = False
        self.displayImage._isRightEyeInit = False
        self.displayImage._isLeftEyeInit = False
        self.displayImage._isSnoutInit = False

        
        #clean screen
        if self._Image is not None:
            #remove all lines in the graph
            for item in self.displayImage._scene.items():
                if isinstance(item, QtWidgets.QGraphicsLineItem):
                    self.displayImage._scene.removeItem(item)
                if isinstance(item, QtWidgets.QGraphicsEllipseItem):
                    self.displayImage._scene.removeItem(item)
                    
        #block button that cannot be used
        self.LeftEyeButton.setEnabled(False)
        self.SnoutButton.setEnabled(False)
        #self.WhiskersButton.setEnabled(False)
                    
                           
        self._RightEyePosition = []
        self._LeftEyePosition = []
        self._SnoutPosition = []
        self._rad = []
        self.displayImage._isRightEyeInit = True        
        self.displayImage.signalEmit.connect(self.Locate_Right_Eye_update)
 
    
    @QtCore.pyqtSlot(object,int,str)     
    def Locate_Right_Eye_update(self, position,number, action):
        
        self._RightEyePosition=position
        self.displayImage.signalEmit.disconnect(self.Locate_Right_Eye_update)
        self.displayImage._isRightEyeInit = False
        self.LeftEyeButton.setEnabled(True)
        
        
    def Locate_Left_Eye(self):
        
        #doing nothin at the moment, inform the display 
        self.displayImage._isManualEstimation = False
        self.displayImage._isRightEyeInit = False
        self.displayImage._isLeftEyeInit = False
        self.displayImage._isSnoutInit = False

        #clean screen
        if self._Image is not None:
            #remove all lines in the graph
            for item in self.displayImage._scene.items():
                if isinstance(item, QtWidgets.QGraphicsLineItem):
                    self.displayImage._scene.removeItem(item)
                if isinstance(item, QtWidgets.QGraphicsEllipseItem):
                    if item.pen().color() == QtCore.Qt.cyan:
                        pass
                    else:
                        self.displayImage._scene.removeItem(item)
                        
        #block button that cannot be used
        self.SnoutButton.setEnabled(False)
        #self.WhiskersButton.setEnabled(False)
                           
        self._LeftEyesPosition = []
        self._SnoutPosition = []
        self._rad = []
        self.displayImage._isLeftEyeInit = True        
        self.displayImage.signalEmit.connect(self.Locate_Left_Eye_update)
 
    
    @QtCore.pyqtSlot(object,int,str)     
    def Locate_Left_Eye_update(self, position,number, action):
        
        self._LeftEyePosition=position
        self.displayImage.signalEmit.disconnect(self.Locate_Left_Eye_update)
        self.displayImage._isLeftEyeInit = False
        

        
        self._EyesCenter = find_center_eyes_with_click(self._Image, self._RightEyePosition, self._LeftEyePosition)

        
        rect = QtCore.QRectF(self.displayImage._photo.pixmap().rect())
        #view_width=rect.width()
        view_height=rect.height() 
        #self.displayImage.draw_line(0,center_eyes,view_width,center_eyes)
        self.displayImage.draw_line(self._EyesCenter[0],0,self._EyesCenter[0],view_height)
        
        self.SnoutButton.setEnabled(True)
        
    def Locate_Snout(self):
        
        #doing nothin at the moment, inform the display 
        self.displayImage._isManualEstimation = False
        self.displayImage._isRightEyeInit = False
        self.displayImage._isLeftEyeInit = False
        self.displayImage._isSnoutInit = False
        
        #remove all blue dots
        for item in self.displayImage._scene.items():
            if isinstance(item, QtWidgets.QGraphicsEllipseItem):
                if item.pen().color() == QtCore.Qt.blue:
                    self.displayImage._scene.removeItem(item)  
                if item.pen().color() == QtCore.Qt.yellow:
                    self.displayImage._scene.removeItem(item) 
                if item.pen().color() == QtCore.Qt.red:
                    self.displayImage._scene.removeItem(item) 
                if item.pen().color() == QtCore.Qt.white:
                    self.displayImage._scene.removeItem(item) 
            if isinstance(item, QtWidgets.QGraphicsLineItem):
                if item.boundingRect().width() > 5:
                    self.displayImage._scene.removeItem(item) 
                    
        #block button that cannot be used
        #self.WhiskersButton.setEnabled(False)
                        
        self._SnoutPosition = []
        self._rad = []
        self.displayImage._isSnoutInit = True    
        self.displayImage._FaceCenter = self._EyesCenter
        self.displayImage.signalEmit.connect(self.Locate_Snout_update)
        
        
    @QtCore.pyqtSlot(object,int,str)    
    def Locate_Snout_update(self,position,number, action):


        
        self._SnoutPosition=position
        self.displayImage.signalEmit.disconnect(self.Locate_Snout_update)
        self.displayImage._isSnoutInit = False
        
    
        distance_eyes_snout = (2/3)*(position[1]-self._EyesCenter[1]) #my definition of center of whisker pad is 2/3 of the distance between eyes and snout
    
        #now the we know where the snout is, update the location of FaceCenter 
        self._FaceCenter = np.array([self._EyesCenter[0],self._EyesCenter[1] + int(round(distance_eyes_snout))])
        
        #draw it 
        rect = QtCore.QRectF(self.displayImage._photo.pixmap().rect())
        view_width=rect.width()
        #view_height=rect.height() 
        self.displayImage.draw_line(0,self._FaceCenter[1],view_width,self._FaceCenter[1])
        #self.displayImage.draw_line(self._EyesCenter[0],0,self._EyesCenter[0],view_height)
        
        rad = 1.5*(1-2/3)*(position[1]-self._EyesCenter[1])
        self._rad = rad #this is the radius of the circle used for location of initial conditions
        
        self.displayImage.draw_circle([self._FaceCenter[0],self._FaceCenter[1],rad], 'big')
        
        #activate whiskers button
        self.Locate_Whiskers()

    def Locate_Whiskers(self):
        
        
        
        #doing nothin at the moment, inform the display 
        self.displayImage._isManualEstimation = False
        self.displayImage._isRightEyeInit = False
        self.displayImage._isLeftEyeInit = False
        self.displayImage._isSnoutInit = False
        
        #remove all blue dots
        for item in self.displayImage._scene.items():
            if isinstance(item, QtWidgets.QGraphicsEllipseItem):
                if item.pen().color() == QtCore.Qt.blue:
                    self.displayImage._scene.removeItem(item)  
                if item.pen().color() == QtCore.Qt.red:
                    self.displayImage._scene.removeItem(item) 
            if isinstance(item, QtWidgets.QGraphicsLineItem):
                if item.pen().color() == QtCore.Qt.red:
                    self.displayImage._scene.removeItem(item) 
                if item.pen().color() == QtCore.Qt.blue:
                    self.displayImage._scene.removeItem(item) 
        
        
        self._hasAngleTempRight = [[False],[False]] #a temporary version of the variable self._hasAngle
        self._hasAngleTempLeft = [[False],[False]]  #a temporary version of the variable self._hasAngle
        self._temp_storage_right = [[None],[None]]
        self._temp_storage_left = [[None],[None]]
        
        self.displayImage._isManualEstimation = True
        self.displayImage._rad = self._rad
        self.displayImage._FaceCenter = self._FaceCenter
        self.displayImage.signalEmit.connect(self.Locate_Whiskers_update)
        self.displayImage.finished.connect(self.Locate_Whiskers_end)


    @QtCore.pyqtSlot(object,int,str)     
    def Locate_Whiskers_update(self,position,number, action):
        
        if action == 'append': #append the information in the current frame
            if position[0]<self._FaceCenter[0]:
                if number == 1:
                    self._hasAngleTempRight[0]= True
                    self._temp_storage_right[0]= [position[0],position[1]]#angle_est
                elif number == 2:
                    self._hasAngleTempRight[1] = True            
                    self._temp_storage_right[1] = [position[0],position[1]]#angle_est
                
            elif position[0]>self._FaceCenter[0]:
        #                angle_est = np.arctan(((position[0] - self._FaceCenter[0])/(self._FaceCenter[1]-position[1])))*(180/np.pi)
        #                if angle_est < 0 :
        #                    angle_est = 180+angle_est
                if number == 1:    
                    self._hasAngleTempLeft[0] = True
                    self._temp_storage_left[0] = [position[0],position[1]]#angle_est
                elif number == 2:
                    self._hasAngleTempLeft[1] = True
                    self._temp_storage_left[1]= [position[0],position[1]]#angle_est
                
        elif action == 'remove': #remove the information from the current frame
            self._hasAngleTempRight[0]= False
            self._temp_storage_right[0] = None
            self._hasAngleTempRight[1] = False            
            self._temp_storage_right[1] = None
            
            self._hasAngleTempLeft[0] = False
            self._temp_storage_left[0] = None
            self._hasAngleTempLeft[1] = False
            self._temp_storage_left[1] = None            
    
    def Locate_Whiskers_end(self):
        self.displayImage._isManualEstimation = False #end manual estimation
        
        right = None
        left = None
        
        if (self._hasAngleTempRight[0] is True) and (self._hasAngleTempRight[1] is True):
                #print(self._FaceCenter)
                x1 = self._FaceCenter[0] - self._temp_storage_right[0][0]
                y1 = self._FaceCenter[1] - self._temp_storage_right[0][1]

                x2 = self._FaceCenter[0] - self._temp_storage_right[1][0]
                y2 = self._FaceCenter[1] - self._temp_storage_right[1][1]

                rad = np.sqrt(x1**2 + y1**2)
                p = rad*(x1+x2)/(np.sqrt((x1+x2)**2 + (y1+y2)**2))                 
                q = ((y1+y2)/(x1+x2))*p
                #p = self._FaceCenter[0]-p
                #q = self._FaceCenter[1]-q
                if q == 0:
                    angle_est = 0
                else:
                    angle_est = np.arctan(((p)/(-q)))*180/np.pi + 90

#                if angle_est < 0 :
#                    angle_est = 180+angle_est
                right = angle_est

        if (self._hasAngleTempLeft[0] is True) and (self._hasAngleTempLeft[1] is True):
                x1 = self._FaceCenter[0] - self._temp_storage_left[0][0]
                y1 = self._FaceCenter[1] - self._temp_storage_left[0][1]

                x2 = self._FaceCenter[0] - self._temp_storage_left[1][0]
                y2 = self._FaceCenter[1] - self._temp_storage_left[1][1]

                rad = np.sqrt(x1**2 + y1**2)
                p = rad*(x1+x2)/(np.sqrt((x1+x2)**2 + (y1+y2)**2))                
                q = ((y1+y2)/(x1+x2))*p
                
                if q == 0 :
                    angle_est = 180 
                else:                   
                    angle_est = np.arctan(((p)/(q)))*180/np.pi -90
#                if angle_est < 0 :
#                    angle_est = 180+angle_est
                                
                left = angle_est
                
                
        if right is not None and left is not None:
            self._rightAngle = right
            self._leftAngle = left
            
            l_bar = self._FaceCenter[1]*0.75
            dy_right= l_bar*np.tan(self._rightAngle*np.pi/180)
            dy_left= l_bar*np.tan(self._leftAngle*np.pi/180)
#                self.draw_line(self._FaceCenter[0],self._FaceCenter[1], self._FaceCenter[0]-l_bar, int(self._FaceCenter[1]-dy_right),1,3)
#                self.draw_line(self._FaceCenter[0],self._FaceCenter[1], self._FaceCenter[0]+l_bar, int(self._FaceCenter[1]-dy_left),1,3)
            self.displayImage.draw_line(self._FaceCenter[0],self._FaceCenter[1], self._FaceCenter[0]-l_bar, self._FaceCenter[1]-dy_right,1,3)
            self.displayImage.draw_line(self._FaceCenter[0],self._FaceCenter[1], self._FaceCenter[0]+l_bar, self._FaceCenter[1]-dy_left,1,3)
            
            for item in self.displayImage._scene.items():
                if isinstance(item, QtWidgets.QGraphicsEllipseItem):
                    if item.pen().color() == QtCore.Qt.cyan:
                        self.displayImage._scene.removeItem(item)  
                    if item.pen().color() == QtCore.Qt.magenta:
                        self.displayImage._scene.removeItem(item) 
                    if item.pen().color() == QtCore.Qt.white:
                        self.displayImage._scene.removeItem(item) 

    
    def Done(self):
              
        self._InitFrame = int(self._FramestoAnalizeInitEdit.text())-1
        self._Initial_Conditions = np.array([self._rightAngle, self._leftAngle])
        
        if self._FaceCenter is None and self._Initial_Conditions[0] is None:
                     #ask is the user really wants to close the app
            choice = QtWidgets.QMessageBox.question(self, 'Message', 
                                'Face Center and Initial Conditions not defined. Frames cannot be proccessed.\nDo you want to exit?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
            
            if choice == QtWidgets.QMessageBox.Yes :
                self.close()
            else:
                return
            
        elif self._FaceCenter is None:
            choice = QtWidgets.QMessageBox.question(self, 'Message', 
                                'Face Center not defined, frames cannot be proccessed.\nDo you want to exit?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
            
            if choice == QtWidgets.QMessageBox.Yes :
                self.close()
            else:
                return
            
        elif self._Initial_Conditions[0] is None:
                     #ask is the user really wants to close the app
            choice = QtWidgets.QMessageBox.question(self, 'Message', 
                                'Initial Conditions not defined.\nDo you want to exit?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
            
            if choice == QtWidgets.QMessageBox.Yes :
                self.close()
            else:
                return
        else:                    
            self.close()
               
    def closeEvent(self, event):
        event.accept()

    #this function read the style sheet used to presents the GroupBox, 
    #it is located in .\include\GroupBoxStyle.qss
    def getStyleSheet(self, path):
        f = QFile(path)
        f.open(QFile.ReadOnly | QFile.Text)
        stylesheet = QTextStream(f).readAll()
        f.close()
        return stylesheet
        
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
#    if not QtWidgets.QApplication.instance():
#        app = QtWidgets.QApplication(sys.argv)
#    else:
#        app = QtWidgets.QApplication.instance()
       
    GUI = InitConditionsWindow()
    GUI.show()
    app.exec_()

