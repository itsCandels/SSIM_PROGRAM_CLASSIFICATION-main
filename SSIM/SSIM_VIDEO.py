#base#@Author: Federico Candela 
#Description Similarity in Video
#09/02/2022 UniRc

#IMPORT
from pathlib import Path
from datetime import datetime as dt
from skimage.metrics import structural_similarity
import os
import cv2
import time
import numpy as np
import pandas as pd
import argparse



import pickle
from collections import deque

#CALCOLO TEMPI DI ELABORAZIONE
start=time.time()



#PERCORSI UTENTE

ap = argparse.ArgumentParser()
ap.add_argument("-iV", "--Video", required=True,
	help="PATH_VIDEO_INPUT")
args = vars(ap.parse_args())



# MASCHERA
def mask_function (imageMath):
    y=15
    for i in imageMath:
        
        mask=np.zeros([imageMath.shape[0]-2*y,imageMath.shape[1],3],np.uint8)
        mask=imageMath[y:imageMath.shape[0]- y,0: imageMath.shape[1]]
        return mask

#DIRECTORY

db= 'DB'
pathlist = Path(db).glob('**/*.png')


#DICHIARAZIONI VARIABILI
soglia=0.9681
soglia=float(soglia)
A3D=[]
listImage=[]



for path in pathlist:
     path_in_str = str(path)
     d= os.path.normpath(path_in_str)
     listImage.append(d)
print('Nuber Picture:',len(listImage))

for i in range(len(listImage)):

    gray= cv2.cvtColor(cv2.imread(listImage[i]), cv2.COLOR_BGR2GRAY)
    #frameRes = cv2.resize(gray, (100, 100)).astype("float32")
    maskimage= mask_function(gray)
    A3D.append(maskimage)

        
#INPUT VIDEO     
cap = cv2.VideoCapture(args["Video"])
print(args["Video"])


    
hidden=0
category=[]
listframe=[]

h=[]
m=[]
s=[]
ms=[]
l=[]
nframe=0

cambio=None


fps = cap.get(cv2.CAP_PROP_FPS)

print('Total Fps:', fps)
totframe = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print ('Total Frame:', totframe)
now=dt.now()
now_time= now.strftime("%m_%d_%Y_%H:%M:%S")
print("Data & Hours:",now_time)




while nframe< (totframe-fps):

    ret,frame=cap.read()
    nframe+=1
    if not ret:
        break


    if ((nframe % (fps/2) == 0)):
        movie_frame=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)        
        maskframe= mask_function(movie_frame)
        

        milliseconds = cap.get(cv2.CAP_PROP_POS_MSEC)

        seconds = int(milliseconds//1000)
        milliseconds =milliseconds%1000
        minutes = 0
        hours = 0
        if hours >= 60:
            minutes = int(hours//60)
            hours = int(hours % 60)
    
        if seconds >= 60:

            minutes =int(seconds//60)
            seconds = int(seconds % 60)
    
        if minutes >= 60:
            hours = int(minutes//60)
            minutes = int(minutes % 60)
            
        ore=(f'{hours:02}')
        minuti=(f'{minutes:02}')
        secondi=(f'{seconds:02}')
            
        timestamp=(f'{hours:02}'+':'+f'{minutes:02}'+':'+f'{seconds:02}')
        
        t=0
        for i in range(len(listImage)):
            t=i
            p =float(structural_similarity(A3D[i],maskframe))

            if(p>soglia):
 
                d=print("SIMILARITY: {}".format(p),"LABEL:{}".format(listImage[t].split("/")[-1])[:-4],timestamp,"NFRAME:{}".format(nframe))
                
                h.append(ore)
                m.append(minuti)
                s.append(secondi)
                ms.append(milliseconds)                               
                category.append((listImage[t].split("/")[-1])[:-4])

                
                hPD=pd.DataFrame(h)
                mPD=pd.DataFrame(m)
                sPD=pd.DataFrame(s)
                msPD=pd.DataFrame(ms)
                
                timestampPD= hPD + ':' + mPD + ':' + sPD
                
                
                lPd=pd.DataFrame(l)
                categoriaPd=pd.DataFrame(category)
                timestamp1=pd.DataFrame(timestampPD)


                f=pd.DataFrame({'category':categoriaPd.iloc[:,0], 
                                'time': timestamp1.iloc[:,0], 
                                '':'\n'+lPd.iloc[:,0]})

                f.to_csv(r'classification.csv',index=False)
                old_name= r"classification.csv"
                new_name= r""+(args["Video"])[:-4]+'_'+now_time+".csv"
                os.rename(old_name,new_name)

cv2.destroyAllWindows()
cap.release()

#END ELABORATION TIME
elapsed=time.time()-start
output=dt.strftime(dt.utcfromtimestamp(elapsed), '%H:%M:%S')
print("TIME_PROCESS:",output)
