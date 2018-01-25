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
from PyQt5.QtWidgets import QLabel, QPushButton, QDialog, QSpinBox
"""

"""

        
class FPSWindow(QDialog):
        
    
    def __init__(self, fps=None):
        super(FPSWindow, self).__init__()
        
        if fps:
            self._fps = fps
        else:
            self._FrameIndex = 24
            
       
        #keep the old threshold in memory in case the user cancel the 
        #operation so its value will simply go back to its old number
        self._old_fps  = fps

        self.Canceled = True #informs if the operation was canceled
        
                
        self.initUI()
        
    def initUI(self):
        
        self.setWindowTitle('PlayBack Speed')
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
        
        self.label = QLabel('Frames per second:')
        self.label.setFont(newfont)
        self.label.setFixedWidth(150)
        
        self.spinBox =  QSpinBox()
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(1000)
        self.spinBox.setFont(newfont)
        self.spinBox.setFixedWidth(150)
        self.spinBox.setValue(self._fps)
        
        textLayout = QtWidgets.QHBoxLayout()
        textLayout.addWidget(self.label)
        textLayout.addWidget(self.spinBox)
        
        
        #buttons       
        
        DoneButton = QPushButton('&Accept', self)
        DoneButton.setFixedWidth(75)
        DoneButton.setFont(newfont)
        DoneButton.clicked.connect(self.Done)
        
        CancelButton = QPushButton('&Cancel', self)
        CancelButton.setFixedWidth(75)
        CancelButton.setFont(newfont)
        CancelButton.clicked.connect(self.Cancel)
        
        buttonLayout = QtWidgets.QHBoxLayout()
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
        
    def Done(self):
        self.Canceled = False
        self._fps = self.spinBox.value()
       
        self.close()

    def Cancel(self):
        
        self._fps = self._old_fps
        
        self.close()  

       
    def closeEvent(self, event):
        event.accept()

        
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
#    if not QtWidgets.QApplication.instance():
#        app = QtWidgets.QApplication(sys.argv)
#    else:
#        app = QtWidgets.QApplication.instance()
       
    GUI = FPSWindow()
    GUI.show()
    app.exec_()
    

