# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 18:41:24 2017

@author: Diego L.Guarin -- diego_guarin at meei.harvard.edu
"""
import os 
import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt

from PyQt5 import QtWidgets, QtGui, QtCore

#add an option to load and save parameters


from ImageViewer import ImageViewer

from threshold_window import ThresholdWindow
from goto_window import GoToWindow
from fps_window import FPSWindow
from process_window import ProcessWindow
from video_window import VideoWindow

from rotation_window import RotationAngleWindow

from save_utils import SaveTXT
from save_utils import ReadTXT


def get_pixmap(image, threshold=None, rotation_angle = None):
    #conver an opencv image to a QtImage (Pixmap) this function takes into consideration
    #if the image is color or gray and if there is a threshold defined or not
    if rotation_angle is None: #no rotation
        pass
    else: #user wants to rotate the image, lets do it...
        M = cv2.getRotationMatrix2D((int(image.shape[1]/2),int(image.shape[0]/2)), rotation_angle, 1.0)
        image = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
    
    if threshold is None:                        
        #separate color and gray images
        if len(image.shape) == 3: #color image
            height, width, channel = image.shape
            bytesPerLine = 3 * width
            img_Qt = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
        elif len(image.shape) == 2: #gary image
            height, width = image.shape
            bytesPerLine = 1 * width
            img_Qt = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_Indexed8)
        
        img_show = QtGui.QPixmap.fromImage(img_Qt)
    else:
        #function differs if image is color or gray         
        if len(image.shape) == 3: #color image     
            #convert to gray
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            #apply threshold
            image[image>threshold] = 255
            height, width = image.shape
            bytesPerLine = 1 * width
            img_Qt = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_Indexed8)
            img_show = QtGui.QPixmap.fromImage(img_Qt)
        elif len(image.shape) == 2: #gray image
            image[image>threshold] = 255
            height, width = image.shape
            bytesPerLine = 1 * width
            img_Qt = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_Indexed8)
        
        img_show = QtGui.QPixmap.fromImage(img_Qt) 
            
    return img_show            
            
    

class QHLine(QtWidgets.QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)

class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        #self.setGeometry(5,60,700,500)
        self.setWindowTitle('Whisker Analysis')
        scriptDir = os.getcwd()
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'face_icon.ico'))
        self.background_color = self.palette().color(QtGui.QPalette.Background)
        
        #initialize the User Interface
        self.initUI()
        
        self._threshold = None #threshold for image processing 
        
        self._current_Image = None #this variable stores the image that is being displayed in the screen 
        
        self._FaceCenter = None #stores position of face center
        self._RightROI = None #stores position of right ROI
        self._LeftROI = None #stores position of left ROI
        
        self._FrameIndex = 0  #Frame Index
        self._FileList = None #list of files to be processed
        self._Folder = None #folder where photos are located 
        
        self._fps = 24  #this variable controls the playback speed
        
        self._rotation_angle = None #rotation angle 
        
        self.timer = QtCore.QTimer()  #controls video playback 
        
        
    def initUI(self):
        #local directory
        scriptDir = os.getcwd()#os.path.dirname(os.path.realpath(sys.argv[0]))

        #image
        #read the image from file        
        img_Qt = QtGui.QImage(scriptDir + os.path.sep + 'include' +os.path.sep + 'mid-face.png')
        img_show = QtGui.QPixmap.fromImage(img_Qt)
        
        #the image will be displayed in the custom ImageViewer
        self.displayImage = ImageViewer()      
        self.displayImage.setPhoto(img_show)    
        
        self.main_Widget = QtWidgets.QWidget(self)
        
       
        
        MenuBar = QtWidgets.QMenuBar(self)
        MenuBar.setStyleSheet("font-size:18px;")
        self.setStyleSheet("""
                           QMenuBar {
                           font-size:18px;
                           background : transparent;
                           }
                           """)       
        FileMenu = MenuBar.addMenu("&File")
        LoadAction = FileMenu.addAction("Select Folder")
        LoadAction.setShortcut("Ctrl+F")
        LoadAction.setStatusTip('Select folder containing video frames (as .tiff files)')
        LoadAction.triggered.connect(self.load_file)
        
        LoadVideoAction = FileMenu.addAction("Select Video")
        LoadVideoAction.setShortcut("Ctrl+V")
        LoadVideoAction.setStatusTip('Select video file to store each frame as a tiff file')
        LoadVideoAction.triggered.connect(self.load_video)
        
        LoadSettingsAction = FileMenu.addAction("Load Settings")
        LoadSettingsAction.setShortcut("Ctrl+W")
        LoadSettingsAction.setStatusTip('Load FaceCenter, left and right ROI, and threshold')
        LoadSettingsAction.triggered.connect(self.loadsettings_function)
        
        SaveSettingsAction = FileMenu.addAction("Save Settings")
        SaveSettingsAction.setShortcut("Ctrl+S")
        SaveSettingsAction.setStatusTip('Save FaceCenter, left and right ROI, and threshold')
        SaveSettingsAction.triggered.connect(self.save_function)
        
        LoadAnglesAction = FileMenu.addAction("Load Results")
        LoadAnglesAction.setShortcut("Ctrl+A")
        LoadAnglesAction.setStatusTip('Load csv file containing angular displacements')
        LoadAnglesAction.triggered.connect(self.loadangular_function)
        
        ExitAction = FileMenu.addAction("Quit")
        ExitAction.setShortcut("Ctrl+Q")
        ExitAction.triggered.connect(self.close_app)
        ExitAction.setStatusTip('Quit')
        
        
        ImageMenu = MenuBar.addMenu("&Image")
        
        
        
                
        FaceCenterAction = ImageMenu.addAction("Find Face Center")
        FaceCenterAction.setShortcut("Ctrl+C")
        FaceCenterAction.triggered.connect(self.face_center)
        FaceCenterAction.setStatusTip('Find facial midline and center of whisker pad')
        
        
        ROIMenu = QtWidgets.QMenu("ROI", self)
        ROIMenu.setStyleSheet("font-size:18px;")
        
        RigthROIAction = ROIMenu.addAction("Find Right ROI")
        RigthROIAction.setShortcut("Ctrl+R")
        RigthROIAction.setStatusTip('Find rigth side Region of Interest (ROI)')
        RigthROIAction.triggered.connect(self.RigthROI_function)
        
        LeftROIAction = ROIMenu.addAction("Find Left ROI")        
        LeftROIAction.setShortcut("Ctrl+L")
        LeftROIAction.setStatusTip('Find left side Region of Interest (ROI)')
        LeftROIAction.triggered.connect(self.LeftROI_function)
        
        MirrorAction = ROIMenu.addAction("Mirror ROI")
        MirrorAction.setShortcut("Ctrl+M")
        MirrorAction.setStatusTip('Mirror right or left ROI to the other side of the face')
        MirrorAction.triggered.connect(self.Mirror_function)
        
        ImageMenu.addMenu(ROIMenu)
        
        ThresholdMenu = QtWidgets.QMenu("Threshold", self)
        ThresholdMenu.setStyleSheet("font-size:18px;")
        
        ThresholdAction = ThresholdMenu.addAction("Find Threshold")
        ThresholdAction.setShortcut("Ctrl+T")
        ThresholdAction.setStatusTip('Find threshold. Image will be converted to gray scale')
        ThresholdAction.triggered.connect(self.threhold_function)
        
        ResetThresholdAction = ThresholdMenu.addAction("Reset Threshold")
        ResetThresholdAction.setShortcut("Ctrl+Y")
        ResetThresholdAction.setStatusTip('Reset threshold')
        ResetThresholdAction.triggered.connect(self.reset_threshold_function)
        
        ImageMenu.addMenu(ThresholdMenu)
        
        
        RotationdMenu = QtWidgets.QMenu("Rotation", self)
        RotationdMenu.setStyleSheet("font-size:18px;")
        
        RotationAction = RotationdMenu.addAction("Rotate Image")
        RotationAction.setShortcut("Ctrl+N")
        RotationAction.setStatusTip('Rotate image using its center as pivot')
        RotationAction.triggered.connect(self.rotate_function)
        
        ResetRotationAction = RotationdMenu.addAction("Reset Rotation")
        ResetRotationAction.setShortcut("Ctrl+M")
        ResetRotationAction.setStatusTip('Reset rotation')
        ResetRotationAction.triggered.connect(self.reset_rotate_function)
        
        ImageMenu.addMenu(RotationdMenu)
        
        ScreenshotAction = ImageMenu.addAction("Take Screenshot")
        ScreenshotAction.setShortcut("Ctrl+W")
        ScreenshotAction.setStatusTip('Save current view')
        ScreenshotAction.triggered.connect(self.Screenshot_function)
        
        VideoMenu = MenuBar.addMenu("&Video")
        ForwardAction = VideoMenu.addAction("Move Forward")
        ForwardAction.setShortcut("Shift+D")
        ForwardAction.setStatusTip('Move forward one frame')
        ForwardAction.triggered.connect(self.Forward_function)
               
        BackwardAction = VideoMenu.addAction("Move Backward")
        BackwardAction.setShortcut("Shift+A")
        BackwardAction.setStatusTip('Move backward one frame')
        BackwardAction.triggered.connect(self.Backward_function)
        
        PlayAction = VideoMenu.addAction("Play Movie")
        PlayAction.setShortcut("Shift+Z")
        PlayAction.setStatusTip('Play movie')
        PlayAction.triggered.connect(self.Play_function)
        
        StopAction = VideoMenu.addAction("Stop Movie")
        StopAction.setShortcut("Shift+S")
        StopAction.setStatusTip('Stop movie')
        StopAction.triggered.connect(self.Stop_function)
        
        GotoAction = VideoMenu.addAction("GoTo Frame")
        GotoAction.setShortcut("Shift+F")
        GotoAction.setStatusTip('Go to a specific frame')
        GotoAction.triggered.connect(self.goto_function)
        
        SpeedAction = VideoMenu.addAction("PlayBack Speed")
        SpeedAction.setShortcut("Shift+P")
        SpeedAction.setStatusTip('Define playback speed for video reproduction')
        SpeedAction.triggered.connect(self.speed_function)
        
        ProcessMenu = MenuBar.addMenu("&Analysis")
        
        ProcessAction = ProcessMenu.addAction("Start Tracking")
        ProcessAction.setShortcut("Ctrl+G")
        ProcessAction.setStatusTip('Estimate whisker angular displacement')
        ProcessAction.triggered.connect(self.process_function)
        
        
        PlotAction = ProcessMenu.addAction("Plot Results")
        PlotAction.setShortcut("Ctrl+P")
        PlotAction.setStatusTip('Plot estimated angular displacement')
        PlotAction.triggered.connect(self.plot_function)
        
        

        
        #the main window consist of the toolbar and the ImageViewer
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(MenuBar)
        #layout.addWidget(QHLine())
        layout.addWidget(self.displayImage)
        #self.setLayout(layout)
        self.main_Widget.setLayout(layout)
        
        self.setCentralWidget(self.main_Widget)

        self.resize(800, 650)
        self.statusBar()
        self.show()
   
    def load_file(self):
        
#        #load a file using the widget
#        name,_ = QtWidgets.QFileDialog.getOpenFileName(
#                self,'Load Image',
#                '',"Image files (*.png *.jpg *.jpeg *.tif *.tiff *.PNG *.JPG *.JPEG *.TIF *.TIFF)")
#        
#        if not name:
#            pass
#        else:
#            temp_image  = cv2.imread(name)
#            image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
#            self._current_Image = image
#            #separate color and gray images
#            if len(image.shape) == 3: #color image
#                height, width, channel = image.shape
#                bytesPerLine = 3 * width
#                img_Qt = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
#            elif len(image.shape) == 2: #gary image
#                height, width = image.shape
#                bytesPerLine = 1 * width
#                img_Qt = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_Indexed8)
#            img_show = QtGui.QPixmap.fromImage(img_Qt)
#            
#            #show the photo
#            self.displayImage.setPhoto(img_show)    
        
        #stop playback if active
        if self.timer.isActive(): #verify is the video is running 
            #stop playback
            self.timer.stop()
        
        name = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory')
        if not name:
            pass
        else:
            Files = os.listdir(name)            
            ext=('.png', '.jpg', '.jpeg', '.bmp','tif', 'tiff', '.PNG', '.JPG', '.JPEG', '.BMP', 'TIF', 'TIFF')
            Files = [i for i in Files if i.endswith(tuple(ext))]
            
            if not Files: #no items in the folder, print a critiall error message 
                QtWidgets.QMessageBox.critical(self, 'No Valid Files', 
                            'Selected folder does not contain valid files.\nPlease select another folder.')
            else:  #there are files
                #reset everything 
                self._threshold = None #threshold for image processing     
                
                self._FaceCenter = None #stores position of face center
                self._RightROI = None #stores position of right ROI
                self._LeftROI = None #stores position of left ROI
                
                #and clean scene
                self.displayImage.clean_scene()
                      
                #sort the files
                Files.sort()            
                self._FrameIndex = 0
                self._FileList = Files
                self._Folder = name
                #and pick the first one 
                temp_image  = cv2.imread(os.path.join(self._Folder,self._FileList[self._FrameIndex]))
                image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
                self._current_Image = image
                
                img_show = get_pixmap(self._current_Image, self._threshold, self._rotation_angle)
                
                #show the photo
                self.displayImage.setPhoto(img_show)  
                
    def load_video(self):
        if self.timer.isActive(): #verify is the video is running 
            #stop playback
            self.timer.stop()
            
        name,_ = QtWidgets.QFileDialog.getOpenFileName(self,'Load Video','',"Video Files(*.avi *.mp4 *.AVI *.MP4)")
            
        if not name:
            pass
        else:       
            name = os.path.normpath(name)
            VidWin = VideoWindow(name)
            VidWin.exec_()      
            
            if VidWin.Canceled:
                pass
            else : 
                #reset everything 
                self._threshold = None #threshold for image processing     
                
                self._FaceCenter = None #stores position of face center
                self._RightROI = None #stores position of right ROI
                self._LeftROI = None #stores position of left ROI
                
                #and clean scene
                self.displayImage.clean_scene()

                
                name = VidWin._newfolder
                Files = os.listdir(name)            
                ext=('.png', '.jpg', '.jpeg', '.bmp','tif', 'tiff', '.PNG', '.JPG', '.JPEG', '.BMP', 'TIF', 'TIFF')
                Files = [i for i in Files if i.endswith(tuple(ext))]
                
                self._FileList = Files
                self._Folder = name
                #and pick the first one 
                temp_image  = cv2.imread(os.path.join(self._Folder,self._FileList[self._FrameIndex]))
                image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
                self._current_Image = image
                
                img_show = get_pixmap(self._current_Image, self._threshold, self._rotation_angle)
                
                
                #show the photo
                self.displayImage.setPhoto(img_show) 
                
    def loadangular_function(self):
        if self.timer.isActive(): #verify is the video is running 
            #stop playback
            self.timer.stop()
        if (self._current_Image is not None) and (self._FileList is not None):
            if (self._FaceCenter is not None):
                
                name,_ = QtWidgets.QFileDialog.getOpenFileName(self,'Load CVS file','',"CSV Files(*.csv)")
                #verify the files by reading its first line 
                f = open(name,'r')
                line = f.readline()
                f.close()
                line = str(line)
                if 'Time' in line:
                    if 'Right' in line:
                        if 'Left' in line:
                            self._results = np.loadtxt(name, delimiter=',', skiprows=1)
                            return
                else:
                    QtWidgets.QMessageBox.warning(self, 'Error','Incorrect File')
                    return
       
        
                
    def save_function(self):
        if (self._current_Image is not None) and (self._FileList is not None):
            name,_ = QtWidgets.QFileDialog.getSaveFileName(self, 'Select File to Save', '',"Whisker File (*.whisker)")
            
            if not name:
                pass
            else:
                name = os.path.normpath(name)
    
                #if (self._threshold is not None):
                    #copy everything from the image
                self._FaceCenter = self.displayImage._FaceCenter
                self._RightROI = self.displayImage._RightROI
                self._LeftROI = self.displayImage._LeftROI
                if (self._FaceCenter is not None):

                    if (self._RightROI is not None):

                        if (self._LeftROI is not None):

                            SaveTXT(name = name, RightROI=self._RightROI, LeftROI=self._LeftROI, FaceCenter=self._FaceCenter, threshold = self._threshold)
                            
                        else:

                            QtWidgets.QMessageBox.warning(self, 'Error','Left ROI not defined')
                            return
                    else:

                        QtWidgets.QMessageBox.warning(self, 'Error','Right ROI not defined')
                        return
                else:

                    QtWidgets.QMessageBox.warning(self, 'Error','Face midline not defined')
                    return
                #else:
                #    QtWidgets.QMessageBox.warning(self, 'Error','Threshold not defined')
                #    return
   
    def loadsettings_function(self):
        
        if (self._current_Image is not None) and (self._FileList is not None):
            #load a file using the widget
            name,_ = QtWidgets.QFileDialog.getOpenFileName(self,'Load File','',"Whisker File (*.whisker)")
            
            if not name:
                pass
            else:       
                name = os.path.normpath(name)
                self._FaceCenter, self._threshold, self._RightROI, self._LeftROI   =  ReadTXT(name)
                img_show = get_pixmap(self._current_Image, self._threshold, self._rotation_angle)
                    
                #show the photo
                self.displayImage.setPhoto(img_show)  
                self.displayImage.draw_from_txt(self._FaceCenter, self._RightROI, self._LeftROI)
                
                    
    def Forward_function(self):
        #stop playback if active
        if self.timer.isActive(): #verify is the video is running 
            #stop playback
            self.timer.stop()
        
        #move the video forward
        if self._current_Image is not None: #verify that there is an image on screen
            if self._FileList is not None: #verify that file list is not empy
                if self._FrameIndex < len(self._FileList):
                    self._FrameIndex += 1
                    temp_image  = cv2.imread(os.path.join(self._Folder,self._FileList[self._FrameIndex]))
                    image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
                    self._current_Image = image
                    
                    img_show = get_pixmap(self._current_Image, self._threshold, self._rotation_angle)
                    
                    #show the photo
                    self.displayImage.setPhoto(img_show)  
                    
                

    def Backward_function(self):
        #stop playback if active
        if self.timer.isActive(): #verify is the video is running 
            #stop playback
            self.timer.stop()
        
        #move the video backwards
        if self._current_Image is not None: #verify that there is an image on screen
            if self._FileList is not None: #verify that file list is not empy
                if self._FrameIndex > 0:
                    self._FrameIndex -= 1
                    temp_image  = cv2.imread(os.path.join(self._Folder,self._FileList[self._FrameIndex]))
                    image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
                    self._current_Image = image
                    
                    img_show = get_pixmap(self._current_Image, self._threshold, self._rotation_angle)
                    
                    #show the photo
                    self.displayImage.setPhoto(img_show)  
                    
                    
    def Play_function(self):
        #play the frames as video
        if self._current_Image is not None: #verify that there is an image on screen
            if self._FileList is not None: #verify that file list is not empy
                        
                    self.timer.timeout.connect(self.nextFrame_function)
                    self.timer.start(1000.0/self._fps)
   
    
    def nextFrame_function(self):
               
        if self._FrameIndex < len(self._FileList):
            self._FrameIndex += 1
            temp_image  = cv2.imread(os.path.join(self._Folder,self._FileList[self._FrameIndex]))
            image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
            self._current_Image = image
            
            img_show = get_pixmap(self._current_Image, self._threshold, self._rotation_angle)
            
            #show the photo
            self.displayImage.setPhoto(img_show) 
        else:
            self.timer.stop()    
            
                
            
    def Stop_function(self):
        #stop playback if active
        if self.timer.isActive(): #verify is the video is running 
            #stop playback
            self.timer.stop()
                  
                    
    def goto_function(self):
        #stop playback if active
        if self.timer.isActive(): #verify is the video is running 
            #stop playback
            self.timer.stop()
        
        if self._current_Image is not None: #verify that there is an image on screen
            if self._FileList is not None: #verify that file list is not empy
                self.goto = GoToWindow(self._FileList, self._FrameIndex)
                self.goto.exec_()
                
                if self.goto.Canceled is False:
                    #update threshold 
                    self._FrameIndex = self.goto._FrameIndex 
                    temp_image  = cv2.imread(os.path.join(self._Folder,self._FileList[self._FrameIndex]))
                    image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
                    self._current_Image = image
                    
                    img_show = get_pixmap(self._current_Image, self._threshold, self._rotation_angle)
                    
                    #show the photo
                    self.displayImage.setPhoto(img_show)  
                else:
                    pass
                            
    def speed_function(self):

        isActive = False #this variable informs if the video was runnig 
        if self.timer.isActive(): #verify is the video is running 
            isActive = True
            #stop playback
            self.timer.stop()
        
        if self._current_Image is not None: #verify that there is an image on screen
            if self._FileList is not None: #verify that file list is not empy
                self.speed = FPSWindow(self._fps)
                self.speed.exec_()
                
                if self.speed.Canceled is False:
                    #update threshold 
                    self._fps = self.speed._fps
                    
                    if isActive: #if the video was running then make it run again 
                        
                        self.timer.timeout.connect(self.nextFrame_function)
                        self.timer.start(1000.0/self._fps)
                else:
                    pass        
        
    def RigthROI_function(self):
        #stop playback if active
        if self.timer.isActive(): #verify is the video is running 
            #stop playback
            self.timer.stop()
        
        #allow the user to select multiple points in the right side of the face 
        if self._current_Image is not None:
            if self.displayImage._FaceCenter is not None:
                rect = QtCore.QRectF(self.displayImage._photo.pixmap().rect())
                view_width=rect.width()
                #view_height=rect.height()

                if self.displayImage._FaceCenter[0] >= 0 and self.displayImage._FaceCenter[0] <= view_width:
                    #remove what is in the screen 
                    for item in self.displayImage._scene.items():
    
                        if isinstance(item, QtWidgets.QGraphicsPolygonItem):
                            rect = item.boundingRect()
                            if rect.x() <= self.displayImage._FaceCenter[0]:
                                self.displayImage._scene.removeItem(item)
                            
                        elif isinstance(item, QtWidgets.QGraphicsEllipseItem): 
                            rect = item.scenePos()
                            if rect.x() <= self.displayImage._FaceCenter[0]:
                                self.displayImage._scene.removeItem(item)
                                
                    #remove previous data
                    self.displayImage._temp_storage = []
                    self.displayImage._RightROI = None
                                
                    self.displayImage._isRightROI = True 
                    
                    
    def LeftROI_function(self):
        #stop playback if active
        if self.timer.isActive(): #verify is the video is running 
            #stop playback
            self.timer.stop()
        
        #allow the user to select multiple points in the right side of the face 
        if self._current_Image is not None:
            if self.displayImage._FaceCenter is not None:
                rect = QtCore.QRectF(self.displayImage._photo.pixmap().rect())
                view_width=rect.width()
                #view_height=rect.height()

                if self.displayImage._FaceCenter[0] >= 0 and self.displayImage._FaceCenter[0] <= view_width:
                    #remove what is in the screen 
                    for item in self.displayImage._scene.items():
    
                        if isinstance(item, QtWidgets.QGraphicsPolygonItem):
                            rect = item.boundingRect()
                            if rect.x() >= self.displayImage._FaceCenter[0]:
                                self.displayImage._scene.removeItem(item)
                            
                        elif isinstance(item, QtWidgets.QGraphicsEllipseItem): 
                            rect = item.scenePos()
                            if rect.x() >= self.displayImage._FaceCenter[0]:
                                self.displayImage._scene.removeItem(item)
                                
                    #remove previous data
                    self.displayImage._temp_storage = []
                    self.displayImage._LeftROI = None
                                
                    self.displayImage._isLeftROI = True      
                    
    def Mirror_function(self):
       
        
        if self._current_Image is not None:
            if self.displayImage._LeftROI is not None and self.displayImage._RightROI is not None:
                
                #stop playback if active
                if self.timer.isActive(): #verify is the video is running 
                    #stop playback
                    self.timer.stop()

                #both ROI are present, user needs to define which one will be removed
                box = QtWidgets.QMessageBox()
                box.setIcon(QtWidgets.QMessageBox.Question)
                box.setWindowTitle('Mirror ROI')
                box.setText('Left and Right ROI are present.\nSelect ROI to mirror.')
                box.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No|QtWidgets.QMessageBox.Cancel)
                buttonR = box.button(QtWidgets.QMessageBox.Yes)
                buttonR.setText('Right')
                buttonL = box.button(QtWidgets.QMessageBox.No)
                buttonL.setText('Left') 
                buttonC = box.button(QtWidgets.QMessageBox.Cancel)
                buttonC.setText('Cancel') 
                box.exec_()
                
                if box.clickedButton() == buttonR:
                    #erase what we know about left ROI and remove it from the screen 
                    self.displayImage._LeftROI = None
                    for item in self.displayImage._scene.items():
    
                        if isinstance(item, QtWidgets.QGraphicsPolygonItem):
                            rect = item.boundingRect()
                            if rect.x() >= self.displayImage._FaceCenter[0]:
                                self.displayImage._scene.removeItem(item)
                            
                        elif isinstance(item, QtWidgets.QGraphicsEllipseItem): 
                            rect = item.scenePos()
                            if rect.x() >= self.displayImage._FaceCenter[0]:
                                self.displayImage._scene.removeItem(item)
                                
                elif box.clickedButton() == buttonL:
                    #erase what we know about right ROI and remove it from the screen 
                    self.displayImage._RightROI =None  
                    for item in self.displayImage._scene.items():
    
                        if isinstance(item, QtWidgets.QGraphicsPolygonItem):
                            rect = item.boundingRect()
                            if rect.x() <= self.displayImage._FaceCenter[0]:
                                self.displayImage._scene.removeItem(item)
                            
                        elif isinstance(item, QtWidgets.QGraphicsEllipseItem): 
                            rect = item.scenePos()
                            if rect.x() <= self.displayImage._FaceCenter[0]:
                                self.displayImage._scene.removeItem(item)
                elif box.clickedButton() == buttonC:
                    pass
                
            
            if self.displayImage._LeftROI is None: 
                #user wants to mirror the righ ROI to the left 
                self.displayImage.MirrorROI('Right')
                
            elif self.displayImage._RightROI is None:
                #user wants to mirror the left ROI to the right 
                self.displayImage.MirrorROI('Left')
            
        
    def face_center(self):
        #stop playback if active
        if self.timer.isActive(): #verify is the video is running 
            #stop playback
            self.timer.stop()
        
        #allow the user to click in some point of the image and draw two lines indicating the center of the face (vertical and horizontal)
        if self._current_Image is not None:
            #remove all lines in the graph
            for item in self.displayImage._scene.items():
                if isinstance(item, QtWidgets.QGraphicsLineItem):
                    self.displayImage._scene.removeItem(item)
            
            self.displayImage._isFaceCenter = True
            self.displayImage._FaceCenter = None

    

    def threhold_function(self):
        #stop playback if active
        if self.timer.isActive(): #verify is the video is running 
            #stop playback
            self.timer.stop()
        
        if self._current_Image is not None:
            
            if self._threshold is None:
                temp = self._current_Image.copy()
                temp = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
                hist = cv2.calcHist([temp],[0],None,[256],[0,256]) 
                elem = np.argmax(hist)
                if elem>5:
                    elem=elem-5           
                
                self.th = ThresholdWindow(elem)
                self.th.Threshold_value.connect(self.test_threshold)
                self.th.exec_()
                if self.th.Canceled is False:
                    #update threshold 
                    self._threshold = self.th.threshold 
                
            else:
                self.th = ThresholdWindow(self._threshold)
                self.th.Threshold_value.connect(self.test_threshold)
                self.th.exec_()
                if self.th.Canceled is False:
                    #update threshold 
                    self._threshold = self.th.threshold 
                    
                    
            img_show = get_pixmap(self._current_Image, self._threshold, self._rotation_angle)
            self.displayImage.setPhoto(img_show)
            
            self.th = None
    

    def test_threshold(self, threshold):
        img_show = get_pixmap(self._current_Image, threshold, self._rotation_angle)            
        #show the photo
        self.displayImage.setPhoto(img_show)            
    
    def reset_threshold_function(self):
        
        self._threshold = None
        img_show = get_pixmap(self._current_Image, self._threshold, self._rotation_angle)
            
        #show the photo
        self.displayImage.setPhoto(img_show)  
        
        
    def rotate_function(self):
        #stop playback if active
        if self.timer.isActive(): #verify is the video is running 
            #stop playback
            self.timer.stop()
        
        if self._current_Image is not None:
            self.rt = RotationAngleWindow(self._rotation_angle)
            self.rt.Rotation_Angle_value.connect(self.test_rotation)
            self.rt.exec_()
            if self.rt.Canceled is False:
                #update threshold 
                self._rotation_angle = self.rt._rotation_angle
                        
                        
            img_show = get_pixmap(self._current_Image, self._threshold, self._rotation_angle)
            self.displayImage.setPhoto(img_show)
            
            self.rt = None
            
    
    def test_rotation(self, rotation_angle):
        img_show = get_pixmap(self._current_Image, self._threshold, rotation_angle)            
        #show the photo
        self.displayImage.setPhoto(img_show)  
    
    
    def reset_rotate_function(self):
        
        self._rotation_angle = None
        img_show = get_pixmap(self._current_Image, self._threshold, self._rotation_angle)
            
        #show the photo
        self.displayImage.setPhoto(img_show) 
                                          

    def process_function(self):
        #stop playback if active
        if self.timer.isActive(): #verify is the video is running 
            #stop playback
            self.timer.stop()
            
       
        #verify that ererything exist and is in memory 
        if (self._current_Image is not None) and (self._FileList is not None):
            if (self._threshold is not None):
                #copy everything from the image
                self._FaceCenter = self.displayImage._FaceCenter
                self._RightROI = self.displayImage._RightROI
                self._LeftROI = self.displayImage._LeftROI
                
                
                #get image size, to verify location of ROI and face Center
                rect = QtCore.QRectF(self.displayImage._photo.pixmap().rect())
                view_width=rect.width()
                view_height=rect.height()
                #print(view_width, view_height)
                
                if (self._FaceCenter is not None):
                    #verify position of face center 
                    if self._FaceCenter[0]<0:
                        QtWidgets.QMessageBox.warning(self, 'Error','Problem with Face Midline')
                        return
                    if self._FaceCenter[0]>view_width:
                        QtWidgets.QMessageBox.warning(self, 'Error','Problem with Face Midline')
                        return

                    if (self._RightROI is not None):
                        
                        for (x,y) in self._RightROI:
                            if x < 0:
                                QtWidgets.QMessageBox.warning(self, 'Error','Problem with Right ROI')
                                return
                            if x> view_width/2:
                                QtWidgets.QMessageBox.warning(self, 'Error','Problem with Right ROI')
                                return
                            if y < 0:
                                QtWidgets.QMessageBox.warning(self, 'Error','Problem with Right ROI')
                                return
                            if y > view_height:
                                QtWidgets.QMessageBox.warning(self, 'Error','Problem with Right ROI')
                                return

                        if (self._LeftROI is not None):
                            
                            for (x,y) in self._LeftROI:
                                if x < view_width/2:
                                    QtWidgets.QMessageBox.warning(self, 'Error','Problem with Left ROI')
                                    return
                                if x > view_width:
                                    QtWidgets.QMessageBox.warning(self, 'Error','Problem with Left ROI')
                                    return
                                if y < 0:
                                    QtWidgets.QMessageBox.warning(self, 'Error','Problem with Left ROI')
                                    return
                                if y > view_height:
                                    QtWidgets.QMessageBox.warning(self, 'Error','Problem with Left ROI')
                                    return

                            Process = ProcessWindow(List=self._FileList, folder=self._Folder, RightROI=self._RightROI, LeftROI=self._LeftROI, FaceCenter=self._FaceCenter, threshold = self._threshold)
                            Process.exec_()
                            
                            if Process.Canceles is True :
                                self._results = None
                                pass
                            else:
                                self._results = Process._results
                                
                            
                        else:

                            QtWidgets.QMessageBox.warning(self, 'Error','Left ROI not defined')
                            return
                    else:

                        QtWidgets.QMessageBox.warning(self, 'Error','Right ROI not defined')
                        return
                else:

                    QtWidgets.QMessageBox.warning(self, 'Error','Face midline not defined')
                    return
                        
                            
                            
            else:
                QtWidgets.QMessageBox.warning(self, 'Error','Threshold not defined')
                return
                                
     
    def plot_function(self):
        if self._results is not None:
            right = np.sum(self._results[:,1])
            left = np.sum(self._results[:,2])
            
            max_r = max(self._results[:,1])
            max_l = max(self._results[:,2])
            max_max = max(max_r,max_l)
            lim_max = max_max+0.1*max_max
            min_r = min(self._results[:,1])
            min_l = min(self._results[:,2])
            min_min = min(min_r,min_l)
            lim_mim = min_min+0.1*min_min
            
            lim = max(abs(lim_max), abs(lim_mim))
            
            if right != 0 and left != 0 :                
                #both sides
                fig = plt.figure()
                ax1 = fig.add_subplot(211)
                ax1.plot(self._results[:,0], self._results[:,1])
                ax1.set_ylabel('Displacement (deg)')
                ax1.set_title('Right Side')
                ax1.set_ylim(-lim,lim)
                ax1.set_xticks([]) 
                ax2 = fig.add_subplot(212)
                ax2.plot(self._results[:,0],self._results[:,2])
                ax2.set_ylabel('Displacement (deg)')
                ax2.set_xlabel('Time (s)')
                ax2.set_title('Left Side')
                ax2.set_ylim(-lim,lim)
                
            elif right != 0 and left == 0 :
                fig = plt.figure()
                ax1 = fig.add_subplot(111)
                ax1.plot(self._results[:,0], self._results[:,1])
                ax1.set_ylabel('Displacement (deg)')
                ax1.set_title('Right Side')
                ax1.set_xlabel('Time (s)')
                ax1.set_ylim(-lim,lim)
                
            elif right == 0 and left != 0 :
                fig = plt.figure()
                ax1 = fig.add_subplot(111)
                ax1.plot(self._results[:,0], self._results[:,2])
                ax1.set_ylabel('Displacement (deg)')
                ax1.set_title('Left Side')
                ax1.set_xlabel('Time (s)')
                ax1.set_ylim(-lim,lim)
                
        
        
    
    def Screenshot_function(self):
        #save the current view 
        if (self._current_Image is not None) :
            proposed_name = 'ScreenShot_' + str(self._FrameIndex)
            name,_ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',proposed_name, 'png (*.png)')

            if not name:
                pass
            else:     
                self.displayImage.screenshot(name)
                
                
    def close_app(self):  
        
        #stop playback if active
        if self.timer.isActive(): #verify is the video is running 
            #stop playback
            
            self.timer.stop()
        
        #ask is the user really wants to close the app
        choice = QtWidgets.QMessageBox.question(self, 'Message', 
                            'Do you want to exit?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        
        if choice == QtWidgets.QMessageBox.Yes :
            self.close()
            app.exec_()
        else:
            pass  
        
    def closeEvent(self, event):
        #stop playback if active
        if self.timer.isActive(): #verify is the video is running 
            #stop playback
            self.timer.stop()
        
        event.accept()
        

if __name__ == '__main__':
    
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    
    app.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))
        
    GUI = MainWindow()
    #GUI.show()
    app.exec_()
    
