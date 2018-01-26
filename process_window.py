# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 12:54:17 2017

@author: Diego L.Guarin -- diego_guarin at meei.harvard.edu
"""

import os
import numpy as np


from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtWidgets import QLabel, QPushButton, QDialog, QSpinBox, QCheckBox, QLineEdit

from analysis_window import AnalysisWindow

#import matplotlib.pyplot as plt

"""
"""



class Parallel_Processing(object):    
    #this class contains info about parallel processing 
    def __init__(self):
        self._MultiProcessor = None
        self._NumAgents = None
        
class Save_Results(object):
    #this class contains info about saving results
    def __init__(self):
        self._SaveResults = None
        self._FileName = None

class Analize_Data(object):
    #this class contains info about saving generating and plotting results
    def __init__(self):
        self._AnalizeResults = None
        self._camera_fps = None
        self._InitFrame = None
        self._EndFrame = None
        self._subSampling = None

        
class ProcessWindow(QDialog):
        
    
    def __init__(self, List=None, folder=None, RightROI=None, LeftROI=None, FaceCenter=None, threshold = None):
        super(ProcessWindow, self).__init__()
        
        self._MultiProcessor = True
        self._MaxAgents =  os.cpu_count()
        if self._MaxAgents > 2:
            self._NumAgents = int(self._MaxAgents/2)
        else:
            self._NumAgents = 1
            
        self._SaveWaveforms = True
        self._FileName = None
        
        self._AnalizeResults = 'Both'
        
        self._file_to_save = ''
        self._camera_fps = 1
        self._SubSample = 1 
        self._minAngle = -3.5
        self._maxAngle = 3.5
        self._NumAngles = 100
        self._angles = np.array([],dtype = np.float)
        
        self._List = List
        self._folder= folder
        self._RightROI = RightROI
        self._LeftROI = LeftROI
        self._threshold = threshold 
        self._FaceCenter = FaceCenter
        
        self._InitFrame = 1
        if not List:
            self._EndFrame = 1
        else:
            self._EndFrame = len(List)
        
                
        self.initUI()
        
    def initUI(self):
        
        self.setWindowTitle('Video Process')
        scriptDir = os.getcwd()
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'face_icon.ico'))
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() |
                              QtCore.Qt.WindowSystemMenuHint |
                              QtCore.Qt.WindowMinMaxButtonsHint)
        
        
        #self.main_Widget = QtWidgets.QWidget(self)
        
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
        self._check_process_yes.stateChanged.connect(self.YesParallel)
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
        
        self._label_results1 = QLabel('Sides to Analize: ')
        self._label_results1.setFont(newfont)
        self._label_results1.setFixedWidth(250)
        
        self._check_results_right = QCheckBox('Right')
        self._check_results_right.setFont(newfont)
        self._check_results_right.setChecked(True)
        self._check_results_right.setFixedWidth(75)
        
        self._check_results_left = QCheckBox('Left')
        self._check_results_left.setFont(newfont)
        self._check_results_left.setChecked(True)
        self._check_results_left.setFixedWidth(75)
        
#        self._CheckButtonGroupSave = QtWidgets.QButtonGroup(self)
#        self._CheckButtonGroupSave.addButton(self._check_results_yes,1)
#        self._CheckButtonGroupSave.addButton(self._check_results_no,2)
        
        self._label_results2 = QLabel('Camera Frames per Second:')
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
        self._FramestoAnaalizeInitEdit.setText(str(self._InitFrame)) 
        self._FramestoAnaalizeInitEdit.setFont(newfont)
        self._FramestoAnaalizeInitEdit.setFixedWidth(70)   
        validator = QtGui.QIntValidator(self._InitFrame, self._EndFrame)
        self._FramestoAnaalizeInitEdit.setValidator(validator)
    
        
        
        self._FramestoAnaalizeEndEdit = QLineEdit(self)
        self._FramestoAnaalizeEndEdit.setText(str(self._EndFrame)) 
        self._FramestoAnaalizeEndEdit.setFont(newfont)
        self._FramestoAnaalizeEndEdit.setFixedWidth(70)
        validator = QtGui.QIntValidator(self._InitFrame, self._EndFrame)
        self._FramestoAnaalizeEndEdit.setValidator(validator)
        
        self._label_results4 = QLabel('Sub-Sampling:')
        self._label_results4.setFont(newfont)
        self._label_results4.setFixedWidth(250)
        
        self._spinBoxSubSampling = QSpinBox()
        self._spinBoxSubSampling.setMinimum(1) 
        self._spinBoxSubSampling.setFont(newfont)
        self._spinBoxSubSampling.setValue(self._SubSample)
        self._spinBoxSubSampling.setFixedWidth(150)
            
        ResultsBox = QtWidgets.QGroupBox('Results')
        ResultsBox.setStyleSheet(self.getStyleSheet(scriptDir + os.path.sep + 'include' + os.path.sep + 'GroupBoxStyle.qss'))
        ResultsBoxLayout = QtWidgets.QGridLayout()
        ResultsBoxLayout.addWidget(self._label_results1,0,0)
        ResultsBoxLayout.addWidget(self._check_results_right,0,1)
        ResultsBoxLayout.addWidget(self._check_results_left,0,2)
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
        validator = QtGui.QDoubleValidator(-360, 0,3)
        self._AnglesInitEdit.setValidator(validator)
        
        self._AnglesEndEdit = QLineEdit(self)
        self._AnglesEndEdit.setText(str(self._maxAngle)) 
        self._AnglesEndEdit.setFont(newfont)
        self._AnglesEndEdit.setFixedWidth(70)
        validator = QtGui.QDoubleValidator(0, 360,3)
        self._AnglesEndEdit.setValidator(validator)
               
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
            self._spinBox_process.setEnabled(False)
        else:
            self._spinBox_process.setValue(self._NumAgents)
            self._spinBox_process.setEnabled(True)
            
    def YesParallel(self):
        if self._check_process_yes.isChecked():
            self._NumAgents = int(self._MaxAgents/2)
            self._spinBox_process.setValue(self._NumAgents)
            self._spinBox_process.setEnabled(True)
        else:
            self._spinBox_process.setValue(1)
            self._spinBox_process.setEnabled(False)
            
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
                        
            self._FileName = name
            
            self._SelectFile.setText(tail)
            self.update()
            
            
        
    def Done(self):
        
        #we have to make sure that all the information was properly enter in the form
        #once that is verified, the information is stored locally and passed to 
        #the window that will take care of all the work 

        #Parallel Processing
        if self._check_process_yes.isChecked():
            self._MultiProcessor = True
            self._NumAgents = self._spinBox_process.value()
        else:
            self._MultiProcessor = False
            self._NumAgents = self._spinBox_process.value()
    
        #Save Data
        if not self._check_save_yes.isChecked():
            self._FileName = None
        else:
            fileName =  self._SelectFile.text()
            if fileName == '':
                QtWidgets.QMessageBox.warning(self, 'Error','Missing file name for data storage')
                return
            else:
                head, tail = os.path.splitext(fileName)
                if tail != '.csv':
                    QtWidgets.QMessageBox.warning(self, 'Error','Invalid file name for data storage')
                    return

        #Results
        if self._check_results_right.isChecked() and self._check_results_left.isChecked():
            self._AnalizeResults = 'Both'
        elif self._check_results_right.isChecked() and not self._check_results_left.isChecked():
            self._AnalizeResults = 'Right'
        elif not self._check_results_right.isChecked() and self._check_results_left.isChecked():
            self._AnalizeResults = 'Left'
        else:
            QtWidgets.QMessageBox.warning(self, 'Error','At least one side must be analized')
            return
             
        value_init = int(self._FramestoAnaalizeInitEdit.text())
        value_end = int(self._FramestoAnaalizeEndEdit.text())
        
        if value_end <= value_init :
            QtWidgets.QMessageBox.warning(self, 'Error','Final Frame must be greather than Initial Frame')
            return
        
        self._InitFrame = value_init
        self._EndFrame = value_end         
        
        self._SubSample = self._spinBoxSubSampling.value()
        self._camera_fps = self._spinBox_fps.value()
        
        #Digital Goniometer 
        value_init = float(self._AnglesInitEdit.text())
        value_end = float( self._AnglesEndEdit.text())
        if value_end <= value_init :
            QtWidgets.QMessageBox.warning(self, 'Error','Final Angle must be greather than Initial Angle')
            return       
        
        if value_init > 0 :
            QtWidgets.QMessageBox.warning(self, 'Error','Initial Angle must be less or equal than zero')
            return  
        
        if value_end < 0 :
            QtWidgets.QMessageBox.warning(self, 'Error','Final Angle must be greather or equal than zero')
            return  
        

        #create the list of angles to be evaluated
        self._minAngle = value_init
        self._maxAngle = value_end
        
        self._NumAngles = self._spinAngles.value()
        
        
        angles = np.linspace(self._minAngle, self._maxAngle, self._NumAngles)
        zero_ind = np.where(angles == 0)[0]
        if zero_ind.size == 1:
            pass
        elif zero_ind.size > 0:
            QtWidgets.QMessageBox.warning(self, 'Error','This is weird. There are more than one zero in the angles to evaluate....')
            return
        elif zero_ind.size == 0: #add zero to the list of angles 
            sgn_change_ind = np.where(np.diff(np.sign(angles)))[0]
            angles_neg = angles[:sgn_change_ind[0]+1]
            angles_pos = angles[sgn_change_ind[0]:]
            angles = np.r_[angles_neg, [np.float(0)],angles_pos[1:]]
        else: 
            QtWidgets.QMessageBox.warning(self, 'Error','This is weird. Unknown error with the angles.')
            return 
        
        self._angles = np.asarray(angles)
        ############################
        
        #parallel processing
        parallel = Parallel_Processing()
        parallel._MultiProcessor = self._MultiProcessor
        parallel._NumAgents = self._NumAgents
        
        
        saveInfo = Save_Results()
        saveInfo._SaveResults = self._SaveWaveforms
        saveInfo._FileName = self._FileName
        
        resultsInfo = Analize_Data()
        resultsInfo._AnalizeResults = self._AnalizeResults
        resultsInfo._camera_fps = self._camera_fps
        resultsInfo._InitFrame = self._InitFrame
        resultsInfo._EndFrame = self._EndFrame
        resultsInfo._subSampling = self._SubSample
        
        #this is where all the work will be done, this new window receives all the 
        #information from the main window and this form 
        
        runme = AnalysisWindow(self._List, self._folder, self._RightROI, self._LeftROI, self._FaceCenter, self._threshold, self._angles, parallel, saveInfo, resultsInfo)
        runme.exec_()
        
        if runme.Canceled is not True:
            runme = None
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
    app = QtWidgets.QApplication([])
#    if not QtWidgets.QApplication.instance():
#        app = QtWidgets.QApplication(sys.argv)
#    else:
#        app = QtWidgets.QApplication.instance()
#       
    GUI = ProcessWindow()
    GUI.show()
    app.exec_()
    

