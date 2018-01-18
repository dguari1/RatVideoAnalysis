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
from PyQt5.QtCore import pyqtSignal, pyqtSlot

"""

"""

        
class ThresholdWindow(QDialog):
        
    
    Threshold_value = pyqtSignal(int)

    
    def __init__(self, threshold=None):
        super(ThresholdWindow, self).__init__()
        
        if threshold:
            self.threshold = threshold 
        else:
            self.threshold = 0
       
        #keep the old threshold in memory in case the user cancel the 
        #operation so its value will simply go back to its old number
        self.old_threshold  = threshold 

        self.Canceled = False #informs if the operation was canceled
        
                
        self.initUI()
        
    def initUI(self):
        
        self.setWindowTitle('Threshold Selection')
        #scriptDir = os.getcwd()#os.path.dirname(os.path.realpath(__file__))
        #self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'include' +os.path.sep +'icon_color'+ os.path.sep + 'report_card.ico'))
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
        
        self.label = QLabel('Threshold:')
        self.label.setFont(newfont)
        self.label.setFixedWidth(150)
        
        self.spinBox =  QSpinBox()
        self.spinBox.setMinimum(0)
        self.spinBox.setMaximum(255)
        self.spinBox.setFont(newfont)
        self.spinBox.setFixedWidth(150)
        self.spinBox.setValue(self.threshold)
        
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
        
        self.threshold = self.spinBox.value()
        self.Threshold_value.emit(self.threshold)
        
    def Done(self):
        
        self.threshold = self.spinBox.value()
       
        self.close()

    def Cancel(self):
        
        self.threshold = self.old_threshold 
        self.Canceled = True
        
        self.close()  

       
    def closeEvent(self, event):

        event.accept()

        
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
#    if not QtWidgets.QApplication.instance():
#        app = QtWidgets.QApplication(sys.argv)
#    else:
#        app = QtWidgets.QApplication.instance()
       
    GUI = ThresholdWindow()
    GUI.show()
    app.exec_()
    

