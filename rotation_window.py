# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 12:54:17 2017

@author: Diego L.Guarin -- diego_guarin at meei.harvard.edu
"""

import os
import sys

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QPushButton, QDialog
from PyQt5.QtCore import pyqtSignal, pyqtSlot

"""

"""

        
class RotationAngleWindow(QDialog):
        
    
    Rotation_Angle_value = pyqtSignal(float)

    
    def __init__(self, rotation_angle=None):
        super(RotationAngleWindow, self).__init__()
        
        if rotation_angle:
            self._rotation_angle = rotation_angle
        else:
            self._rotation_angle = 0
       
        #keep the old value in memory in case the user cancel the 
        #operation so its value will simply go back to its old number
        self._old_rotation_angle  = rotation_angle

        self.Canceled = True #informs if the operation was canceled
        
                
        self.initUI()
        
    def initUI(self):
        
        self.setWindowTitle('Rotation Selection')
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
        
        self.label = QLabel('Rotation Angle:')
        self.label.setFont(newfont)
        self.label.setFixedWidth(150)
        
        self.spinBox = QtWidgets.QDoubleSpinBox()
        #QtWidgets.QDoubleSpinBox
        self.spinBox.setMinimum(-30)
        self.spinBox.setMaximum(30)
        self.spinBox.setDecimals(2)
        self.spinBox.setSingleStep(0.01)
        self.spinBox.setFont(newfont)
        self.spinBox.setFixedWidth(150)
        self.spinBox.setValue(self._rotation_angle)
        self.spinBox.valueChanged.connect(self.Test)
        
        textLayout = QtWidgets.QHBoxLayout()
        textLayout.addWidget(self.label)
        textLayout.addWidget(self.spinBox)
        
        
        #buttons       
        TestButton = QPushButton('&Test', self)
        TestButton.setFixedWidth(75)
        TestButton.setFont(newfont)
        TestButton.clicked.connect(self.Test)
        
        DoneButton = QPushButton('&Accept', self)
        DoneButton.setFixedWidth(75)
        DoneButton.setFont(newfont)
        DoneButton.clicked.connect(self.Done)
        
        CancelButton = QPushButton('&Cancel', self)
        CancelButton.setFixedWidth(75)
        CancelButton.setFont(newfont)
        CancelButton.clicked.connect(self.Cancel)
        
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(TestButton)
        buttonLayout.addWidget(DoneButton)
        buttonLayout.addWidget(CancelButton)
        
        
        
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(textLayout)
        layout.addLayout(buttonLayout)
        

        
        self.setLayout(layout)

        #fix the size, the user cannot change it 
        self.resize(self.sizeHint())
        self.setFixedSize(self.size())
        #self.show()
        
    @pyqtSlot()  
    def Test(self):
        
        self._rotation_angle = self.spinBox.value()
        self.Rotation_Angle_value.emit(self._rotation_angle)
        
    def Done(self):
        
        self._rotation_angle = self.spinBox.value()
        self.Canceled = False
        self.close()

    def Cancel(self):
        
        self._rotation_angle = self._old_rotation_angle         
        self.close()  

       
    def closeEvent(self, event):

        event.accept()

        
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
#    if not QtWidgets.QApplication.instance():
#        app = QtWidgets.QApplication(sys.argv)
#    else:
#        app = QtWidgets.QApplication.instance()
       
    GUI = RotationAngleWindow()
    GUI.show()
    app.exec_()
    

