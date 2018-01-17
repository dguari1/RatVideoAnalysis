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

from threshold import ThresholdWindow



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
        
        ThresholdAction = ImageMenu.addAction("Define Threshold")
        ThresholdAction.setShortcut("Ctrl+T")
        ThresholdAction.triggered.connect(self.threhold_function)
        
        RotateAction = ImageMenu.addAction("Rotate Image")
        RotateAction.setShortcut("Ctrl+U")

        FaceCenterAction = ImageMenu.addAction("Define Face Center")
        FaceCenterAction.setShortcut("Ctrl+C")
        
        RigthROIAction = ImageMenu.addAction("Define Right ROI")
        RigthROIAction.setShortcut("Ctrl+R")
        
        LeftROIAction = ImageMenu.addAction("Define Left ROI")        
        LeftROIAction.setShortcut("Ctrl+L")
        
        VideoMenu = MenuBar.addMenu("Video")
        ForwardAction = VideoMenu.addAction("Move Forvward")
        ForwardAction.setShortcut("Shift+F")
        
        BackwardsAction = VideoMenu.addAction("Move Backwards")
        BackwardsAction.setShortcut("Shift+A")
        
        
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
        
        
#    def face_center(self):
#        #find a line connecting the center of both iris and then fit a perperdicular
#        #line in the middle
#        if self.displayImage._shape is not None:
#            
#            if self._toggle_lines == True:
#                self._toggle_lines = False
#                points =  estimate_lines(self.displayImage._opencvimage, 
#                                     self.displayImage._lefteye, 
#                                     self.displayImage._righteye)
#                self.displayImage._points = points
#                self.displayImage.set_update_photo()
#            else:
#                self.displayImage._points = None
#                self.displayImage.set_update_photo()
#                self._toggle_lines = True    
            
            
    def load_file(self):
        
        #load a file using the widget
        name,_ = QtWidgets.QFileDialog.getOpenFileName(
                self,'Load Image',
                '',"Image files (*.png *.jpg *.jpeg *.tif *.tiff *.PNG *.JPG *.JPEG *.TIF *.TIFF)")
        
        if not name:
            pass
        else:
            temp_image  = cv2.imread(name)
            image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
            self._current_Image = image
            height, width, channel = image.shape
            bytesPerLine = 3 * width
            img_Qt = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
            img_show = QtGui.QPixmap.fromImage(img_Qt)
            
            #show the photo
            self.displayImage.setPhoto(img_show)
    

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
                self.th.exec_()
                if self.th.Canceled is False:
                    #update threshold 
                    self._threshold = self.th.threshold 
                    
        
            if self._threshold is not None:
                if self.th.Canceled is False:                    
                    #update image
                    image = self._current_Image.copy()
                    image[image>self._threshold] = 255
                    #image = 0.299*image[:,:,0]+0.587*image[:,:,1]+0.114*image[:,:,2]
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                    self._current_Image = image.copy()
                    height, width = image.shape
                    bytesPerLine = 1 * width
                    img_Qt = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_Indexed8)
                    img_show = QtGui.QPixmap.fromImage(img_Qt)
                    
                    #show the photo
                    self.displayImage.setPhoto(img_show)
                    
                    
    def test_threshold(self, threshold):
        image = self._current_Image.copy()
        image[image>threshold] = 255
        #image = 0.299*image[:,:,0]+0.587*image[:,:,1]+0.114*image[:,:,2]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = image.shape
        bytesPerLine = 1 * width
        img_Qt = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_Indexed8)
        img_show = QtGui.QPixmap.fromImage(img_Qt)
        
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
    
