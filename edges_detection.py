# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 19:31:32 2018

@author: GUARIND
"""

#%%
import os
import re
import cv2
import numpy as np

re_digits  = re.compile(r'(\d+)')

def embedded_numbers(s):
    pieces = re_digits.split(s)
    pieces[1::2] = map(int,pieces[1::2])
    return pieces[-2]

def sort_list_with_embedded_numbers(FileList):
    return sorted(FileList, key = embedded_numbers)



path = r'C:\Users\GUARIND\Videos\Basler\background'
files = os.listdir(path)

FilesSelected = [i for i in files if i.endswith('.tiff')]

sortedFiles = sort_list_with_embedded_numbers(FilesSelected)

img = cv2.imread(os.path.join(path,sortedFiles[0]))

h,w,c = img.shape

average = np.zeros((h,w),dtype = np.float)

for file in sortedFiles:
    img = cv2.imread(os.path.join(path,file),0)
    average = average + img
    
average = average / len(sortedFiles)
average = average.astype(np.uint8)
#%%
cv2.namedWindow("Video0", cv2.WINDOW_NORMAL+cv2.WINDOW_KEEPRATIO)
cv2.imshow("Video0",average)


path2 = r'C:\Users\GUARIND\Videos\Basler\test2'
image = cv2.imread(os.path.join(path2, 'Basler acA800-510uc (22501173)_20180207_161715734_0001.tiff'),0)

no_back = average.astype(np.float)- image.astype(np.float) 
no_back = cv2.GaussianBlur(no_back.astype(np.uint8),(3,3),1)

#no_back[no_back<5] = 0
cv2.namedWindow("Video1", cv2.WINDOW_NORMAL+cv2.WINDOW_KEEPRATIO)
cv2.imshow("Video1", no_back)



#%%

import cv2
import numpy as np 
import time
import matplotlib.pyplot as plt
from scipy import ndimage



start_time = time.time()

#read gray image
path_frames = r'C:\Users\GUARIND\Videos\Basler\test1'
image1 = 'Basler acA800-510uc (22501173)_20171212_190308266_0015.tiff'
frame =  cv2.imread(path_frames + '/' + image1, 0)
#alpha = 2
#beta = 0
#frame = alpha*frame + beta
#frame = frame.astype(np.uint8)
cv2.namedWindow("Video1", cv2.WINDOW_NORMAL+cv2.WINDOW_KEEPRATIO)
cv2.imshow("Video1",frame)


#dilate to remove whiskers and other small objects
kernel = np.ones((11,11), np.uint8)
im1 = cv2.dilate(frame,kernel,iterations=1)
#apply threshold so that only the face is selected. I used the mean brightness value
th,_,_,_ = cv2.mean(im1)
im1[im1>np.ceil(th)] = 255
im1[im1<255] = 0 

#im1 = cv2.GaussianBlur(im1,(13,13),0)

#temp = cv2.bitwise_not(im1)

cv2.imshow("im",im1)
#%%
temp[temp==255] = 1
face = np.multiply(temp,frame)
cv2.imshow("Video2",face.astype(np.uint8))


#smooth edges 
#im1 = cv2.GaussianBlur(im1,(15,15),1)
h,w = im1.shape
im2 = cv2.resize(im1,(0,0),fx=1.1,fy=1.1)
n_h,n_w = im2.shape
delta_h = int((n_h-h)/2)
delta_w = int((n_w-w)/2)
im3 = im2[delta_h:h+delta_h,delta_w:w+delta_w]
im3 = cv2.bitwise_not(im3)

im_out = frame | im3

end_time= time.time()-start_time

cv2.imshow("Video2",im_out)

im_out[im_out>200] = 0
#im_out[im_out>94] = 255
cv2.namedWindow("Video2", cv2.WINDOW_NORMAL+cv2.WINDOW_KEEPRATIO)
cv2.imshow("Video2",im1)


center = [400,310]
right = im3[:,0:center[0]]
edges = cv2.Canny(right,50,100)
EDGES = np.where(edges == 255);
#temp = cv2.bitwise_not(edges)
#temp[temp==255] = 1
cv2.namedWindow("Video3", cv2.WINDOW_NORMAL+cv2.WINDOW_KEEPRATIO)
cv2.imshow("Video3",frame[:,0:center[0]] | edges)

#snout = np.where(temp[:,center[0]]==0)[0][0]
#snout = [center[0],snout]
#%%



right = im1[:,0:center[0]]
h,w = right.shape
im2 = cv2.resize(cv2.bitwise_not(right), None, fx=1, fy=1, interpolation=cv2.INTER_LINEAR)
n_h,n_w = im2.shape
delta_h = int((n_h-h)/2)
delta_w = int((n_w-w)/2)
im3 = im2[delta_h:h+delta_h,delta_w:w+delta_w]
im3 = cv2.bitwise_not(im3)

edges = cv2.Canny(im3, 50,100)

#%%




#%%
ED = np.zeros([h,2], dtype = int)
EDG = np.zeros(right.shape,dtype=np.uint8)
for k in range(0,h):
    ED[k,0] = k
    temp =np.where(edges[k,:]==255)[0]
    if temp.size:
        if temp[0] == 0:
            k=k-1
            break
        else:
            ED[k,1] = np.where(edges[k,:]==255)[0][0]
            EDG[ED[k,0],ED[k,1]] = 255
            

cv2.namedWindow("Video4", cv2.WINDOW_NORMAL+cv2.WINDOW_KEEPRATIO)        
cv2.imshow("Video4",EDG)
plt.plot(ED[:,0],ED[:,1])

#%%
from scipy.signal import savgol_filter


filter_data = savgol_filter(ED[0:405,1],7,3,0)
EDG = np.zeros(right.shape,dtype=np.uint8)
EDG[ED[0:405,0],np.round(filter_data,0).astype(int)] = 255
            

cv2.namedWindow("Video5", cv2.WINDOW_NORMAL+cv2.WINDOW_KEEPRATIO)        
cv2.imshow("Video5",EDG)

plt.plot(ED[0:405,0],filter_data)

    
#%%
Y = EDGES[0]
Y = Y[::-1]
X = EDGES[1]
X = X[::-1]
m_size = 11
RS = np.zeros([len(X)])
for k in range(0,len(X)):
    x=X[k]
    y=Y[k]
    #if k>=500:
    #    break
    
    interest = frame[y+1:y+1+m_size,x-m_size:x]
    y_image = np.zeros([m_size])
    for j in range(0,m_size):
        y_image[j] = np.argmin(interest[j,:])
    
    z = np.polyfit(range(0,m_size), y_image, 1)
    err = y_image - (range(0,m_size)*z[0] + z[1])
    rsq = 1-(np.dot(err, err)/np.dot(y_image-np.mean(y_image),y_image-np.mean(y_image)))
    RS[k] = rsq
    
RS[RS<0.8] = 0
RS[RS>=0.8] = 1
#%%    
x=X[66]
y=Y[66]
m_size = 11
interest = frame[y+1:y+1+m_size,x-m_size:x]
cv2.imshow("Video2",interest)

y_image = np.zeros([m_size])
for k in range(0,m_size):
    y_image[k] = np.argmin(interest[k,:])

z = np.polyfit(range(0,m_size), y_image, 1)
err = y_image - (range(0,m_size)*z[0] + z[1])
rsq = 1-(np.dot(err, err)/np.dot(y_image-np.mean(y_image),y_image-np.mean(y_image)))

print(rsq)

#%%
Y = EDGES[0]
Y = Y[::-1]
X = EDGES[1]
X = X[::-1]
il_edge = np.zeros([len(X)])
for k in range(0,len(X)):
    x=X[k]
    y=Y[k]
    
    il_edge[k] = frame[y,x]
    
plt.plot(il_edge)

#%%
from sklearn.decomposition import PCA
pca = PCA(n_components=2)

x=X[118]
y=Y[118]
m_size =7

interest = frame[y-int(m_size/2):y+int(m_size/2)+1,x-int(m_size/2):x+int(m_size/2)+1].copy()
y_image = np.zeros([m_size])
for k in range(0,m_size):
    y_image[k] = np.argmin(interest[k,:])



#cv2.imshow("Video2",interest)




Data = np.c_[y_image,range(0,m_size)]
pca.fit(Data)


c1 = pca.explained_variance_[0]
c2 = pca.explained_variance_[1]
if c1>=c2:
    major_axis = np.sqrt(c1)
    minor_axis = np.sqrt(c2)
else:
    major_axis = np.sqrt(c2)
    minor_axis = np.sqrt(c1)

exc= np.sqrt(1-(minor_axis**2/major_axis**2))
print(exc)


vector = pca.components_[0]
angle = np.arctan(vector[1]/vector[0])

#%%

framo = frame[:,0:center[0]] | edges

framo = cv2.line(framo, (x,y), (x+7, int(y+7*np.tan(angle))),[255,255,255])
framo= cv2.line(framo, (x,y), (x-7, int(y-7*np.tan(angle))),[255,255,255])
cv2.imshow("Video2",framo)
v = vector * 2 * np.sqrt(major_axis)


#%%
M1 = np.array([[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,1,1,1,1,1,1]])
M2 = np.array([[0,0,0,0,0,0,0],[0,0,0,0,0,1,0],[0,0,0,0,0,1,0],[0,0,0,0,0,1,0],[0,0,0,0,0,1,0],[0,0,1,1,1,1,0],[0,0,0,0,0,0,0]])
M3 = np.array([[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,1,0,0],[0,0,0,0,1,0,0],[0,0,0,1,1,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]])
M4 = np.array([[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,1,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]])
M5 = np.array([[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,1,1,0,0,0],[0,0,1,0,0,0,0],[0,0,1,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]])
M6 = np.array([[0,0,0,0,0,0,0],[0,1,1,1,1,0,0],[0,1,0,0,0,0,0],[0,1,0,0,0,0,0],[0,1,0,0,0,0,0],[0,1,0,0,0,0,0],[0,0,0,0,0,0,0]])
M7 = np.array([[1,1,1,1,1,1,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0]])

#generating a matrix with all the basis of the same size as the image, then multiply this basis matriz (7 in total)
#by the image
h_r,w_r = right.shape
how_many_x = int(np.ceil(h_r/7))
how_many_y = int(np.ceil(w_r/7))
QQ = np.zeros([h_r,w_r,7],dtype = np.uint8)
MM1 = np.tile(M1,(how_many_x,how_many_y))
MM1 = MM1.astype(np.uint8)
QQ[:,:,0] = np.multiply(right, MM1[0:h_r,0:w_r])
MM2 = np.tile(M2,(how_many_x,how_many_y))
MM2 = MM2.astype(np.uint8)
QQ[:,:,1]= np.multiply(right, MM2[0:h_r,0:w_r])
MM3 = np.tile(M3,(how_many_x,how_many_y))
MM3 = MM3.astype(np.uint8)
QQ[:,:,2] = np.multiply(right, MM3[0:h_r,0:w_r])
MM4 = np.tile(M4,(how_many_x,how_many_y))
MM4 = MM4.astype(np.uint8)
QQ[:,:,3] = np.multiply(right, MM4[0:h_r,0:w_r])
MM5 = np.tile(M5,(how_many_x,how_many_y))
MM5 = MM5.astype(np.uint8)
QQ[:,:,4] = np.multiply(right, MM5[0:h_r,0:w_r])
MM6 = np.tile(M6,(how_many_x,how_many_y))
MM6 = MM6.astype(np.uint8)
QQ[:,:,5] = np.multiply(right, MM6[0:h_r,0:w_r])
MM7 = np.tile(M7,(how_many_x,how_many_y))
MM7 = MM7.astype(np.uint8)
QQ[:,:,6] = np.multiply(right, MM7[0:h_r,0:w_r])

#finding exact number of splits (this will speed up computation)
#we don't care much for pixles to the right (animal face) or down (end of field of view)
#so these will be discarded if needed

if how_many_x*7 > h_r:
    numSplitsX = how_many_x - 1
else:
    numSplitsX = how_many_x  

if how_many_y*7 > w_r:
    numSplitsY = how_many_y - 1
else:
    numSplitsY = how_many_y  

#divide all the matrices in 7 by 7 arrays to find local maxima 
#this is done is an "efficient" way using numpy pre-made functions. It can be done manually using for-loops but that wouldn't be very pythonic...
st = time.time()
localMin = np.zeros([numSplitsY,numSplitsX,7], dtype = object)
for k in range(0,7):
    ColumnDivision = np.hsplit(QQ[:,0:numSplitsY*7,k],numSplitsY)
    for m,column in enumerate(ColumnDivision):
        RowDivision = np.vsplit(column[0:numSplitsX*7],numSplitsX)
        for l,row in enumerate(RowDivision):
            row[row==0] = 255 #remove 0 from 7x7 matrix
            _,_,temp,_ = cv2.minMaxLoc(row)
            localMin[m,l,k] = temp
                
print(time.time()-st)   


#%%
st = time.time()
#create the basis that will be used to search for whisker-like structures. This idea was taken from 
#Clack, Nathan G., et al. "Automated tracking of whiskers in videos of head fixed rodents." PLoS computational biology 8.7 (2012)
PartitionDos=np.zeros([7,7,7])
PartitionDos[:,:,0] = np.array([[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,0,0,0,0,0,1],[0,1,1,1,1,1,1]])
PartitionDos[:,:,1] = np.array([[0,0,0,0,0,0,0],[0,0,0,0,0,1,0],[0,0,0,0,0,1,0],[0,0,0,0,0,1,0],[0,0,0,0,0,1,0],[0,0,1,1,1,1,0],[0,0,0,0,0,0,0]])
PartitionDos[:,:,2] = np.array([[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,1,0,0],[0,0,0,0,1,0,0],[0,0,0,1,1,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]])
PartitionDos[:,:,3] = np.array([[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,1,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]])
PartitionDos[:,:,4] = np.array([[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,1,1,0,0,0],[0,0,1,0,0,0,0],[0,0,1,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]])
PartitionDos[:,:,5] = np.array([[0,0,0,0,0,0,0],[0,1,1,1,1,0,0],[0,1,0,0,0,0,0],[0,1,0,0,0,0,0],[0,1,0,0,0,0,0],[0,1,0,0,0,0,0],[0,0,0,0,0,0,0]])
PartitionDos[:,:,6] = np.array([[1,1,1,1,1,1,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0],[1,0,0,0,0,0,0]])



WorkMatrix = right.copy()
for l in range(3, w_r-3):
    for m in range(3,h_r-3):
        if right[m,l] == 0:
            pass
        else:
            SelectedArea = WorkMatrix[m-3:m+4,l-3:l+4]
            for k in range(0,7):
                TEMP = np.multiply(PartitionDos[:,:,k],SelectedArea)
                TEMP[TEMP==0] = 255
                _,_,temp,_ = cv2.minMaxLoc(TEMP)
                

print(time.time()-st)      
    
    

#QQ =  QQ.astype(np.uint8)
#%%
cv2.imshow("Video2",right)
#cv2.waitKey(500)
#cv2.imshow("Video2",QQ[:,:,2])

#%%


#find edges in image 
edges = cv2.Canny(im1_smooth,100,200)
h,w = edges.shape
n_edges = cv2.resize(edges,(0,0),fx=1.06,fy=1.06)
n_h,n_w = n_edges.shape
#delta_h = int((n_h-h)/2)
delta_w = int((n_w-w)/2)
#n_edges = n_edges[delta_h:h+delta_h,delta_w:w+delta_w]
n_edges = n_edges[0:h,delta_w:w+delta_w]


#cv2.imshow("Video1",n_edges)
#cv2.imshow("Video1", cv2.addWeighted(frame,1,n_edges,1,0))

mask = np.zeros((h+2, w+2), np.uint8)
 
# Floodfill from point (0, 0)
n_edges = cv2.bitwise_not(n_edges)
cv2.floodFill(n_edges, mask, (0,0), 0);


im_out = frame | n_edges
cv2.imshow("Video1",im_out)


#%%
#test circle

IM1 = np.zeros([500,400],dtype = np.uint8)
IM1 = cv2.circle(IM1,(200,0),50,[255,255,255])


cv2.namedWindow("IM_test", cv2.WINDOW_NORMAL+cv2.WINDOW_KEEPRATIO)
cv2.imshow("IM_test",IM1)


h,w = IM1.shape
IM2 = cv2.resize(IM1,(0,0),fx=1.25,fy=1.25,interpolation = cv2.INTER_LINEAR)
#cv2.imshow("IM_test",IM2)
n_h,n_w = IM2.shape
delta_h = int((n_h-h)/2)
delta_w = int((n_w-w)/2)
IM3= IM2[int(delta_h/25):h+int(delta_h/25),delta_w:w+delta_w]
#IM3 = IM2[delta_h:h+delta_h,delta_w:w+delta_w]

cv2.imshow("IM_test",IM1|IM3)

#%%
frame1 = frame.copy()
frame1 = cv2.flip(frame1,-1)
cv2.imshow("IM_test",frame1)
framo = np.vstack((frame1,frame))


framo_large = cv2.resize(framo, None, fx=1.025, fy=1.025, interpolation=cv2.INTER_LINEAR)
h,w = frame.shape
n_h,n_w = framo_large.shape
delta_h = int((n_h-h)/2)
delta_w = int((n_w-w)/2)

temp = framo_large[h:2*h,delta_w:w+delta_w]

cv2.imshow("IM_test",frame|temp)

