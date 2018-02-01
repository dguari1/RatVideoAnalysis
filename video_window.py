# -*- coding: utf-8 -*-
"""
Created on Sat Aug 19 12:54:17 2017

@author: Diego L.Guarin -- diego_guarin at meei.harvard.edu
"""

import os
import cv2


from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QPushButton, QDialog,  QLineEdit
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import shutil
from skimage.external.tifffile import imsave
"""

"""

class FramesAnalysis(QObject):
    
    finished = pyqtSignal()
    indexFrame = pyqtSignal(int)
    
    def __init__(self,video_name, folder_name):
        super(FramesAnalysis, self).__init__()
        self._videoname = video_name
        self._foldername = folder_name
        
    @pyqtSlot()
    def ProcessVideo(self):

        self.cap = cv2.VideoCapture(self._videoname)

        length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        num_ele=len(str(length))
        success,image = self.cap.read()

        if not success:
            QtWidgets.QMessageBox.warning(self, 'Error','Error reading the video file')
            self.finished.emit()
            return 
        
        #print(length)
        
        step = 0
        
#        #we read the file sucessfully, lets create the new directory and save the files in there
#        name_frame = 'Frame_%0'+str(num_ele)+'d.tiff'
#        full_name_frame = os.path.join(self._foldername, name_frame)
#        cv2.imwrite(full_name_frame%step,image)
        
        while success:                                    

            name_frame = 'Frame_%0'+str(num_ele)+'d.tiff'
            full_name_frame = os.path.join(self._foldername, name_frame)
            #cv2.imwrite(full_name_frame%step,image)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            imsave(full_name_frame%step,image,compress=0)
            success,image = self.cap.read()
            step +=1   
                                                      
        self.cap.release()        
        self.indexFrame.emit(step)
        
        #now inform that is over
        self.finished.emit()
    

        
class VideoWindow(QDialog):
        
    

    
    def __init__(self, name=None):
        super(VideoWindow, self).__init__()
        
        
        self._name = name
        head,tail = os.path.split(name)
        self._folder = head
        self._filename_full = tail
        name_file, ext = os.path.splitext(self._filename_full)
        self._filename_noext = name_file
        
        self._newfolder = os.path.join(head,self._filename_noext)
        
        Info = QtCore.QFileInfo(name)
        self._fileSize = Info.size()
        self._fileSize = self._fileSize/(1024**2)
        
        cap = cv2.VideoCapture(self._name)
        self._length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        


         # create Thread  to take care of video processing    
        self.thread_frames = QtCore.QThread()  # no parent!

        self.Canceled = True #informs if the operation was canceled
        
        self.Processing = True #controls the poor's man "progress bar"
        self.FrameAna = None
                
        self.initUI()
        
    def initUI(self):
        
        self.setWindowTitle('Video Processing')
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
        
        self._label = QLabel('Video will be splitted into frames, and images will be stored\nin a new folder:')
        self._label.setFont(newfont)
        self._label.setFixedWidth(450)
        
        self._folder = QLineEdit(self)
        self._folder.setText(self._newfolder) 
        self._folder.setFont(newfont)
        self._folder.setFixedWidth(450)
        
        self._label2 = QLabel('Folder size will be {0} MB.'.format(int(self._fileSize)))
        self._label2.setFont(newfont)
        self._label2.setFixedWidth(450)
        
        
        #a progress bar to show progress
        self._label3 = QLabel('')
        self._label3.setFont(QtGui.QFont("Times", 25))
        self._label3.setFixedWidth(450)
        self._label3.setAlignment(QtCore.Qt.AlignCenter)
        
        self._label3a = QLabel('')
        self._label3a.setFont(newfont)
        self._label3a.setFixedWidth(450)
        self._label3a.setAlignment(QtCore.Qt.AlignCenter)
        
        
        
        self._DoneButton = QPushButton('&Accept', self)
        self._DoneButton.setFixedWidth(100)
        self._DoneButton.setFont(newfont)
        self._DoneButton.clicked.connect(self.Done)
        
        self._CancelButton = QPushButton('&Cancel', self)
        self._CancelButton.setFixedWidth(100)
        self._CancelButton.setFont(newfont)
        self._CancelButton.clicked.connect(self.Cancel)
        
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self._DoneButton)
        buttonLayout.addWidget(self._CancelButton)
        
        
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._label)
        layout.addWidget(self._folder)
        layout.addWidget(self._label2)
        layout.addWidget(self._label3a)
        layout.addWidget(self._label3)
        layout.addWidget(spacerv)
        layout.addLayout(buttonLayout)
        

        
        self.setLayout(layout)

        #fix the size, the user cannot change it 
        self.resize(self.sizeHint())
        self.setFixedSize(self.size())
        #self.show()


    def Done(self):
        if self.Processing:
            
            if os.path.isdir(self._newfolder):
                
                choice = QtWidgets.QMessageBox.question(self, 'Message', 
                            'Folder already exists. Do you want to replace it?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
            
                if choice == QtWidgets.QMessageBox.No :
                    return
                else:
                    shutil.rmtree(self._newfolder, ignore_errors=True) #eliminate folder
                    os.makedirs(self._newfolder) #create it again
            else:
                os.makedirs(self._newfolder) #create folder
            
            #move the frames processing to another thread 
            self.FrameAna = FramesAnalysis(self._name, self._newfolder)
            #move worker to new thread
            self.FrameAna.moveToThread(self.thread_frames)
            #start the new thread where the landmark processing will be performed
            self.thread_frames.start() 
            #Connect Thread started signal to Worker operational slot method
            self.thread_frames.started.connect(self.FrameAna.ProcessVideo)
            #connect signal emmited by landmarks to a function
            self.FrameAna.indexFrame.connect(self.DisplayProgressBar)
            #define the end of the thread
            self.FrameAna.finished.connect(self.thread_frames.quit)
            
            
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.UpdateProgressBar)
            self.timer.start(250)
        else:
            self.Canceled = False
            self.close()

        
    def DisplayProgressBar(self, index):
        #print('Done')
        self._TotalFrames = index+1
        self.Processing = False
        
    def UpdateProgressBar(self):
        
        if self.Processing:
            read = self._label3.text()
            if read =='':           
                self._label3.setText('.  ')
            elif read == '.  ':
                self._label3.setText('.. ')
            elif read == '.. ':
                self._label3.setText('...')
            elif read == '...':
                self._label3.setText('')
                
                
        else:
            self._label3a.setText('DONE')
            self._label3.setFont(QtGui.QFont("Times", 12))
            self._label3.setText('Number of frames Processed: {0}'.format(self._TotalFrames))
            
        
            self._DoneButton.setText('Close')
            self._CancelButton.setEnabled(False)

        

    def Cancel(self):
        
        if self.FrameAna is not None:
            self.FrameAna.cap.release()
        if self.thread_frames.isRunning():
            self.thread_frames.quit

            
        self.close()  

       
    def closeEvent(self, event):

        event.accept()

        
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
#    if not QtWidgets.QApplication.instance():
#        app = QtWidgets.QApplication(sys.argv)
#    else:
#        app = QtWidgets.QApplication.instance()
       
    GUI = VideoWindow()
    GUI.show()
    app.exec_()
    

