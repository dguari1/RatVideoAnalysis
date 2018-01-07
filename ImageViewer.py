# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 10:53:19 2017

@author: Diego L.Guarin -- diego_guarin at meei.harvard.edu
"""
import cv2
import numpy as np
from scipy.spatial.distance import cdist

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore


"""
This class is in charge of drawing the picture and the landmarks in the main 
window, it also takes care of lifting and re-location of landmarks. 
"""

class ImageViewer(QtWidgets.QGraphicsView):       
    
    def __init__(self):
        #usual parameters to make sure the image can be zoom-in and out and is 
        #possible to move around the zoomed-in view
        super(ImageViewer, self).__init__()
        self._zoom = 0
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(100,100,100)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setMouseTracking(True)
        

        
    def setPhoto(self, pixmap = None):
        #this function puts an image in the scece (if pixmap is not None), it
        #sets the zoom to zero 
        self._zoom = 0        
        if pixmap and not pixmap.isNull():
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            self._photo.setPixmap(pixmap)
            self.fitInView()
        else:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())

    def fitInView(self):
        #this function takes care of accomodating the view so that it can fit
        #in the scene, it resets the zoom to 0 (i think is a overkill, i took
        #it from somewhere else)
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        #self.setSceneRect(rect)
        if not rect.isNull():
            unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())        
            viewrect = self.viewport().rect()
            scenerect = self.transform().mapRect(rect)
            factor = min(viewrect.width() / scenerect.width(),
                     viewrect.height() / scenerect.height())               
            self.scale(factor, factor)
            self.centerOn(rect.center())
            self._zoom = 0                        
            
    def zoomFactor(self):
        return self._zoom
    
    def wheelEvent(self, event):
        #this take care of the zoom, it modifies the zoom factor if the mouse 
        #wheel is moved forward or backward by 20%
        if not self._photo.pixmap().isNull():
            move=(event.angleDelta().y()/120)
            if move > 0:
                factor = 1.2
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
                                        
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom <= 0:
                self._zoom = 0
                self.fitInView()
                
                
    def mousePressEvent(self, event):
        #this function takes care of lifting (if RightClick) and relocating (if
        #a point is lifted and LeftClick) landmarks. It also verifies if the 
        #user wants to manually modify the position of the iris. In that case,
        #it opens up a new window showing only the eye (left or right) where 
        #the user can select four points around the iris
        if not self._photo.pixmap().isNull():
            scenePos = self.mapToScene(event.pos())
            if event.button() == QtCore.Qt.RightButton:                                
                #if the user RightClick and no point is lifted then verify if 
                #the position of the click is close to one of the landmarks
                x_mousePos = scenePos.toPoint().x()
                y_mousePos = scenePos.toPoint().y()
                mousePos=np.array([(x_mousePos, y_mousePos)])                   
                distance=cdist(np.append(self._shape,
                                [[self._righteye[0],self._righteye[1]],
                                [self._lefteye[0],self._lefteye[1]]], axis=0)
                                , mousePos)
                distance=distance[:,0]
                PointToModify = [i for i, j in enumerate(distance) if j <=3 ]
                if PointToModify:
                    #action
                    print('hola')
                    
                self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
                self.set_update_photo()  
                
               
                    
            elif event.button() == QtCore.Qt.LeftButton:
                
                self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
                    
                            
                            
            QtWidgets.QGraphicsView.mousePressEvent(self, event)
            
    def mouseReleaseEvent(self, event):     
        #this function defines what happens when you release the mouse click 
        

        QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)

   
    def mouseDoubleClickEvent(self, event):
   

        QtWidgets.QGraphicsView.mouseDoubleClickEvent(self, event)
                

    
    def mouseMoveEvent(self, event):
        #this function takes care of the pan (move around the photo) and draggin of the eyes
                    

        QtWidgets.QGraphicsView.mouseMoveEvent(self, event)
            


    def draw_circle(self, CircleInformation ):
        #this function draws an circle with specific center and radius 
        
        Ellipse = QtWidgets.QGraphicsEllipseItem(0,0,CircleInformation[2]*2,CircleInformation[2]*2)
        #ellipse will be green
        pen = QtGui.QPen(QtCore.Qt.green)
        #set the ellipse line width according to the image size
        if self._scene.height() < 1000:
            pen.setWidth(1)
        else:
            pen.setWidth(3)
            
        Ellipse.setPen(pen)      
        #if I want to fill the ellipse i should do this:
        #brush = QtGui.QBrush(QtCore.Qt.green) 
        #Ellipse.setPen(brush)
        
        #this is the position of the top-left corner of the ellipse.......
        Ellipse.setPos(CircleInformation[0]-CircleInformation[2],CircleInformation[1]-CircleInformation[2])
        Ellipse.setTransform(QtGui.QTransform())        
        self._scene.addItem(Ellipse)
   

    def set_update_photo(self, toggle=True):
        #this function takes care of updating the view without re-setting the 
        #zoom. Is usefull for when you lift or relocate landmarks or when 
        #drawing lines in the middle of the face
        if self._opencvimage is not None:
            self._scene.removeItem(self._photo)
            
            temp_image  = self._opencvimage.copy()   
                        
            image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
            height, width, channel = image.shape
            bytesPerLine = 3 * width
            img_Qt = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
            img_show = QtGui.QPixmap.fromImage(img_Qt)
            
            self._photo.setPixmap(img_show)    
            self._scene.addItem(self._photo)
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

        
    def show_entire_image(self):
        #this is a little utility to reset the zoom with a single click
        self.fitInView()
        
        
    def resizeEvent(self, event):
        #this function assure that when the main window is resized the image 
        #is also resized preserving the h/w ratio
        self.fitInView()
        
            
            
    def update_view(self):
        #this function takes care of updating the view by re-setting the zoom.
        #is usefull to place the image in the scene for the first time
        
        
        #if shape then add shape to image
        if self._opencvimage is not None:
            temp_image  = self._opencvimage.copy()
            
            image = cv2.cvtColor(temp_image,cv2.COLOR_BGR2RGB)
            height, width, channel = image.shape
            bytesPerLine = 3 * width
            img_Qt = QtGui.QImage(image.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
            img_show = QtGui.QPixmap.fromImage(img_Qt)
            
            #show the photo
            self.setPhoto(img_show)
        
        
           
        
        
        

        
            
