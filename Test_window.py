# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 11:30:39 2018

@author: guarind
"""

import os
import sys
import cv2
import numpy as np


from ImageViewer import ImageViewer

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QPushButton, QDialog, QSpinBox, QCheckBox,QLineEdit, QToolButton,QPlainTextEdit
#from PyQt5.QtCore import pyqtSlot
#from PyQt5.QtCore import QFile, QTextStream
"""

"""

        
class TestWindow(QDialog):
        
    
    def __init__(self, FileList = None, Folder = None, RightROI = None, LeftROI = None, FaceCenter =  None ):
        super(TestWindow, self).__init__()
        
#        self._scene = QtWidgets.QGraphicsScene(self)
#        self.setScene(self._scene)
        
#        FileList = ['Basler acA800-510uc (22501173)_20171212_190308266_0001.tiff', 'Basler acA800-510uc (22501173)_20171212_190308266_0002.tiff', 'Basler acA800-510uc (22501173)_20171212_190308266_0003.tiff', 'Basler acA800-510uc (22501173)_20171212_190308266_0004.tiff', 'Basler acA800-510uc (22501173)_20171212_190308266_0005.tiff', 'Basler acA800-510uc (22501173)_20171212_190308266_0006.tiff', 'Basler acA800-510uc (22501173)_20171212_190308266_0007.tiff', 'Basler acA800-510uc (22501173)_20171212_190308266_0008.tiff', 'Basler acA800-510uc (22501173)_20171212_190308266_0009.tiff', 'Basler acA800-510uc (22501173)_20171212_190308266_0010.tiff']
#        Folder = r'C:/Users/GUARIND/Videos/Basler/test3'
#        RightROI = np.array([[368,387],[324,329],[299,261],[230,157],[196,78],[ 21,77],[16,581],[373,585]])
#        LeftROI = np.array([[440,387],[484,329],[509,261],[578,157],[612,78],[787,77],[792,581],[435,585]])
#        FaceCenter = np.array([404,302])

        self._Folder = Folder
        self._FileList = FileList
        self._InitFrame = 1 
        self._EndFrame = self._InitFrame+1#len(self._List)
        
        self._NumAngles = 50
        
        self._minAngle = -3.5
        self._maxAngle = 3.5
        
        
        self._FaceCenter = FaceCenter
        self._RightROI = RightROI
        self._LeftROI = LeftROI
        
        self._ImageUno = None
        self._ImageDos = None
        
        self._angles = None #all avaliable angles
        self._angle = 0 #current angle to analize
        self._angle_index = 0 #index of current angle
        self._threshold = 255 #threshold value
        self._rotation = 0 #rotation value
        
        self._AnalizeSide = None
        
        
        self.initUI()
        

        
    def initUI(self):
        
        self.setWindowTitle('Test Parameters')
        scriptDir = os.getcwd()
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'face_icon.ico'))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() |
                              QtCore.Qt.WindowSystemMenuHint |
                              QtCore.Qt.WindowMinMaxButtonsHint)
        
        
        
#        
#        self._scene = QtWidgets.QGraphicsScene()
#        self._scene.setSceneRect(0, 0, 600,800)
#        self._photo = QtWidgets.QGraphicsPixmapItem()
#        self._scene.addItem(self._photo)
#        
#        self.view = QtWidgets.QGraphicsView(self)
#        self.view.setScene(self._scene)
#        #self.view.setRenderHint(QtGui.QPainter.Antialiasing)
#        #self.view.setFrameShape(QtWidgets.QFrame.NoFrame)
#        
#        #self.view.setFocusPolicy(QtCore.Qt.NoFocus)
#        color = self.palette().color(QtGui.QPalette.Background)
#        self.view.setBackgroundBrush(color)
#        
#        
#        self.view.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
#        self.view.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
#        self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
#        self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.spacerh = QtWidgets.QWidget(self)
        self.spacerh.setFixedSize(20,0)
        
        self.spacerv = QtWidgets.QWidget(self)
        self.spacerv.setFixedSize(0,5)

        
        #Top part
        newfont = QtGui.QFont("Times", 12)
        
        self.label1 = QLabel('Frames to Analyze:')
        self.label1.setFont(newfont)
        self.label1.setFixedWidth(250)
        
        self._FramestoAnalizeInitEdit = QLineEdit(self)
        self._FramestoAnalizeInitEdit.setText(str(self._InitFrame)) 
        self._FramestoAnalizeInitEdit.setFont(newfont)
        self._FramestoAnalizeInitEdit.setFixedWidth(75)   
        validator = QtGui.QIntValidator(1, len(self._FileList))
        self._FramestoAnalizeInitEdit.setValidator(validator)
    
        self._FramestoAnalizeEndEdit = QLineEdit(self)
        self._FramestoAnalizeEndEdit.setText(str(self._EndFrame)) 
        self._FramestoAnalizeEndEdit.setFont(newfont)
        self._FramestoAnalizeEndEdit.setFixedWidth(75)
        validator = QtGui.QIntValidator(1, len(self._FileList))
        self._FramestoAnalizeEndEdit.setValidator(validator)
        
        
        
        self.label2 = QLabel('Side To Analyze')
        self.label2.setFont(newfont)
        self.label2.setFixedWidth(250)
        
        self._check_right = QCheckBox('Right')
        self._check_right.setFont(newfont)
        self._check_right.setChecked(True)
        self._check_right.setFixedWidth(70)
        
        self._check_left = QCheckBox('Left')
        self._check_left.setFont(newfont)
        self._check_left.setChecked(False)
        self._check_left.setFixedWidth(70)
        
        self._CheckButtonGroup = QtWidgets.QButtonGroup(self)
        self._CheckButtonGroup.addButton(self._check_right,1)
        self._CheckButtonGroup.addButton(self._check_left,2)
               
        self.label3 = QLabel('Angular Range')
        self.label3.setFont(newfont)
        self.label3.setFixedWidth(250)
        
        self._AnglesInitEdit = QLineEdit(self)
        self._AnglesInitEdit.setText(str(self._minAngle)) 
        self._AnglesInitEdit.setFont(newfont)
        self._AnglesInitEdit.setFixedWidth(70) 
        validator = QtGui.QDoubleValidator(-100, 100,3)
        self._AnglesInitEdit.setValidator(validator)
        
        self._AnglesEndEdit = QLineEdit(self)
        self._AnglesEndEdit.setText(str(self._maxAngle)) 
        self._AnglesEndEdit.setFont(newfont)
        self._AnglesEndEdit.setFixedWidth(70)
        validator = QtGui.QDoubleValidator(-100, 100,3)
        self._AnglesEndEdit.setValidator(validator)
        
        
        self.label4 = QLabel('Number of Angles to Analyze')
        self.label4.setFont(newfont)
        self.label4.setFixedWidth(250)
               
        self._spinAngles = QSpinBox()
        self._spinAngles.setMinimum(1) 
        self._spinAngles.setMaximum(1000)
        self._spinAngles.setFont(newfont)
        self._spinAngles.setValue(self._NumAngles)
        self._spinAngles.setFixedWidth(150)
        
        
        TopLayout = QtWidgets.QGridLayout()
        TopLayout.addWidget(self.label1, 0 , 0)
        TopLayout.addWidget(self._FramestoAnalizeInitEdit, 0 , 2)
        TopLayout.addWidget(self._FramestoAnalizeEndEdit, 0 , 3)
        
        TopLayout.addWidget(self.label2, 1 , 0)
        TopLayout.addWidget(self._check_right, 1 , 2)
        TopLayout.addWidget(self._check_left, 1 , 3)
        
        TopLayout.addWidget(self.label3, 2 , 0)
        TopLayout.addWidget(self._AnglesInitEdit, 2 , 2)
        TopLayout.addWidget(self._AnglesEndEdit, 2 , 3)
        
        TopLayout.addWidget(self.label4, 3 , 0)
        TopLayout.addWidget( self._spinAngles, 3 , 2,1,2)
        
        
        
        #buttons       
        
        DoneButton = QPushButton('&Start', self)
        DoneButton.setFixedWidth(75)
        DoneButton.setFont(newfont)
        DoneButton.clicked.connect(self.Start)
        
        CancelButton = QPushButton('&Close', self)
        CancelButton.setFixedWidth(75)
        CancelButton.setFont(newfont)
        CancelButton.clicked.connect(self.Cancel)
        
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(DoneButton)
        buttonLayout.addWidget(CancelButton)
        
        
        #button part
        self.label5 = QLabel('Angle')
        self.label5.setFont(newfont)
        #self.label5.setFixedWidth(250)
        self.label5.setAlignment(QtCore.Qt.AlignCenter)
        
        #angle change
        self._left_Angle_button = QToolButton()
        self._left_Angle_button.setArrowType(QtCore.Qt.LeftArrow)
        self._left_Angle_button.setFont(newfont)
        self._left_Angle_button.setFixedWidth(75)
        self._left_Angle_button.setEnabled(False)
        self._left_Angle_button.clicked.connect(self.AngleChange_Left)
        
        self._right_Angle_button = QToolButton()
        self._right_Angle_button.setArrowType(QtCore.Qt.RightArrow)
        self._right_Angle_button.setFont(newfont)
        self._right_Angle_button.setFixedWidth(75)
        self._right_Angle_button.setEnabled(False)
        self._right_Angle_button.clicked.connect(self.AngleChange_Right)
        
        self._Angle = QLineEdit(self)
        self._Angle.setText(str(self._angle)) 
        self._Angle.setFont(newfont)
        self._Angle.setFixedWidth(150) 
        validator = QtGui.QDoubleValidator(self._minAngle, self._maxAngle,3)
        self._Angle.setValidator(validator)
        self._Angle.setAlignment(QtCore.Qt.AlignCenter)
        self._Angle.setEnabled(False)
        self._Angle.textChanged.connect(self.AngleChange)
        
        AngleLayout = QtWidgets.QHBoxLayout()
        AngleLayout.addWidget(self._left_Angle_button)
        AngleLayout.addWidget(self._Angle)
        AngleLayout.addWidget(self._right_Angle_button)
        
        
        #Threshold change
        self.label6 = QLabel('Threshold')
        self.label6.setFont(newfont)
        #self.label5.setFixedWidth(250)
        self.label6.setAlignment(QtCore.Qt.AlignCenter)
        
        self._left_Threshold_button = QToolButton()
        self._left_Threshold_button.setArrowType(QtCore.Qt.LeftArrow)
        self._left_Threshold_button.setFont(newfont)
        self._left_Threshold_button.setFixedWidth(75)
        self._left_Threshold_button.setEnabled(False)
        self._left_Threshold_button.clicked.connect(self.ThresholdChange_Left)
        
        self._right_Threshold_button = QToolButton()
        self._right_Threshold_button.setArrowType(QtCore.Qt.RightArrow)
        self._right_Threshold_button.setFont(newfont)
        self._right_Threshold_button.setFixedWidth(75)
        self._right_Threshold_button.setEnabled(False)
        self._right_Threshold_button.clicked.connect(self.ThresholdChange_Right)
        
        self._Threshold = QLineEdit(self)
        self._Threshold.setText(str(self._threshold)) 
        self._Threshold.setFont(newfont)
        self._Threshold.setFixedWidth(150) 
        validator = QtGui.QIntValidator(0, 255)
        self._Threshold.setValidator(validator)
        self._Threshold.setAlignment(QtCore.Qt.AlignCenter)
        self._Threshold.setEnabled(False)
        self._Threshold.textChanged.connect(self.ThresholdChange)
        
        ThresholdLayout = QtWidgets.QHBoxLayout()
        ThresholdLayout.addWidget(self._left_Threshold_button)
        ThresholdLayout.addWidget(self._Threshold)
        ThresholdLayout.addWidget(self._right_Threshold_button)
        
        
        #Threshold change
        self.label7 = QLabel('Rotation')
        self.label7.setFont(newfont)
        #self.label5.setFixedWidth(250)
        self.label7.setAlignment(QtCore.Qt.AlignCenter)
        
        self._left_Rotation_button = QToolButton()
        self._left_Rotation_button.setArrowType(QtCore.Qt.LeftArrow)
        self._left_Rotation_button.setFont(newfont)
        self._left_Rotation_button.setFixedWidth(75)
        self._left_Rotation_button.setEnabled(False)
        self._left_Rotation_button.clicked.connect(self.RotationChange_Left)
        
        self._right_Rotation_button = QToolButton()
        self._right_Rotation_button.setArrowType(QtCore.Qt.RightArrow)
        self._right_Rotation_button.setFont(newfont)
        self._right_Rotation_button.setFixedWidth(75)
        self._right_Rotation_button.setEnabled(False)
        self._right_Rotation_button.clicked.connect(self.RotationChange_Right)
        
        self._Rotation = QLineEdit(self)
        self._Rotation.setText(str(self._rotation)) 
        self._Rotation.setFont(newfont)
        self._Rotation.setFixedWidth(150) 
        validator = QtGui.QDoubleValidator(-15, 15,3)
        self._Rotation.setValidator(validator)
        self._Rotation.setAlignment(QtCore.Qt.AlignCenter)
        self._Rotation.setEnabled(False)
        self._Rotation.textChanged.connect(self.RotationChange)
        
        RotationLayout = QtWidgets.QHBoxLayout()
        RotationLayout.addWidget(self._left_Rotation_button)
        RotationLayout.addWidget(self._Rotation)
        RotationLayout.addWidget(self._right_Rotation_button)
        
        
        #Estimated Correlation 
        self.label8 = QLabel('Estimated Correlation')
        self.label8.setFont(newfont)
        #self.label5.setFixedWidth(250)
        self.label8.setAlignment(QtCore.Qt.AlignCenter)
        
        self._Correlation= QPlainTextEdit(self)
        self._Correlation.clear()
        self._Correlation.setPlainText(str(0)) 
        self._Correlation.setFont(newfont)
        self._Correlation.setFixedWidth(250) 
        self._Correlation.setFixedHeight(30) 
        #validator = QtGui.QDoubleValidator(-1, 1,5)
        #self._Correlation.setValidator(validator)
        #self._Correlation.setAlignment(QtCore.Qt.AlignCenter)
        self._Correlation.setEnabled(False)
        self._Correlation.setReadOnly(True)
        
        CorrelationLayout = QtWidgets.QHBoxLayout()
        #CorrelationLayout.addWidget(self._left_Threshold_button)
        CorrelationLayout.addWidget(self._Correlation)
        #CorrelationLayout.addWidget(self._right_Threshold_button)
        
        
        ViewLayout = QtWidgets.QHBoxLayout()
        
        self.displayImage = ImageViewer()
        color = self.palette().color(QtGui.QPalette.Background)
        self.displayImage.setBackgroundBrush(color)
        
        ViewLayout.addWidget(self.displayImage)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(TopLayout)
        layout.addLayout(buttonLayout)
        #layout.addWidget(self.view)
        layout.addLayout(ViewLayout)
        layout.addWidget(self.label5)
        layout.addLayout(AngleLayout)
        layout.addWidget(self.label6)
        layout.addLayout(ThresholdLayout)
        layout.addWidget(self.label7)
        layout.addLayout(RotationLayout)
        layout.addWidget(self.label8)
        layout.addLayout(CorrelationLayout)
        
        self.setLayout(layout)

        

        #fix the size, the user cannot change it 
        #self.resize(self.sizeHint())
        #self.setFixedSize(self.size())
        
        self.setGeometry(300,300,400,800)
        self.show()   
        
        
    def Start(self):        
        #compute angles
        value_init = float(self._AnglesInitEdit.text())
        value_end = float( self._AnglesEndEdit.text())
        if value_end <= value_init :
            QtWidgets.QMessageBox.warning(self, 'Error','Final Angle must be greather than Initial Angle')
            return       
        
#        if value_init > 0 :
#            QtWidgets.QMessageBox.warning(self, 'Error','Initial Angle must be less or equal than zero')
#            return  
#        
#        if value_end < 0 :
#            QtWidgets.QMessageBox.warning(self, 'Error','Final Angle must be greather or equal than zero')
#            return  
        
        self._minAngle = value_init
        self._maxAngle = value_end
        
        self._NumAngles = self._spinAngles.value()
        
        
        angles = np.linspace(self._minAngle, self._maxAngle, self._NumAngles)
        print(self._minAngle*self._maxAngle)
        #verify that there are positive and negative angles 
        if  self._minAngle*self._maxAngle < 0:
        
            zero_ind = np.where(angles == 0)[0]
            if zero_ind.size == 1:
                pass
            elif zero_ind.size > 0:
                QtWidgets.QMessageBox.warning(self, 'Error','This is weird. There are more than one zero in the angles to evaluate....')
                return
            elif zero_ind.size == 0: #add zero to the list of angles 
                sgn_change_ind = np.where(np.diff(np.sign(angles)))[0]
                angles_neg = angles[:sgn_change_ind[0]+1]
                angles_pos = angles[sgn_change_ind[0]:]
                angles = np.r_[angles_neg, [np.float(0)],angles_pos[1:]]
            else: 
                QtWidgets.QMessageBox.warning(self, 'Error','This is weird. Unknown error with the angles.')
                return 

            self._angles = np.asarray(angles)
            
            
            self._angle_index = int(np.where(self._angles  == 0)[0])
            self._angle = self._angles[self._angle_index]
            self._Angle.setText(str(np.round(self._angle,5)))
            
        else:
            self._angles = np.asarray(angles)
            self._angle = 0
            self._Angle.setText(str(np.round(self._angle,5)))
        
        
        #Frames to analize
        Init_Frame =  int(self._FramestoAnalizeInitEdit.text())
        if Init_Frame == 0:
            QtWidgets.QMessageBox.warning(self, 'Error','Frame number must be larger than 0')
            return  
        End_Frame =  int(self._FramestoAnalizeEndEdit.text())
        if End_Frame == 0:
            QtWidgets.QMessageBox.warning(self, 'Error','Frame number must be larger than 0')
            return  
        
        if Init_Frame > End_Frame:
            QtWidgets.QMessageBox.warning(self, 'Error','Initial Frame cannot be larger than Final Frame')
            return
        
        if self._check_right.isChecked() :
            self._AnalizeSide = 'Right'
        elif self._check_left.isChecked() :
            self._AnalizeSide = 'Left'
        
        #read images from memory in gray format
        temp_image  = cv2.imread(os.path.join(self._Folder,self._FileList[Init_Frame]))
        temp_image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
        self._ImageUno = cv2.cvtColor(temp_image , cv2.COLOR_BGR2GRAY)
        
        temp_image  = cv2.imread(os.path.join(self._Folder,self._FileList[End_Frame]))
        temp_image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
        self._ImageDos = cv2.cvtColor(temp_image , cv2.COLOR_BGR2GRAY)

        h_orig, w_orig = self._ImageUno.shape #original shape 

        blended = self.create_blend_image()
        
        if self._AnalizeSide == 'Right':
            ROI = self._RightROI
            image = blended.copy()
            image = image[:,0:self._FaceCenter[0]] #take right side
        else:
            ROI = self._LeftROI
            ROI = ROI -[self._FaceCenter[0],0]
            #ROI = [2*self._FaceCenter[0],0]-ROI  #mirror the left ROI to the right 
            #ROI[:,1]=abs(ROI[:,1])  #correct the minus sign in the y column
            image = blended.copy()
            #image = cv2.flip(image,1) #mirror it
            image = image[:,self._FaceCenter[0]:-1]  #take left side
        
        
        image = image.astype(np.uint8)
            
#        cv2.namedWindow("Video", cv2.WINDOW_NORMAL+cv2.WINDOW_KEEPRATIO)
#        cv2.imshow("Video", image)
#        cv2.waitKey(0)
#        cv2.destroyAllWindows()
        
        height, width = image.shape
        bytesPerLine = 1 * width
        #img_Qt = QtGui.QImage(self._ImageDos.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
        img_Qt = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_Indexed8)
        img_show = QtGui.QPixmap.fromImage(img_Qt) 
        self.displayImage.setPhoto(img_show)
        self.displayImage.draw_polygon(ROI)

        
        self._left_Angle_button.setEnabled(True)
        self._right_Angle_button.setEnabled(True)
        self._Angle.setEnabled(True)
        self._left_Threshold_button.setEnabled(True)
        self._right_Threshold_button.setEnabled(True)
        self._Threshold.setEnabled(True)
        self._left_Rotation_button.setEnabled(True)
        self._right_Rotation_button.setEnabled(True)
        self._Rotation.setEnabled(True)
        
        self._Correlation.setEnabled(True)
    
    
        self.ProcessFrames()

    def create_blend_image(self):
        
        h,w = self._ImageUno.shape
        
        #rotate both images 
        M = cv2.getRotationMatrix2D((int(w/2),int(h/2)), self._rotation, 1.0)
        
        imageuno = cv2.warpAffine(self._ImageUno, M, (w, h))
        imagedos = cv2.warpAffine(self._ImageDos, M, (w, h))
        
        imageuno[imageuno>self._threshold] = 255
        imagedos[imagedos>self._threshold] = 255
        
        
        blend = cv2.addWeighted(imageuno,0.5,imagedos,0.5,0)
        
        return blend

 #----------------------------------------------- 
            
    def AngleChange(self):
        if float(self._Angle.text()) > self._maxAngle:            
            self._angle = self._maxAngle
            self._Angle.setText(str(np.round(self._angle,5)))
        elif float(self._Angle.text()) < self._minAngle:            
            self._angle = self._minAngle
            self._Angle.setText(str(np.round(self._angle,5)))
            
        self.ProcessFrames()
        
        
    def AngleChange_Right(self):
        if self._angle_index < len(self._angles)-1:
            self._angle_index +=1
            self._angle = self._angles[self._angle_index]
            self._Angle.setText(str(np.round(self._angle,5)))
            
    def AngleChange_Left(self):
        if self._angle_index > 0:
            self._angle_index -=1
            self._angle = self._angles[self._angle_index]
            self._Angle.setText(str(np.round(self._angle,5)))
 
 #-----------------------------------------------   
        
    def ThresholdChange(self):
        if int(self._Threshold.text()) > 255:            
            self._threshold = 255
            self._Threshold.setText(str(np.round(self._threshold)))
        elif int(self._Threshold.text()) < 0:            
            self._threshold = 0
            self._Threshold.setText(str(np.round(self._threshold)))
            
        self.ProcessFrames()
                
    def ThresholdChange_Right(self):
        if self._threshold < 255:
            self._threshold  +=1
            self._Threshold.setText(str(np.round(self._threshold)))
            
    def ThresholdChange_Left(self):
        if self._threshold > 0 :
            self._threshold  -=1
            self._Threshold.setText(str(np.round(self._threshold)))
            
 #-----------------------------------------------   
        
    def RotationChange(self):
        if float(self._Rotation.text()) > 15:            
            self._rotation = 15
            self._Rotation.setText(str(np.round(self._rotation,5)))
        elif float(self._Rotation.text()) < -15:            
            self._rotation = -15
            self._Rotation.setText(str(np.round(self._rotation,5)))
            
        self.ProcessFrames()
                
    def RotationChange_Right(self):
        if self._rotation < 15:
            self._rotation  = self._rotation + 0.25
            self._Rotation.setText(str(np.round(self._rotation,5)))
            
    def RotationChange_Left(self):
        if self._rotation > -15 :
            self._rotation = self._rotation - 0.25
            self._Rotation.setText(str(np.round(self._rotation,5)))
        
    
#---------------------------------------------------------
            
    def ProcessFrames(self):

        self._rotation = float(self._Rotation.text())
        self._angle = float(self._Angle.text())
        self._threshold = int(self._Threshold.text())
        

        #apply threshold and rotation and blend both images 
        imageuno= self._ImageUno.copy()
        imagedos = self._ImageDos.copy()

        h,w = imageuno.shape

        #rotation that will be applied to both image
        M = cv2.getRotationMatrix2D((int(w/2),int(h/2)), self._rotation, 1.0)

        imageuno = cv2.warpAffine(imageuno, M, (w, h))
        imagedos = cv2.warpAffine(imagedos, M, (w, h))

        imageuno[imageuno>self._threshold] = 255
        imagedos[imagedos>self._threshold] = 255

        if self._AnalizeSide == 'Right':

            ROI = self._RightROI
            imageuno = imageuno[:,0:self._FaceCenter[0]] #take right side
            imagedos = imagedos[:,0:self._FaceCenter[0]] #take right side

            #rotation that will be applied to second image
            M_angle = cv2.getRotationMatrix2D(tuple(self._FaceCenter),self._angle,1)

            
        else:
            ROI = self._LeftROI
            ROI = ROI -[self._FaceCenter[0],0]
            imageuno = imageuno[:,self._FaceCenter[0]:-1]  #take left side
            imagedos = imagedos[:,self._FaceCenter[0]:-1]  #take left side
            
            M_angle = cv2.getRotationMatrix2D((0,self.FaceCenter[1]), self._angle,1)
            
        
        #invert image
        imageuno = cv2.bitwise_not(imageuno)
        imagedos = cv2.bitwise_not(imagedos)

        #create the mask that will cover only the whiskers in left and right sides of the face
        mask = np.zeros(imageuno.shape, np.uint8)    
        cv2.fillConvexPoly(mask, ROI, (255,255,255))

        tempuno= np.zeros(imageuno.shape, np.uint8)
        cv2.bitwise_and(imageuno,mask,tempuno)
        
        height, width = imageuno.shape
        imagedos = cv2.warpAffine(imagedos, M_angle, (width, height))
        
        tempdos= np.zeros(imagedos.shape, np.uint8)
        cv2.bitwise_and(imagedos,mask,tempdos)

        blended = cv2.addWeighted(imageuno,0.5,imagedos,0.5,0)
        
        blended = blended.astype(np.uint8)
            
#        cv2.namedWindow("Video", cv2.WINDOW_NORMAL+cv2.WINDOW_KEEPRATIO)
#        cv2.imshow("Video", blended)
#        cv2.waitKey(0)
#        cv2.destroyAllWindows()
        
        #height, width = blended.shape
        blended= cv2.bitwise_not(blended)
        bytesPerLine = 1 * width
        #img_Qt = QtGui.QImage(self._ImageDos.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
        img_Qt = QtGui.QImage(blended.data, width, height, bytesPerLine, QtGui.QImage.Format_Indexed8)
        img_show = QtGui.QPixmap.fromImage(img_Qt) 
        self.displayImage.setPhoto(img_show)
        
        
        #find the correlation between the previous frame and the rotate version of the current frame                                                     
        correl = cv2.matchTemplate(cv2.resize(tempuno,(0,0),fx=0.5,fy=0.5), cv2.resize(tempdos,(0,0),fx=0.5,fy=0.5), cv2.TM_CCORR_NORMED)[0]
        #show results
        
        self._Correlation.setPlainText(str(np.round(correl[0],5)))
        
        
        
        
    def Cancel(self):
               
        self.close()  

       
    def closeEvent(self, event):
        event.accept()

        
if __name__ == '__main__':
#    app = QtWidgets.QApplication([])
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
       
    GUI = TestWindow()
    GUI.show()
    app.exec_()
    

