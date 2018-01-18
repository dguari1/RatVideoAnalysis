# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 18:41:24 2017

@author: Diego L.Guarin -- diego_guarin at meei.harvard.edu
"""
import os 
import sys
import cv2
import numpy as np

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

#add an option to load and save parameters


from ImageViewer import ImageViewer

from threshold_window import ThresholdWindow
from goto_window import GoToWindow
from fps_window import FPSWindow


def get_pixmap(image, threshold):
    #conver an opencv image to a QtImage (Pixmap) this function takes into consideration
    #if the image is color or gray and if there is a threshold defined or not
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

class MainWindow(QtWidgets.QWidget):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        #self.setGeometry(5,60,700,500)
        self.setWindowTitle('Whisker Analysis')
        scriptDir = os.getcwd()#os.path.dirname(os.path.realpath(sys.argv[0]))
        print(scriptDir)
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'face_icon.ico'))
        self.background_color = self.palette().color(QtGui.QPalette.Background)
        #initialize the User Interface
        self.initUI()
        
        self._threshold = None #threshold for image processing 
        
        self._current_Image = None #this variable stores the image that is being displayed in the screen 
        
        self._FaceCenter = None #stores position of face center
        self._RightROI = None #stores position of right ROI
        self._LeftRIO = None #stores position of left ROI
        
        self._FrameIndex = 0  #Frame Index
        self._FileList = None #list of files to be processed
        self._Folder = None #folder where photos are located 
        
        self._fps = 24  #this variable controls the playback speed
        
        self.timer = QtCore.QTimer()  #controls video playback 
        
        
    def initUI(self):
        #local directory
        scriptDir = os.getcwd()#os.path.dirname(os.path.realpath(sys.argv[0]))

        #image
        #read the image from file        
        img_Qt = QtGui.QImage(scriptDir + os.path.sep + 'include' +os.path.sep +'icons'+ os.path.sep + 'face2.png')
        img_show = QtGui.QPixmap.fromImage(img_Qt)
        
        #the image will be displayed in the custom ImageViewer
        self.displayImage = ImageViewer()      
        self.displayImage.setPhoto(img_show)    
        
       
        
        MenuBar = QtWidgets.QMenuBar(self)
        MenuBar.setStyleSheet("font-size:18px;")
        self.setStyleSheet("""
                           QMenuBar {
                           font-size:18px;
                           background : transparent;
                           }
                           """)       
        FileMenu = MenuBar.addMenu("File")
        LoadAction = FileMenu.addAction("Select Folder")
        LoadAction.setShortcut("Ctrl+F")
        LoadAction.triggered.connect(self.load_file)
        
        ExitAction = FileMenu.addAction("Quit")
        ExitAction.setShortcut("Ctrl+Q")
        ExitAction.triggered.connect(self.close_app)
        
        
        ImageMenu = MenuBar.addMenu("Image")
                
        FaceCenterAction = ImageMenu.addAction("Find Face Center")
        FaceCenterAction.setShortcut("Ctrl+C")
        FaceCenterAction.triggered.connect(self.face_center)
        
        
        RigthROIAction = ImageMenu.addAction("Find Right ROI")
        RigthROIAction.setShortcut("Ctrl+R")
        RigthROIAction.triggered.connect(self.RigthROI_function)
        
        LeftROIAction = ImageMenu.addAction("Find Left ROI")        
        LeftROIAction.setShortcut("Ctrl+L")
        LeftROIAction.triggered.connect(self.LeftROI_function)
        
        MirrorAction = ImageMenu.addAction("Mirror ROI")
        MirrorAction.setShortcut("Ctrl+M")
        MirrorAction.triggered.connect(self.Mirror_function)
        
        ThresholdAction = ImageMenu.addAction("Find Threshold")
        ThresholdAction.setShortcut("Ctrl+T")
        ThresholdAction.triggered.connect(self.threhold_function)
        
        ResetThresholdAction = ImageMenu.addAction("Reset Threshold")
        ResetThresholdAction.setShortcut("Ctrl+Y")
        ResetThresholdAction.triggered.connect(self.reset_threshold_function)
        
        
        RotateAction = ImageMenu.addAction("Rotate Image")
        RotateAction.setShortcut("Ctrl+U")
        
        VideoMenu = MenuBar.addMenu("Video")
        ForwardAction = VideoMenu.addAction("Move Forward")
        ForwardAction.setShortcut("Shift+D")
        ForwardAction.triggered.connect(self.Forward_function)
        
        BackwardAction = VideoMenu.addAction("Move Backward")
        BackwardAction.setShortcut("Shift+A")
        BackwardAction.triggered.connect(self.Backward_function)
        
        PlayAction = VideoMenu.addAction("Play Movie")
        PlayAction.setShortcut("Shift+Z")
        PlayAction.triggered.connect(self.Play_function)
        
        StopAction = VideoMenu.addAction("Stop Movie")
        StopAction.setShortcut("Shift+S")
        StopAction.triggered.connect(self.Stop_function)
        
        GotoAction = VideoMenu.addAction("GoTo Frame")
        GotoAction.setShortcut("Shift+F")
        GotoAction.triggered.connect(self.goto_function)
        
        SpeedAction = VideoMenu.addAction("PlayBack Speed")
        SpeedAction.setShortcut("Shift+P")
        SpeedAction.triggered.connect(self.speed_function)
        
        ProcessMenu = MenuBar.addMenu("Process")
        
        NumProcessorsAction = ProcessMenu.addAction("Number of Processor")
        NumProcessorsAction.setShortcut("Ctrl+P")
        
        ProcessAction = ProcessMenu.addAction("Start Tracking")
        ProcessAction.setShortcut("Ctrl+S")
       
        
        

        
        #the main window consist of the toolbar and the ImageViewer
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(MenuBar)
        layout.addWidget(QHLine())
        layout.addWidget(self.displayImage)
        self.setLayout(layout)
        

        self.resize(800, 650)
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
        
                self._current_Image = None #this variable stores the image that is being displayed in the screen 
                
                self._FaceCenter = None #stores position of face center
                self._RightROI = None #stores position of right ROI
                self._LeftRIO = None #stores position of left ROI
                
                self._FrameIndex = 0  #Frame Index
                self._FileList = None #list of files to be processed
                self._Folder = None #folder where photos are located 
                      
                #sort the files
                Files.sort()            
                self._FrameIndex = 0
                self._FileList = Files
                self._Folder = name
                #and pick the first one 
                temp_image  = cv2.imread(os.path.join(self._Folder,self._FileList[self._FrameIndex]))
                image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
                self._current_Image = image
                
                img_show = get_pixmap(self._current_Image, self._threshold)
                
                #show the photo
                self.displayImage.setPhoto(img_show)  
                    
    def Forward_function(self):
        #move the video forward
        if self._current_Image is not None: #verify that there is an image on screen
            if self._FileList is not None: #verify that file list is not empy
                if self._FrameIndex < len(self._FileList):
                    self._FrameIndex += 1
                    temp_image  = cv2.imread(os.path.join(self._Folder,self._FileList[self._FrameIndex]))
                    image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
                    self._current_Image = image
                    
                    img_show = get_pixmap(self._current_Image, self._threshold)
                    
                    #show the photo
                    self.displayImage.setPhoto(img_show)  
                    
                

    def Backward_function(self):
        #move the video backwards
        if self._current_Image is not None: #verify that there is an image on screen
            if self._FileList is not None: #verify that file list is not empy
                if self._FrameIndex > 0:
                    self._FrameIndex -= 1
                    temp_image  = cv2.imread(os.path.join(self._Folder,self._FileList[self._FrameIndex]))
                    image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
                    self._current_Image = image
                    
                    img_show = get_pixmap(self._current_Image, self._threshold)
                    
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
            
            img_show = get_pixmap(self._current_Image, self._threshold)
            
            #show the photo
            self.displayImage.setPhoto(img_show)  
            
        else:
            self.timer.stop()
                
            
    def Stop_function(self):
        #stop playback
        self.timer.stop()
                  
                    
    def goto_function(self):
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
                    
                    img_show = get_pixmap(self._current_Image, self._threshold)
                    
                    #show the photo
                    self.displayImage.setPhoto(img_show)  
                else:
                    pass
                            
    def speed_function(self):
        if self._current_Image is not None: #verify that there is an image on screen
            if self._FileList is not None: #verify that file list is not empy
                self.speed = FPSWindow(self._fps)
                self.speed.exec_()
                
                if self.speed.Canceled is False:
                    #update threshold 
                    self._fps = self.speed._fps
                else:
                    pass        
        
    def RigthROI_function(self):
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
        #allow the user to click in some point of the image and draw two lines indicating the center of the face (vertical and horizontal)
        if self._current_Image is not None:
            #remove all lines in the graph
            for item in self.displayImage._scene.items():
                if isinstance(item, QtWidgets.QGraphicsLineItem):
                    self.displayImage._scene.removeItem(item)
            
            self.displayImage._isFaceCenter = True
            self.displayImage._FaceCenter = None

    

    def threhold_function(self):
        
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
                    
                    
            img_show = get_pixmap(self._current_Image, self._threshold)
            self.displayImage.setPhoto(img_show)
            
    
    def reset_threshold_function(self):
        self._threshold = None
        img_show = get_pixmap(self._current_Image, self._threshold)
            
        #show the photo
        self.displayImage.setPhoto(img_show)  
        
                
                    
    def test_threshold(self, threshold):
        img_show = get_pixmap(self._current_Image, threshold)            
        #show the photo
        self.displayImage.setPhoto(img_show)               
            
    def close_app(self):  
        
        
        #ask is the user really wants to close the app
        choice = QtWidgets.QMessageBox.question(self, 'Message', 
                            'Do you want to exit?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        
        if choice == QtWidgets.QMessageBox.Yes :
            self.close()
            app.exec_()
        else:
            pass  
        
    def closeEvent(self, event):
        #we need to close all the windows before closing the program  
        if self._new_window is not None:
            self._new_window.close()
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
    
