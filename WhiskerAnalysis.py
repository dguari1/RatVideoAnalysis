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

from ImageViewerandProcess import ImageViewer



class MainWindow(QtWidgets.QWidget):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        #self.setGeometry(5,60,700,500)
        self.setWindowTitle('Whisker Analysis')
        scriptDir = os.getcwd()#os.path.dirname(os.path.realpath(sys.argv[0]))
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icons'+ os.path.sep + 'face_icon.ico'))
        
        #initialize the User Interface
        self.initUI()
        
    def initUI(self):
        #local directory
        scriptDir = os.getcwd()#os.path.dirname(os.path.realpath(sys.argv[0]))

        #image
        #read the image from file        
        img_Qt = QtGui.QImage(scriptDir + os.path.sep + 'include' +os.path.sep +'icons'+ os.path.sep + 'face.png')
        img_show = QtGui.QPixmap.fromImage(img_Qt)
        
        #the image will be displayed in the custom ImageViewer
        self.displayImage = ImageViewer()      
        self.displayImage.setPhoto(img_show)    
        
        #toolbar         
        LoadAction = QtWidgets.QAction('Select Images Folder', self)
        LoadAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icons'+ os.path.sep + 'face.png'))
        #LoadAction.triggered.connect(self.load_file)
        
        FaceCenterAction = QtWidgets.QAction('Find Face Center', self)
        FaceCenterAction.setIcon( QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icons'+ os.path.sep + 'mid-face.png'))
        #FaceCenterAction.triggered.connect(self.CreatePatient)
        
        
        RigthROIAction = QtWidgets.QAction('Find Right Side ROI', self)
        RigthROIAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icons'+ os.path.sep + 'find_right_ROI.png'))
        #RigthROIAction.triggered.connect(self.displayImage.show_entire_image)
        
        LeftROIAction = QtWidgets.QAction('Find Left Side ROI', self)
        LeftROIAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icons'+ os.path.sep + 'find_left_ROI.png'))
        #LeftROIAction.triggered.connect(self.displayImage.show_entire_image)

                
        ExitAction = QtWidgets.QAction('Close', self)
        ExitAction.setIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icons'+ os.path.sep + 'close.png'))
        ExitAction.triggered.connect(self.close_app)
                
        
        #create the toolbar and add the actions 
        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.addActions((LoadAction, FaceCenterAction, RigthROIAction,
                                 LeftROIAction,ExitAction))
        
        #set the size of each icon to 50x50
        self.toolBar.setIconSize(QtCore.QSize(50,50))
        
        for action in self.toolBar.actions():
            widget = self.toolBar.widgetForAction(action)
            widget.setFixedSize(50, 50)
           
        self.toolBar.setMinimumSize(self.toolBar.sizeHint())
        self.toolBar.setStyleSheet('QToolBar{spacing:5px;}')

        
        #the main window consist of the toolbar and the ImageViewer
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolBar)
        layout.addWidget(self.displayImage)
        self.setLayout(layout)
        

        
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
        
        #if not name:
        #    pass
        #else:
            
            
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
    
