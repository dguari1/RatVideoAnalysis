# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 10:53:19 2017

@author: Diego L.Guarin -- diego_guarin at meei.harvard.edu
"""
import cv2
import numpy as np
import os

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

"""
This class is in charge of drawing the picture and the landmarks in the main 
window, it also takes care of lifting and re-location of landmarks. 
"""

class ImageViewer(QtWidgets.QGraphicsView):  

    signalEmit = pyqtSignal(object,int,str)  
    finished = pyqtSignal()
    
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
        
        
        self._isFaceCenter = False #variable that indicates if the face center will be localized
        self._FaceCenter = None #this variable defines the point selected as the face center
        
        self._isRightROI = False #variable that indicates if the right ROI will be localized 
        self._RightROI = None #variable that stores the points selected as right ROI
        self._isLeftROI = False #variable that indicates if the left ROI will be localized 
        self._LeftROI = None #variable that stores the points selected as left ROI
        
        
        self._isManualEstimation = False
        self._rad = None
        
        self._temp_storage = [] #this is a variable that is used to store temporary data... :)
        
        self._temp_storage_right = [] #this is a variable that is used to store temporary data... :)
        self._temp_storage_left = [] #this is a variable that is used to store temporary data... :)
        
        
        self._isRightEyeInit = False
        self._isLeftEyeInit = False
        self._isSnoutInit = False

    def setPhotoFirstTime(self, pixmap = None, result = None):
        #this function puts an image in the scece (if pixmap is not None), it
        #sets the zoom to zero 
        self._zoom = 0        
        if pixmap and not pixmap.isNull():
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            self._photo.setPixmap(pixmap)
            self.fitInView()
            
            if (result is not None) and (self._FaceCenter is not None):
                for item in self._scene.items():
                        if isinstance(item, QtWidgets.QGraphicsLineItem):
                            if item.pen().color() == QtCore.Qt.blue:
                                self._scene.removeItem(item)
                
#                l_bar = int(self._FaceCenter[1]*0.75)
                l_bar = self._FaceCenter[1]*0.75
                dy_right= l_bar*np.tan(result[0]*np.pi/180)
                dy_left= l_bar*np.tan(result[1]*np.pi/180)
#                self.draw_line(self._FaceCenter[0],self._FaceCenter[1], self._FaceCenter[0]-l_bar, int(self._FaceCenter[1]-dy_right),1,3)
#                self.draw_line(self._FaceCenter[0],self._FaceCenter[1], self._FaceCenter[0]+l_bar, int(self._FaceCenter[1]-dy_left),1,3)
                self.draw_line(self._FaceCenter[0],self._FaceCenter[1], self._FaceCenter[0]-l_bar, self._FaceCenter[1]-dy_right,1,3)
                self.draw_line(self._FaceCenter[0],self._FaceCenter[1], self._FaceCenter[0]+l_bar, self._FaceCenter[1]-dy_left,1,3)

            if (result is None) and (self._FaceCenter is not None):
               rect = QtCore.QRectF(self._photo.pixmap().rect())
               view_width=rect.width()
               view_height=rect.height() 
               self.draw_line(0,self._FaceCenter[1],view_width,self._FaceCenter[1])
               self.draw_line(self._FaceCenter[0],0,self._FaceCenter[0],view_height)
        else:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        
    def setPhoto(self, pixmap = None, result = None):
        #this function puts an image in the scece (if pixmap is not None),   
        if pixmap and not pixmap.isNull():
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            self._photo.setPixmap(pixmap)
            
            if (result is not None) and (self._FaceCenter is not None):
                for item in self._scene.items():
                        if isinstance(item, QtWidgets.QGraphicsLineItem):
                            if item.pen().color() == QtCore.Qt.blue:
                                self._scene.removeItem(item)
                
                l_bar = int(self._FaceCenter[1]*0.75)
                dy_right= l_bar*np.tan(result[0]*np.pi/180)
                dy_left= l_bar*np.tan(result[1]*np.pi/180)
                self.draw_line(self._FaceCenter[0],self._FaceCenter[1], self._FaceCenter[0]-l_bar, int(self._FaceCenter[1]-dy_right),1,3)
                self.draw_line(self._FaceCenter[0],self._FaceCenter[1], self._FaceCenter[0]+l_bar, int(self._FaceCenter[1]-dy_left),1,3)
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
   

    @pyqtSlot()              
    def mousePressEvent(self, event):
        
        
        
        if not self._photo.pixmap().isNull():
            
            rect = QtCore.QRectF(self._photo.pixmap().rect())
            view_width=rect.width()
            view_height=rect.height()
            
            
            if self._isFaceCenter is True: #user is going to select the center of the face 
                #remove the Drag  and change cursor
                self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                self.setCursor(QtGui.QCursor(QtCore.Qt.SizeAllCursor))
                if event.button() == QtCore.Qt.LeftButton: #this will only works with left click
                    
                    scenePos = self.mapToScene(event.pos()) #take the position of the mouse
                    x_mousePos = scenePos.toPoint().x()
                    y_mousePos = scenePos.toPoint().y()
                    self._FaceCenter = [x_mousePos, y_mousePos]
                    
                    if x_mousePos>=0 and x_mousePos <= view_width:
                        self.draw_line(0,y_mousePos,view_width,y_mousePos)
                        self.draw_line(x_mousePos,0,x_mousePos,view_height)
                        
                        self.draw_text(x_mousePos,y_mousePos)
                    
            elif self._isRightROI is True: #user if going to input the points for the right ROI
                    
                if event.button() == QtCore.Qt.LeftButton: #this will only works with left click
                    #remove the Drag  and change cursor
                    self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                    self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
                    
                    
                    scenePos = self.mapToScene(event.pos()) #take the position of the mouse
                    x_mousePos = scenePos.toPoint().x()
                    y_mousePos = scenePos.toPoint().y()

                    if x_mousePos >= 0 and x_mousePos <= self._FaceCenter[0]:
                        self._temp_storage.append((x_mousePos,y_mousePos))
                        self.draw_circle([x_mousePos,y_mousePos,3])
                
                elif event.button() == QtCore.Qt.RightButton: #on right button just finish
                    
                    self._isRightROI = False
                    self._RightROI = np.asarray(self._temp_storage) #save the ROI limits as an np array. This is useful for math operations with it
                    if len(self._temp_storage) > 2:
                        self.draw_polygon(self._temp_storage)
                    self._temp_storage = []
          
            elif self._isLeftROI is True: #user if going to input the points for the left ROI
                
                if event.button() == QtCore.Qt.LeftButton: #this will only works with left click
                    #remove the Drag  and change cursor
                    self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                    self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
                    
                    
                    scenePos = self.mapToScene(event.pos()) #take the position of the mouse
                    x_mousePos = scenePos.toPoint().x()
                    y_mousePos = scenePos.toPoint().y()

                    if  x_mousePos >= self._FaceCenter[0] and x_mousePos <= view_width:
                        self._temp_storage.append((x_mousePos,y_mousePos))
                        self.draw_circle([x_mousePos,y_mousePos,3])
                
                elif event.button() == QtCore.Qt.RightButton: #on right button just finish
                    
                    self._isLeftROI = False
                    self._LeftROI = np.asarray(self._temp_storage) #save the ROI limits as an np array. This is useful for math operations with it
                    if len(self._temp_storage) > 2:
                        self.draw_polygon(self._temp_storage)
                    self._temp_storage = []
                        
            elif self._isManualEstimation is True: #the user wants to start manual marking 
                
                if event.button() == QtCore.Qt.LeftButton: #this will only works with left click
                    
                    #self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                    self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
                    
                    
                    scenePos = self.mapToScene(event.pos()) #take the position of the mouse
                    x_mousePos = scenePos.toPoint().x()
                    y_mousePos = scenePos.toPoint().y()
                                                            
                    if self._rad is not None: 
                        rad = np.sqrt((self._FaceCenter[0]-x_mousePos)**2 + (self._FaceCenter[1]-y_mousePos)**2)
                        limit1 = 0.015*self._rad
                        limit2 = 0.004*self._rad
                        if abs(rad - self._rad) >= limit1: # click was too far away from circle, user wants to drag the image
                            
                            #self.setDragMode(QtWidgets.QGraphicsView.Drag)
                            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
                            
                        else:#click was close to the circle, user wants to track whisker                        
                            #remove the Drag  and change cursor
                            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
                            
                            if (x_mousePos < self._FaceCenter[0]) and (len(self._temp_storage_right)<2): # click on the rigth side and there are less than point in the circle                              
                                
                                if abs(rad - self._rad) > limit2: #click was just close to the circle but not close enough, modify x_position so that it appears on the circle 
                                    x_mousePos = self._FaceCenter[0] - np.sqrt(self._rad**2 -(y_mousePos - self._FaceCenter[1])**2)
                                    
                                self._temp_storage_right.append((x_mousePos,y_mousePos))
                                self.draw_circle([x_mousePos,y_mousePos,1], 'small')
                                self.signalEmit.emit(np.asarray([x_mousePos,y_mousePos]),len(self._temp_storage_right),'append')
                                
                                #draw a blue line between the two selected points 
                                if len(self._temp_storage_right) == 2:
                                    x1 = self._temp_storage_right[0][0]-self._FaceCenter[0]
                                    y1 = self._temp_storage_right[0][1]-self._FaceCenter[1]
                                    
                                    x2 = self._temp_storage_right[1][0]-self._FaceCenter[0]
                                    y2 = self._temp_storage_right[1][1]-self._FaceCenter[1]
                                    
                                    p = self._rad*(x1+x2)/(np.sqrt((x1+x2)**2 + (y1+y2)**2))
                                    q = ((y1+y2)/(x1+x2))*p
                                    
                                    self.draw_line(self._FaceCenter[0],self._FaceCenter[1],p+self._FaceCenter[0],q+self._FaceCenter[1], 1, 1)
                                    
                                self.draw_line(self._FaceCenter[0],self._FaceCenter[1],x_mousePos,y_mousePos, 0, 0.1)
                                
                            elif (x_mousePos > self._FaceCenter[0]) and (len(self._temp_storage_left)<2): # click on the left side and there are less than point in the circle    
                                
                                if abs(rad - self._rad) > limit2: #click was just close to the circle but not close enough, modify x_position so that it appears on the circle  
                                    x_mousePos = self._FaceCenter[0] + np.sqrt(self._rad**2 -(y_mousePos - self._FaceCenter[1])**2) 
                                    
                                self._temp_storage_left.append((x_mousePos,y_mousePos))
                                self.draw_circle([x_mousePos,y_mousePos,1], 'small')
                                self.signalEmit.emit(np.asarray([x_mousePos,y_mousePos]),len(self._temp_storage_left), 'append')
                                
                                #draw a blue line between the two selected points 
                                if len(self._temp_storage_left) == 2:
                                    x1 = self._FaceCenter[0]-self._temp_storage_left[0][0]
                                    y1 = self._temp_storage_left[0][1]-self._FaceCenter[1]
                                    
                                    x2 = self._FaceCenter[0]-self._temp_storage_left[1][0]
                                    y2 = self._temp_storage_left[1][1]-self._FaceCenter[1]
                                    
                                    p = -self._rad*(x1+x2)/(np.sqrt((x1+x2)**2 + (y1+y2)**2))
                                    q = ((y1+y2)/(x1+x2))*abs(p)
                                    
                                    self.draw_line(self._FaceCenter[0],self._FaceCenter[1],p+self._FaceCenter[0],self._FaceCenter[1]-q, 1, 1)
                                
                                self.draw_line(self._FaceCenter[0],self._FaceCenter[1],x_mousePos,y_mousePos, 0, 0.1)                            
                                
                    else:
                            self._rad = np.sqrt((self._FaceCenter[0]-x_mousePos)**2 + (self._FaceCenter[1]-y_mousePos)**2)
                            self.draw_circle([self._FaceCenter[0],self._FaceCenter[1],self._rad], 'big')
                            self.draw_circle([x_mousePos,y_mousePos,1], 'small')
                            if (x_mousePos < self._FaceCenter[0]):                            
                                self._temp_storage_right.append((x_mousePos,y_mousePos))
                                self.signalEmit.emit(np.asarray([x_mousePos,y_mousePos]),len(self._temp_storage_right),'append')  
                            else:
                                self._temp_storage_left.append((x_mousePos,y_mousePos))
                                self.signalEmit.emit(np.asarray([x_mousePos,y_mousePos]),len(self._temp_storage_left),'append')  
                                
                            self.draw_line(self._FaceCenter[0],self._FaceCenter[1],x_mousePos,y_mousePos, 0, 0.1)
                
                elif event.button() == QtCore.Qt.RightButton: #on right button just finish

                    self._isManualEstimation = False
                    self._rad = None
                    for item in self._scene.items():
                        if isinstance(item, QtWidgets.QGraphicsEllipseItem) or isinstance(item, QtWidgets.QGraphicsLineItem): 
                            if (item.pen().color() == QtCore.Qt.red) or (item.pen().color() == QtCore.Qt.blue) or (item.pen().color() == QtCore.Qt.yellow):
                                self._scene.removeItem(item)
                    self._temp_storage_right = []    
                    self._temp_storage_left = []    
                    self.finished.emit()


            elif self._isRightEyeInit is True:

                if event.button() == QtCore.Qt.LeftButton:
                
                    scenePos = self.mapToScene(event.pos()) #take the position of the mouse
                    x_mousePos = scenePos.toPoint().x()
                    y_mousePos = scenePos.toPoint().y()     
                    self.draw_circle([x_mousePos,y_mousePos,3], 'small','cyan')  
                    self.signalEmit.emit(np.asarray([x_mousePos,y_mousePos]),0,'--')  
                    
            elif self._isLeftEyeInit is True:

                if event.button() == QtCore.Qt.LeftButton:
                
                    scenePos = self.mapToScene(event.pos()) #take the position of the mouse
                    x_mousePos = scenePos.toPoint().x()
                    y_mousePos = scenePos.toPoint().y()     
                    self.draw_circle([x_mousePos,y_mousePos,3], 'small','magenta')  
                    self.signalEmit.emit(np.asarray([x_mousePos,y_mousePos]),0,'--')  
                    
            elif self._isSnoutInit is True:

                if event.button() == QtCore.Qt.LeftButton:
                
                    scenePos = self.mapToScene(event.pos()) #take the position of the mouse
                    x_mousePos = scenePos.toPoint().x()
                    y_mousePos = scenePos.toPoint().y()
                    if abs(self._FaceCenter[0]-x_mousePos) >= 3:
                        pass
                    else:
                        self.draw_circle([x_mousePos,y_mousePos,3], 'small','white')  
                        self.signalEmit.emit(np.asarray([x_mousePos,y_mousePos]),0,'--') 

                    
            elif event.button() == QtCore.Qt.LeftButton:
                    
                    self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
                    
                          
                            
            QtWidgets.QGraphicsView.mousePressEvent(self, event)
            
            
            
    def mouseReleaseEvent(self, event):     
        #this function defines what happens when you release the mouse click
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        if self._isFaceCenter is True:
            self._isFaceCenter = False
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            for item in self._scene.items():
                if isinstance(item,QtWidgets.QGraphicsSimpleTextItem):
                            self._scene.removeItem(item)
        elif self._isRightROI is True:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        
        elif self._isLeftROI is True:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        
        elif self._isManualEstimation is True:
            #self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        elif self._isRightEyeInit is True:
            #self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        elif self._isLeftEyeInit is True:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        elif self._isSnoutInit is True:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        
        QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)

   
    def mouseDoubleClickEvent(self, event):
        
        if self._isManualEstimation is True: #the user is doing manual marking and wants to remove the information from the current frame
            self._temp_storage_right = []
            self._temp_storage_left = []
            for item in self._scene.items():
                if isinstance(item, QtWidgets.QGraphicsLineItem) or isinstance(item, QtWidgets.QGraphicsEllipseItem):
                     if (item.pen().color() == QtCore.Qt.red) or  (item.pen().color() == QtCore.Qt.blue):                                                 
                        self._scene.removeItem(item)
                        
            self.signalEmit.emit(None,0,'remove')#inform the main window that data should be removed

        QtWidgets.QGraphicsView.mouseDoubleClickEvent(self, event)
                

    
    def mouseMoveEvent(self, event):
        #this function takes care of the pan (move around the photo) and draggin face center line
        if not self._photo.pixmap().isNull():
            if self._isFaceCenter is True: #user wants to move the lines that define the center of the face
                if self._FaceCenter is not None:
                    event.accept()
                    #remove the Drag  and change cursor
                    self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                    self.setCursor(QtGui.QCursor(QtCore.Qt.SizeAllCursor))
                    #remove the lines that currently exist 
                    for item in self._scene.items():
                        if isinstance(item, QtWidgets.QGraphicsLineItem):
                            self._scene.removeItem(item)
                            
                        if isinstance(item,QtWidgets.QGraphicsSimpleTextItem):
                            self._scene.removeItem(item)
                            
                    #re-draw the lines
                    
                    scenePos = self.mapToScene(event.pos()) #take the position of the mouse
                    x_mousePos = scenePos.toPoint().x()
                    y_mousePos = scenePos.toPoint().y()
                    
                    rect = QtCore.QRectF(self._photo.pixmap().rect())
                    view_width=rect.width()
                    view_height=rect.height()
                    
                    self._FaceCenter = [x_mousePos, y_mousePos]
                    
                    if x_mousePos>=0 and x_mousePos <= view_width:
                                           
                        rect = QtCore.QRectF(self._photo.pixmap().rect())
                        view_width=rect.width()
                        view_height=rect.height()
                        self.draw_line(0,y_mousePos,view_width,y_mousePos)
                        self.draw_line(x_mousePos,0,x_mousePos,view_height)
                        self.draw_text(x_mousePos,y_mousePos)
                        
            elif self._isManualEstimation is True: #the user is locating a point around a circle 
                #remove the Drag  and change cursor
                #self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
                
                    
            elif self._isRightROI is True:
                if self._FaceCenter is not None:
                    #remove the Drag  and change cursor
                    self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                    self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))      
                    
            elif self._isLeftROI is True:
                if self._FaceCenter is not None:
                    #remove the Drag  and change cursor
                    self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                    self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))  
            
            elif self._isRightEyeInit is True:
                #remove the Drag  and change cursor
                self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))  
                
            elif self._isLeftEyeInit is True:
                #remove the Drag  and change cursor
                self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))  
                
            elif self._isSnoutInit is True:
                #remove the Drag  and change cursor
                self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))  
            #else:
            #   self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)


        QtWidgets.QGraphicsView.mouseMoveEvent(self, event)
            
    
    def draw_line(self,x0,y0,x1,y1, Type=None, dim=None):
        
        if Type is None:
            pen = QtGui.QPen(QtCore.Qt.green)
        elif Type == 0:
            pen = QtGui.QPen(QtCore.Qt.red)
        else:
            pen = QtGui.QPen(QtCore.Qt.blue)
            
        if dim is None:
            pen.setWidth(2)
        else:
            pen.setWidth(dim)   
        pen.setStyle(QtCore.Qt.SolidLine)
        self._scene.addLine(QtCore.QLineF(x0,y0,x1,y1), pen)
    
    
    def draw_text(self,x,y):

        TextItem = QtWidgets.QGraphicsSimpleTextItem()
        brush=QtGui.QBrush(QtCore.Qt.green)
        TextItem.setBrush(brush)
        TextItem.setPos(QtCore.QPointF(x+10,y-20))
        TextItem.setText("(%d,%d)"%(x,y))

        
        self._scene.addItem(TextItem)
        

    def draw_circle(self, CircleInformation, circletype = None, Color = 'red' ):
        #this function draws an circle with specific center and radius 
        
        Ellipse = QtWidgets.QGraphicsEllipseItem(0,0,CircleInformation[2]*2,CircleInformation[2]*2)
        
        if circletype is None: #draw a point
            #ellipse will be red
            pen = QtGui.QPen(QtCore.Qt.red)
            #set the ellipse line width according to the image size
            if self._scene.height() < 1000:
                pen.setWidth(1)
            else:
                pen.setWidth(3)
                
            Ellipse.setPen(pen)      
            #if I want to fill the ellipse i should do this:
            brush = QtGui.QBrush(QtCore.Qt.red) 
            Ellipse.setBrush(brush)
        elif circletype == 'big':
            #ellipse will be yellow
            pen = QtGui.QPen(QtCore.Qt.yellow)
            pen.setWidth(0.5)
            Ellipse.setPen(pen)   
        elif circletype == 'small':
            #ellipse will be yellow
            if Color is 'red':
                color = QtCore.Qt.red
            elif Color is 'yellow':
                color = QtCore.Qt.yellow
            elif Color is 'blue':
                color = QtCore.Qt.blue
            elif Color is 'cyan':
                color = QtCore.Qt.cyan
            elif Color is 'magenta':
                color = QtCore.Qt.magenta
            elif Color is 'white':
                color = QtCore.Qt.white
                
            
            pen = QtGui.QPen(color)
            pen.setWidth(1)
            Ellipse.setPen(pen)
            brush = QtGui.QBrush(color) 
            Ellipse.setBrush(brush)
              
        #this is the position of the top-left corner of the ellipse.......
        Ellipse.setPos(CircleInformation[0]-CircleInformation[2],CircleInformation[1]-CircleInformation[2])
        Ellipse.setTransform(QtGui.QTransform())        
        self._scene.addItem(Ellipse)
        
    def draw_polygon(self,poly_points):
        
        Points = QtGui.QPolygonF()
        for point in poly_points:
            Points.append(QtCore.QPointF(point[0],point[1]))
        
        Polygon = QtWidgets.QGraphicsPolygonItem()
        pen = QtGui.QPen(QtCore.Qt.red)
        pen.setWidth(2)
        Polygon.setPen(pen)
        Polygon.setPolygon(Points)
        Polygon.setTransform(QtGui.QTransform())
        self._scene.addItem(Polygon)
            

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
        
        
    def MirrorROI(self,side):
        if not self._photo.pixmap().isNull(): #verify there is photo
            
            #find image dimensions 
            #rect = QtCore.QRectF(self._photo.pixmap().rect())
            #view_width=rect.width()
            #view_height=rect.height()
            
            #this will only work if the face center is defines
            if self._FaceCenter is not None:
                
                x_center = self._FaceCenter[0]
                
                if side == 'Right':
                #user wants to mirror the right ROI into the left side...
                    #update the left ROI and draw it        
                    #self._LeftROI = np.abs([2*x_center,0]-self._RightROI)
                    self._LeftROI = [2*x_center,0]-self._RightROI
                    self._LeftROI[:,1] = abs(self._LeftROI[:,1])
                    for (x,y) in self._LeftROI:
                        self.draw_circle([x,y,3])            
                        
                    self.draw_polygon(self._LeftROI)

                
                
                elif side == 'Left':
                #user wants to mirror the right ROI into the left side...                    
                    #update the right ROI and draw it                     
                    #self._RightROI = np.abs([2*x_center,0]-self._LeftROI)
                    self._RightROI = [2*x_center,0]-self._LeftROI
                    self._RightROI[:,1] = abs(self._RightROI[:,1])
                    for (x,y) in self._RightROI:
                        self.draw_circle([x,y,3])            
                        
                    self.draw_polygon(self._RightROI)
                    
                    
    def draw_from_txt(self, FaceCenter, RightROI, leftROI):
        #draw in screen from information read from txt file
        self._FaceCenter = FaceCenter    
        self._RightROI = RightROI
        self._LeftROI = leftROI
        
        #clean scene
        for item in self._scene.items():
            if isinstance(item, QtWidgets.QGraphicsPixmapItem):
                pass
            else:
                self._scene.removeItem(item)
        
        #draw midline        
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        view_height=rect.height()
        view_width=rect.width()
        
        if self._FaceCenter is not None:
        
            self.draw_line(self._FaceCenter[0],0, self._FaceCenter[0],view_height)
            self.draw_line(0,self._FaceCenter[1],view_width, self._FaceCenter[1])
        
        if self._RightROI is not None: 
            #draw points
            for (x,y) in self._RightROI:
                self.draw_circle([x,y,3])
                
            #draw polynomials
            self.draw_polygon(self._RightROI)
            
        if self._LeftROI is not None: 
            for (x,y) in self._LeftROI:
                self.draw_circle([x,y,3])
                
            #draw polynomials
            self.draw_polygon(self._LeftROI)
            
    def screenshot(self,name):

        rect = QtCore.QRectF(self._photo.pixmap().rect())
        width=rect.width()
        height=rect.height()
        outputimg = QtGui.QPixmap(width, height)
        painter = QtGui.QPainter(outputimg)
        targetrect = QtCore.QRectF(0, 0, width, height)
        sourcerect = QtCore.QRect(0, 0, width, height)
 
        secondview = QtWidgets.QGraphicsView(self)
        secondview.setScene(self._scene)
        secondview.render(painter, targetrect, sourcerect)
        
        
        outputimg.save(name, 'PNG') 
        painter.end()
        
    def clean_scene(self):
        #clean scene
        for item in self._scene.items():
            if isinstance(item, QtWidgets.QGraphicsPixmapItem):
                pass
            else:
                self._scene.removeItem(item)
        
    def clean_results(self):
        #clean results from sreen 
        for item in self._scene.items():
            if isinstance(item, QtWidgets.QGraphicsLineItem):
                if item.pen().color() == QtCore.Qt.blue:
                    self._scene.removeItem(item)

        
            
