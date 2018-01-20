# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 12:54:17 2017

@author: Diego L.Guarin -- diego_guarin at meei.harvard.edu
"""

import os
import sys
from multiprocessing import Pool
from functools import partial

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtWidgets import QLabel, QPushButton, QDialog, QSpinBox, QCheckBox, QLineEdit

import matplotlib.pyplot as plt

"""

"""

        
class ProcessWindow(QDialog):
        
    
    def __init__(self):
        super(ProcessWindow, self).__init__()
        
        self._MultiProcessor = True
        self._MaxAgents =  os.cpu_count()
        if self._MaxAgents > 2:
            self._NumAgents = int(self._MaxAgents/2)
        else:
            self._NumAgents = 1
            
        self._SaveWaveforms = True
        self._FileName = None
        
        self._DisplayResults = False
        
        self._file_to_save = ''
        self._camera_fps = 1
        self._subsample = 1 
        self._minAngle = -3.5
        self._maxAngle = 3.5
        self._NumAngles = 100
        
                
        self.initUI()
        
    def initUI(self):
        
        self.setWindowTitle('Video Process')
        scriptDir = os.getcwd()#os.path.dirname(os.path.realpath(__file__))
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
        
        self._label_process1 = QLabel('Use Multiple Processors:')
        self._label_process1.setFont(newfont)
        self._label_process1.setFixedWidth(250)
        
        self._check_process_yes = QCheckBox('Yes')
        self._check_process_yes.setFont(newfont)
        self._check_process_yes.setChecked(True)
        self._check_process_yes.setFixedWidth(75)
        
        self._check_process_no = QCheckBox('No')
        self._check_process_no.setFont(newfont)
        self._check_process_no.setChecked(False)
        self._check_process_no.stateChanged.connect(self.NoParallel)
        self._check_process_no.setFixedWidth(75)
        
        self._CheckButtonGroupProcess = QtWidgets.QButtonGroup(self)
        self._CheckButtonGroupProcess.addButton(self._check_process_yes,1)
        self._CheckButtonGroupProcess.addButton(self._check_process_no,2)
        
        self._label_process2 = QLabel('Number of Processors:')
        self._label_process2.setFont(newfont)
        self._label_process2.setFixedWidth(250)
        
        
        self._spinBox_process =  QSpinBox()
        self._spinBox_process.setMinimum(1)
        self._spinBox_process.setMaximum(self._MaxAgents - 2)
        self._spinBox_process.setFont(newfont)
        self._spinBox_process.setValue(self._NumAgents)
        self._spinBox_process.setFixedWidth(150)
            
            
        ProcessBox = QtWidgets.QGroupBox('Parallel Processing')
        ProcessBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        ProcessBoxLayout = QtWidgets.QGridLayout()
        ProcessBoxLayout.addWidget(self._label_process1,0,0)
        ProcessBoxLayout.addWidget(self._check_process_yes,0,1)
        ProcessBoxLayout.addWidget(self._check_process_no,0,2)
        ProcessBoxLayout.addWidget(self._label_process2,1,0)
        ProcessBoxLayout.addWidget(self._spinBox_process,1,1,1,2)        
        
        ProcessBox.setLayout(ProcessBoxLayout)
        
        ######################################################
        
        self._label_save1 = QLabel('Save Generated Waveforms: ')
        self._label_save1.setFont(newfont)
        self._label_save1.setFixedWidth(250)
        
        self._check_save_yes = QCheckBox('Yes')
        self._check_save_yes.setFont(newfont)
        self._check_save_yes.setChecked(True)
        self._check_save_yes.setFixedWidth(75)
        
        self._check_save_no = QCheckBox('No')
        self._check_save_no.setFont(newfont)
        self._check_save_no.setChecked(False)
        self._check_save_no.stateChanged.connect(self.NoSave)
        self._check_save_no.setFixedWidth(75)
        
        self._CheckButtonGroupSave = QtWidgets.QButtonGroup(self)
        self._CheckButtonGroupSave.addButton(self._check_save_yes,1)
        self._CheckButtonGroupSave.addButton(self._check_save_no,2)
        
        self._SelectFileButton = QPushButton('&Select File', self)
        self._SelectFileButton.setFixedWidth(150)
        self._SelectFileButton.setFont(newfont)
        self._SelectFileButton.clicked.connect(self.SelectFile)       
        self._SelectFile = QLineEdit(self)
        self._SelectFile.setText(self._file_to_save) 
        self._SelectFile.setFont(newfont)
        self._SelectFile.setFixedWidth(150)    
            
        SaveBox = QtWidgets.QGroupBox('Save Results')
        SaveBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        SaveBoxLayout = QtWidgets.QGridLayout()
        SaveBoxLayout.addWidget(self._label_save1,0,0)
        SaveBoxLayout.addWidget(self._check_save_yes,0,1)
        SaveBoxLayout.addWidget(self._check_save_no,0,2)
        SaveBoxLayout.addWidget(self._SelectFileButton,1,0)
        SaveBoxLayout.addWidget(self._SelectFile,1,1,1,2)        
        
        SaveBox.setLayout(SaveBoxLayout)

        ################################################################
        
        self._label_results1 = QLabel('Plot Generated Waveforms: ')
        self._label_results1.setFont(newfont)
        self._label_results1.setFixedWidth(250)
        
        self._check_results_yes = QCheckBox('Yes')
        self._check_results_yes.setFont(newfont)
        self._check_results_yes.setChecked(True)
        self._check_results_yes.setFixedWidth(75)
        
        self._check_results_no = QCheckBox('No')
        self._check_results_no.setFont(newfont)
        self._check_results_no.setChecked(True)
        self._check_results_no.setFixedWidth(75)
        
        self._CheckButtonGroupSave = QtWidgets.QButtonGroup(self)
        self._CheckButtonGroupSave.addButton(self._check_results_yes,1)
        self._CheckButtonGroupSave.addButton(self._check_results_no,2)
        
        self._label_results2 = QLabel('Camera Frame Rate:')
        self._label_results2.setFont(newfont)
        self._label_results2.setFixedWidth(250)     
        self._spinBox_fps =  QSpinBox()
        self._spinBox_fps.setMinimum(1)
        self._spinBox_fps.setMaximum(1000)
        self._spinBox_fps.setFont(newfont)
        self._spinBox_fps.setValue(self._camera_fps)
        self._spinBox_fps.setFixedWidth(150)    
        
        self._label_results3 = QLabel('Frames to Analize:')
        self._label_results3.setFont(newfont)
        self._label_results3.setFixedWidth(250)   
        
        self._FramestoAnaalizeInitEdit = QLineEdit(self)
        self._FramestoAnaalizeInitEdit.setText('1') 
        self._FramestoAnaalizeInitEdit.setFont(newfont)
        self._FramestoAnaalizeInitEdit.setFixedWidth(70)   
        
        self._FramestoAnaalizeEndEdit = QLineEdit(self)
        self._FramestoAnaalizeEndEdit.setText('101') 
        self._FramestoAnaalizeEndEdit.setFont(newfont)
        self._FramestoAnaalizeEndEdit.setFixedWidth(70)
        
        self._label_results4 = QLabel('Sub-Sampling:')
        self._label_results4.setFont(newfont)
        self._label_results4.setFixedWidth(250)
        
        self._spinBoxSubSampling = QSpinBox()
        self._spinBoxSubSampling.setMinimum(1) 
        self._spinBoxSubSampling.setFont(newfont)
        self._spinBoxSubSampling.setValue(self._subsample)
        self._spinBoxSubSampling.setFixedWidth(150)
            
        ResultsBox = QtWidgets.QGroupBox('Results')
        ResultsBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        ResultsBoxLayout = QtWidgets.QGridLayout()
        ResultsBoxLayout.addWidget(self._label_results1,0,0)
        ResultsBoxLayout.addWidget(self._check_results_yes,0,1)
        ResultsBoxLayout.addWidget(self._check_results_no,0,2)
        ResultsBoxLayout.addWidget(self._label_results2,1,0)
        ResultsBoxLayout.addWidget(self._spinBox_fps,1,1,1,2)   
        ResultsBoxLayout.addWidget(self._label_results3,2,0)
        ResultsBoxLayout.addWidget(self._FramestoAnaalizeInitEdit,2,1)
        ResultsBoxLayout.addWidget(self._FramestoAnaalizeEndEdit,2,2)
        ResultsBoxLayout.addWidget(self._label_results4,3,0)
        ResultsBoxLayout.addWidget(self._spinBoxSubSampling,3,1,1,2)
        
        ResultsBox.setLayout(ResultsBoxLayout)

        ################################################################
        
        self._label_angles1 = QLabel('Angular Range:')
        self._label_angles1.setFont(newfont)
        self._label_angles1.setFixedWidth(250)
        
        self._AnglesInitEdit = QLineEdit(self)
        self._AnglesInitEdit.setText(str(self._minAngle)) 
        self._AnglesInitEdit.setFont(newfont)
        self._AnglesInitEdit.setFixedWidth(70)   
        
        self._AnglesEndEdit = QLineEdit(self)
        self._AnglesEndEdit.setText(str(self._maxAngle)) 
        self._AnglesEndEdit.setFont(newfont)
        self._AnglesEndEdit.setFixedWidth(70)
               
        self._label_angles2 = QLabel('Number of Angles to Analize:')
        self._label_angles2.setFont(newfont)
        self._label_angles2.setFixedWidth(250)        
        
        self._spinAngles = QSpinBox()
        self._spinAngles.setMinimum(1) 
        self._spinAngles.setMaximum(1000)
        self._spinAngles.setFont(newfont)
        self._spinAngles.setValue(self._NumAngles)
        self._spinAngles.setFixedWidth(150)
        
        
        AnglesBox = QtWidgets.QGroupBox('Digital Goniometer')
        AnglesBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        AnglesBoxLayout = QtWidgets.QGridLayout()
        AnglesBoxLayout.addWidget(self._label_angles1,0,0)
        AnglesBoxLayout.addWidget(self._AnglesInitEdit,0,1)
        AnglesBoxLayout.addWidget(self._AnglesEndEdit,0,2)
        AnglesBoxLayout.addWidget(self._label_angles2,1,0)
        AnglesBoxLayout.addWidget(self._spinAngles,1,1,1,2)
        
        AnglesBox.setLayout(AnglesBoxLayout)

        ################################################################
        
        #buttons       
        
        DoneButton = QPushButton('&Continue', self)
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
        layout.addWidget(ProcessBox)
        spacerv = QtWidgets.QWidget(self)
        spacerv.setFixedSize(0,20)
        layout.addWidget(spacerv)
        
        layout.addWidget(SaveBox)
        spacerv = QtWidgets.QWidget(self)
        spacerv.setFixedSize(0,20)
        layout.addWidget(spacerv)
        
        layout.addWidget(ResultsBox)
        spacerv = QtWidgets.QWidget(self)
        spacerv.setFixedSize(0,20)
        layout.addWidget(spacerv)
        
        layout.addWidget(AnglesBox)
        spacerv = QtWidgets.QWidget(self)
        spacerv.setFixedSize(0,20)
        layout.addWidget(spacerv)
        
        layout.addLayout(buttonLayout)
        

        
        self.setLayout(layout)

        #fix the size, the user cannot change it 
        self.resize(self.sizeHint())
        self.setFixedSize(self.size())
        
        #self.show()   
        
    def NoParallel(self):
        if self._check_process_no.isChecked():
            self._spinBox_process.setValue(1)
        else:
            self._spinBox_process.setValue(self._NumAgents)
            
    def NoSave(self):
        if self._check_save_no.isChecked():
            self._SelectFileButton.setEnabled(False)
            self._SelectFile.setEnabled(False)
        else:
            self._SelectFileButton.setEnabled(True)
            self._SelectFile.setEnabled(True)
   
        
    def SelectFile(self):
#        name,_ = QtWidgets.QFileDialog.getOpenFileName(
#                self,'Select File to Save',
#                '',"Comma-separated values  (*.csv)")
        
        name,_ = QtWidgets.QFileDialog.getSaveFileName(self, 'Select File to Save', '',"Comma-separated values  (*.csv)")

        
        if not name:
            pass
        else:
            name = os.path.normpath(name)
            
            head,tail = os.path.split(name)           
                        
            self._file_name = name
            
            self._SelectFile.setText(tail)
            self.update()
            
            
        
    def Done(self):
        
        plt.figure(1)
        plt.plot(np.linspace(0,10,5000))

        self.close()

    def Cancel(self):
        
        self.Canceled = True
        
        self.close()  

       
    def closeEvent(self, event):

        event.accept()
        
    #this function read the style sheet used to presents the GroupBox, 
    #it is located in .\include\GroupBoxStyle.qss
    def getStyleSheet(self, path):
        f = QFile(path)
        f.open(QFile.ReadOnly | QFile.Text)
        stylesheet = QTextStream(f).readAll()
        f.close()
        return stylesheet

        
if __name__ == '__main__':
#    app = QtWidgets.QApplication([])
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
       
    GUI = ProcessWindow()
    GUI.show()
    app.exec_()
    

