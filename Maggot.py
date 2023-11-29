#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 20:34:00 2019

@author: jhony_az
"""

import os
os.chdir('/Users/jhony_az/dev/SpaceJam/lib/python3.7/site-packages')
import cv2
#%%
os.chdir('/Users/jhony_az/Documents/Done/Behavioral_Assay/Vids/Demo')
import numpy as np;
import math
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt 
from matplotlib import style
from scipy.signal import find_peaks
import tkinter as tk
from tkinter import *
from tkinter import ttk
import glob
import numpy as np;
import shutil


        

#%%
LARGE_FONT=("Verdana",12)

def rescale_frame(frame,percent):

    width=int(frame.shape[1]*percent/100)
    height=int(frame.shape[0]*percent/100)
    
    dim=(width,height)
    return cv2.resize(frame,dim,interpolation=cv2.INTER_AREA)

#Converts milliseconds to minutes
def millitomin(milliseconds):
    seconds=round(milliseconds/1000,2)
    minutes=int(seconds//60)
    sec=seconds-(minutes*60)
    time=str(minutes)+':'+str(sec)
    return str(time)

#Converts frames to minutes
def frame_to_min(x,n_frame):
    #'rate' is a global variable set by main function
    sec=n_frame/rate 
    time=millitomin(sec*1000)
    return time
#Converts pixels to cm
def pixels_to_cm(pixels,radius):
    ratio=5/radius
    cm=round(pixels*(ratio),3)
    return(cm)

#Calculates the distance between two points
def point_distance(x0,y0,x1,y1):
    difference= math.sqrt((x1-x0)**2 + (y1-y0)**2)
    return(difference)
    

#Draws a line between two points (Easier to use for the program)
def drawlines(img,x0,y0,x1,y1):
    cv2.line(img,(x0,y0),(x1,y1),(0,255,0),1)

#creates a tuple (b) that will be used in giving directions for the bounding box
def Bounds_from_center(x,y):
    global b
    b=(x-20,y-20,50,50)
    return(b)

#shows the skeletons of the blobs
def skeletonize(images): 
    img=cv2.cvtColor(images,cv2.COLOR_RGB2GRAY)
    ret,img=cv2.threshold(img,220,256,cv2.THRESH_BINARY)
    size = np.size(img)
    skel = np.zeros(img.shape,np.uint8)
    
    ret,img = cv2.threshold(img,127,255,0)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    done = False
    
    while( not done):
        eroded = cv2.erode(img,element)
        temp = cv2.dilate(eroded,element)
        temp = cv2.subtract(img,temp)
        skel = cv2.bitwise_or(skel,temp)
        img = eroded.copy()
    
        zeros = size - cv2.countNonZero(img)
        if zeros==size:
            done = True
    cv2.imshow("skel",skel)


def smoothTriangle(data, degree):
    triangle=np.concatenate((np.arange(degree + 1), np.arange(degree)[::-1])) # up then down
    smoothed=[]

    for i in range(degree, len(data) - degree * 2):
        point=data[i:i + len(triangle)] * triangle
        smoothed.append(np.sum(point)/np.sum(triangle))
    # Handle boundaries
    smoothed=[smoothed[0]]*int(degree + degree/2) + smoothed
    while len(smoothed) < len(data):
        smoothed.append(smoothed[-1])
    return smoothed

    
class GUI_Behavior(tk.Tk):
    def __init__(self,*args,**kwargs):
        #*args- any argument can be passed
        #*kwargs- keyboard arguments, you pass through DICTIONARIES
        tk.Tk.__init__(self,*args,**kwargs)
        
        container=tk.Frame(self) #container to be populated, made into a frame
        container.pack(side="top",fill="both",expand=True) #Packs container into window
        
        #configurations
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)
        
        self.frames={} #creates a dictionary
        
        for F in (StartPage,Threshold_Q,Select_Thresholds_YES,
                  Select_Thresholds_NO,GRAPH_Page,
                  Time_to_Run_Indiv_Thresh,Time_to_Run_One_Thresh):
        
            frame=F(container,self) #defined later
            
            self.frames[F]=frame
        #cells of rows and columns are only as big as you need them to be
        #sticky is talking about orientation in terms of N, S,E,W        
            frame.grid(row=0,column=0,sticky="nsew") 
        
        self.show_frame(StartPage)
        
    def show_frame(self,cont):
        frame=self.frames[cont]
        frame.tkraise()
        



def New_directory(controller,Page,path):
    current_dir=str(os.getcwd())
    new_directory=str(path.get()) 
    controller.show_frame(Page)
    os.chdir(new_directory)
    print("Directory changed from:\n "+current_dir+"\nTO\n"+new_directory)
    
def Same_directory(controller,Page,path):
    current_dir=str(os.getcwd())
    controller.show_frame(Page)
    print("Current directory is: "+current_dir)

def Reset_all_Data():
    global Expecting_area_values
    global Data_array_perimeter
    global Num_of_Contractions
    global Distance_over_time_array
    global Video_graphs
    global threshold_values
    global Keypoint_X_Y
    global Arena_circles
    global Num_of_Contractions_distance
    global Total_Distance
   
    
    Expecting_area_values={}
    Data_array_perimeter={}
    Total_Distance={}
    Num_of_Contractions_distance={}
    Distance_over_time_array={}
    Video_graphs={}
    threshold_values={}
    Keypoint_X_Y={}
    Arena_circles={}

class StartPage(tk.Frame):
    
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text="ENTER new directory \nor\n select 'SAME Directory'",font=LARGE_FONT)
        label.pack(pady=0,padx=100)
        
        path=tk.StringVar()
        PathBox=tk.Entry(self,textvariable=path)
        PathBox.pack()        
             
        label2=tk.Label(self,text="* * * If first run, enter your directory using forward slashes '/' * * *",font=LARGE_FONT)
        label2.pack(pady=0,padx=100)

        button=tk.Button(self, text="NEW Directory", 
                          command=lambda: New_directory(controller,Threshold_Q,path))
        button.pack()
        
        button1=tk.Button(self, text="SAME Directory", 
                          command=lambda: Same_directory(controller,Threshold_Q,path))
        button1.pack(pady=20)
        
        current_dir=str(os.getcwd())
        #print("Current directory is: "+current_dir)
        label1=tk.Label(self,text=str("Current Directory is:\n"+current_dir),font=LARGE_FONT)
        label1.pack(pady=0,padx=100)
        
        
        
        
        button2=tk.Button(self,text='ALREADY HAVE DATA?\n Go to Graph Page!',
                          command=lambda:controller.show_frame(GRAPH_Page))#controller,PageTwo))
        button2.pack(anchor="center",pady=20)
        
        button3=tk.Button(self,text='RESET Existing DATA \n+\nParameters\n*Click once,then select other option*',
                          command=Reset_all_Data())#controller,PageTwo))
        button3.pack(anchor="center",pady=20)

class Threshold_Q(tk.Frame):
    
    
    def __init__(self,parent,controller):
       # global general_threshold
        tk.Frame.__init__(self,parent)
        
        label=tk.Label(self,text="Do you want to set thresholds\n for these videos INDIVIDUALLY?",font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        
        button1=tk.Button(self, text="YES,\nindividually", 
                          command=lambda: controller.show_frame(Select_Thresholds_YES))
        button1.pack(pady=10)
        
        button2=tk.Button(self, text="NO,\nmatch the first", 
                          command=lambda: controller.show_frame(Select_Thresholds_NO))
        button2.pack(pady=10)     
        
        label1=tk.Label(self,text="NOTE: Selecting NO may cause issues \nif video was not taken properly",font=LARGE_FONT)
        label1.pack(pady=10,padx=10)
        
        button3=tk.Button(self,text='PREVIOUS PAGE',command=lambda:controller.show_frame(StartPage))#controller,PageTwo))
        button3.pack(anchor=CENTER)

test_var=0
Queue_or_Done="Next"

ADAPTIVE_VAR=255
BINARY_VAR=140


def TestThreshold(label,controller,var_,var_2,label_keypoints):
    global test_var
    global threshold_values
    global ADAPTIVE_VAR
    global BINARY_VAR
    global Arena_circles
    
    videoname=glob.glob('*.MP4')[test_var]
    label.config(text=videoname)
    ADAPTIVE_VAR = var_.get()
    BINARY_VAR = var_2.get()
    print(ADAPTIVE_VAR,BINARY_VAR)
    print("i: "+str(test_var))
    videoname=glob.glob('*.MP4')[test_var]
    print(videoname)
    select_threshhold_func(videoname,ADAPTIVE_VAR,BINARY_VAR,label_keypoints)
    
    threshold_values["TOZERO_threshold_{0}".format(videoname)]=ADAPTIVE_VAR
    threshold_values["Binary_threshold_{0}".format(videoname)]=BINARY_VAR
    
    print("Adaptive threshold value for "+ videoname +" was set at a value of " + str(ADAPTIVE_VAR)+"\n")
    print("Binary threshold value for "+ videoname +" was set at a value of " + str(BINARY_VAR)  +"\n")
    
    
def Back_skip(button,label,controller,direction):
    global test_var
    global Queue_or_Done
    
    print("start"+str(test_var))
    test_var=test_var+direction
    print("mid"+str(test_var))
    if test_var<0:
       test_var=0
       print("No videos before this")
    if test_var ==len(glob.glob('*.MP4')):
        test_var=len(glob.glob('*.MP4'))-1
        controller.show_frame(Time_to_Run_Indiv_Thresh)
        
    videoname=glob.glob('*.MP4')[test_var]
    print(videoname)
    label.config(text=videoname+" (#"+str(test_var+1)+" of "+str(len(glob.glob('*.MP4')))+")")
    
    if test_var >=0 and test_var <=len(glob.glob('*.MP4'))-2:
        button.config(text="Next is "+str(glob.glob('*.MP4')[test_var+1])+" (#"+str(test_var+2)+" of "+str(len(glob.glob('*.MP4')))+")")
        
    if test_var==len(glob.glob('*.MP4'))-1:
        button.config(text="DONE")
            
    
    
    

def Back_skip_NO(button,label,controller,direction):
    global test_var
    global Queue_or_Done
    
    if test_var >=0 and test_var <len(glob.glob('*.MP4'))-1:
        test_var=test_var+direction
        label.config(text=str(glob.glob('*.MP4')[test_var])+" (#"+str(test_var+2)+" of "+str(len(glob.glob('*.MP4'))-1)+")")
        if test_var<0:
            test_var=0
            print("No videos before this")
        label.config(text=glob.glob('*.MP4')[test_var])
        button.config(text="Next is "+str(glob.glob('*.MP4')[test_var+1])+" (#"+str(test_var+2)+" of "+str(len(glob.glob('*.MP4'))-1)+")")
        
    if test_var>= len(glob.glob('*.MP4'))-2 and test_var<len(glob.glob('*.MP4'))-1:
        label.config(text=glob.glob('*.MP4')[test_var])
        button.config(text="DONE")
        
    elif test_var== len(glob.glob('*.MP4')):
        test_var=len(glob.glob('*.MP4'))
        controller.show_frame(Time_to_Run_Indiv_Thresh)
        
    videoname=glob.glob('*.MP4')[test_var]
    label.config(text=videoname)
    
def Next_thresh():
    print("in progress")
    

class Select_Thresholds_YES(tk.Frame):
    def __init__(self,parent,controller):
        
        global Queue_or_Done
        global test_var
        test_var=0
        #global general_threshold
        #videoname,self,parent,controller):
        
        tk.Frame.__init__(self,parent)
        
       # tk.Tk.wm_title(self,"Adaptive & Binary Threshold selection for ")#+videoname)
    
        label=tk.Label(self,text='\nVideofile name:')#+ videoname)
        label.pack()
        Label_6=glob.glob('*.MP4')[test_var]
        label6=tk.Label(self,text=Label_6)
        label6.pack()
        var=tk.DoubleVar()
        var.set(255)
        label2=tk.Label(self,text='ADAPTIVE THRESHOLDING')
        label2.pack()
        scale1=tk.Scale(self,from_=0,to=260,length=600,tickinterval=20,orient=HORIZONTAL,variable=var)
        scale1.pack()
        
        
        
        label3=tk.Label(self,text='Press "q" to close the images before selecting a new value or closing the windows.')
        label3.pack()
        
        label4=tk.Label(self,text= 'number of keypoints will appear HERE after closing images')
        label4.pack()
        
        button=tk.Button(self,text='Test Threshold',command=lambda:TestThreshold(label6,controller,var,var2,label4))#controller,PageTwo))
        button.pack(anchor=CENTER)
        
        label5=tk.Label(self,text='BINARY THRESHOLDING (Countours)')
        label5.pack()
        
        var2=tk.DoubleVar()
        var2.set(120)
        scale2=tk.Scale(self,from_=0,to=260,length=600,tickinterval=20,orient=HORIZONTAL,variable=var2)
        scale2.pack()
        
        button2=tk.Button(self,text=Queue_or_Done,command=lambda:Back_skip(button2,label6,controller,+1))#controller,PageTwo))
        button2.pack(anchor=CENTER)
        
        button1=tk.Button(self,text='Back',command=lambda:Back_skip(button2,label6,controller,-1))#controller,PageTwo))
        button1.pack(anchor=CENTER)
        
        
        button3=tk.Button(self,text='PREVIOUS PAGE',command=lambda:controller.show_frame(Threshold_Q))#controller,PageTwo))
        button3.pack(anchor="w")
        
class Select_Thresholds_NO(tk.Frame):
    def __init__(self,parent,controller):
        global Queue_or_Done
        #global general_threshold
        #videoname,self,parent,controller):
        global test_var

        test_var=0
        tk.Frame.__init__(self,parent)
        
       # tk.Tk.wm_title(self,"Adaptive & Binary Threshold selection for ")#+videoname)
    
        label=tk.Label(self,text='\nVideofile name:')#+ videoname)
        label.pack()
        
        Label_6=glob.glob('*.MP4')[test_var]
        label6=tk.Label(self,text=Label_6)
        label6.pack()
        
        label2=tk.Label(self,text='ADAPTIVE THRESHOLDING')
        label2.pack()
        
        var=tk.DoubleVar()
        var.set(255)
        
        scale1=tk.Scale(self,from_=0,to=260,length=600,tickinterval=20,orient=HORIZONTAL,variable=var)
        scale1.pack()
        
        
        
        label3=tk.Label(self,text='Press "q" to close the images before selecting a new value or closing the windows.')
        label3.pack()
        
        label4=tk.Label(self,text= 'number of keypoints will appear HERE after closing images')
        label4.pack()
        
        button=tk.Button(self,text='Test Threshold',command=lambda:TestThreshold(label6,controller,var,var2,label4))#controller,PageTwo))
        button.pack(anchor=CENTER)
        
        
        label5=tk.Label(self,text='BINARY THRESHOLDING (Countours)')
        label5.pack()
        
        var2=tk.DoubleVar()
        var2.set(120)
        
        scale2=tk.Scale(self,from_=0,to=260,length=600,tickinterval=20,orient=HORIZONTAL,variable=var2)
        scale2.pack()
        
        button1=tk.Button(self,text='DONE',command=lambda:controller.show_frame(Time_to_Run_One_Thresh))#controller,PageTwo))
        button1.pack(anchor=CENTER)
        
        button2=tk.Button(self,text='PREVIOUS PAGE',command=lambda:controller.show_frame(Threshold_Q))#controller,PageTwo))
        button2.pack(anchor="w")


class GRAPH_Page(tk.Frame):
    global Timefromframe_list
    global Data_array_perimeter
    global Distance_over_time_array
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text="Time to get some data!",font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        button1=tk.Button(self, text="Go Home", 
                          command=lambda: controller.show_frame(StartPage))
        button1.pack()
        
        button3=tk.Button(self, text="Output Contractions and overall distance",command=lambda:Output_Contractions_button())
        button3.pack()
        
        
        button2=tk.Button(self, text="Graph distance/time\n for each video\n(not recommended for many videos)",command=lambda:Graph_button())
        button2.pack()
        
   #     f=Figure(figsize=(5,5),dpi=100)
    #    a=f.add_subplot(111)
     #   canvas= FigureCanvasTkAgg(f,self)
        
        #for fname in glob.glob('*.MP4')[:1]:
   #     x_axis_perimeter=np.asarray(smoothTriangle(
    #            Data_array_perimeter['Perimeter_over_time'+ glob.glob('*.MP4')[test_var]],degree))
     #   a.plot([Timefromframe_list],[x_axis_perimeter])
      #  x_axis_distance=np.asarray(smoothTriangle(
       #         Distance_over_time_array['Distance_over_time'+ glob.glob('*.MP4')[test_var]],degree))
        #a.plot([Timefromframe_list],[x_axis_distance])
        
#        canvas.draw()
 #       canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH,expand=True)
        
  #      toolbar= NavigationToolbar2Tk(canvas,self)
   #     toolbar.update()
    #    canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH,expand=True)
        
def Graph_button():
    global Data_array_perimeter
    global Distance_over_time_array
    global Video_graphs
    global Num_of_Contractions
    degree=10
    for fname in glob.glob('*.MP4'):#[:1]:
        if str('Perimeter_over_time'+ fname) in Data_array_perimeter:
        #Get data for graphs
            x_axis_perimeter=np.asarray(smoothTriangle(Data_array_perimeter['Perimeter_over_time'+ fname],degree))
            peaksData_perimeter, _ = find_peaks(x_axis_perimeter, prominence=.101,distance=15,height=.185)
            x_axis_distance=np.asarray(smoothTriangle(Distance_over_time_array['Distance_over_time'+ fname],degree))
            peaksData_distance, _ = find_peaks(x_axis_distance,distance=15,prominence=.00098)#height=.002
            
            #Create figures
            Video_graphs["{0}".format(fname)],ax1=plt.subplots(figsize=(15,7)) #Make dictionary of all graphs
            fig=Video_graphs["{0}".format(fname)] #abbreviate for easier reading/usage
            #labels
            ax1.set_title('Distance and perimeter over time for video: '+fname+'\n', color='black')
     #       ax1.set_ylabel('Larva perimeter in cm',color='red')
            ax1.set_xlabel('Time',)
            #ax1.set_ylim(0.18,0.24)#7, 1.2)
            #plot data
       #     ax1.plot(peaksData_perimeter,x_axis_perimeter[peaksData_perimeter],'ob',color='darkorange')
            
            ax1.plot(Timefromframe_list,x_axis_perimeter,color='darkorange')
            #Change the number of ticks
         #   plt.xticks(np.arange(0, len(x_axis_perimeter)+(90-len(x_axis_perimeter)%90), 30.0,),rotation='vertical')
          #  plt.yticks(color='red')
            
            #ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
            
            ##########
            ax1.set_ylabel('Larva crawling distance in cm', color='blue')
            #ax2.set_ylim(0, .025)
            ax1.plot( peaksData_distance,x_axis_distance[peaksData_distance],'ob',color='deepskyblue')
            ax1.plot(Timefromframe_list,x_axis_distance)
            #plt.xticks(np.arange(0, len(x_axis_distance)+(90-len(x_axis_distance)%90), 30.0,),rotation='vertical',color='lavender')
            
            #plt.yticks(color='blue')
            ax1.tick_params(which='minor', width=2,grid_alpha=.5)#, direction='in')
            #ax2.grid(axis='x',color='black');
            #ax2.set_xlim(0,xaxis_limit)
            fig.tight_layout()
            #plt.show
            Num_of_Contractions_distance["{0}".format(fname)]=len(peaksData_distance)
            #plt.savefig(fname +'.png')
            ##########
        else:
            print("No data for "+str(fname))
    plt.show()



def Output_Contractions_button():
    global Data_array_perimeter
    global Distance_over_time_array
    global Video_graphs
    global Num_of_Contractions_distance
    global Num_of_Contractions_perimeter
    degree=10
    for fname in glob.glob('*.MP4'):
        if str('Perimeter_over_time'+ fname) in Data_array_perimeter:
        #Get data for graphs
           # x_axis_perimeter=np.asarray(smoothTriangle(Data_array_perimeter['Perimeter_over_time'+ fname],degree))
           # peaksData_perimeter, _ = find_peaks(x_axis_perimeter, prominence=.101,distance=15,height=.185)
            x_axis_distance=np.asarray(smoothTriangle(Distance_over_time_array['Distance_over_time'+ fname],degree))
            peaksData_distance, _ = find_peaks(x_axis_distance,distance=15,prominence=.00098)#height=.002
            
            #Num_of_Contractions_perimeter["{0}".format(fname)]=len(peaksData_perimeter)
            Num_of_Contractions_distance["{0}".format(fname)]=str(len(peaksData_distance))
            Total_Distance["Total_distance_for_{0}".format(fname)]=str(round(sum(Distance_over_time_array['Distance_over_time'+ fname]),2))
        else:
            print("No data for "+str(fname))
  #  print("Contractions calculated by Distance: "+ str(Num_of_Contractions_perimeter))
    print("Contractions calculated by Distance:\n"+ str(Num_of_Contractions_distance))
    print("Total Distances traveled(cm):\n"+ str(Total_Distance))

def One_thresh_at_a_time_func(controller):
    global ADAPTIVE_VAR
    global BINARY_VAR
    for fname in glob.glob('*.MP4')[:]:
        main(fname,displayY_N='Y',time_to_analyze=10)
        print("Feeeenal adaptive threshold value for "+ fname +" was set at a value of " + str(threshold_values["TOZERO_threshold_{0}".format(fname)])+"\n")
        print("Feeenal binary threshold value for "+ fname +" was set at a value of " + str(threshold_values["Binary_threshold_{0}".format(fname)])  +"\n")
    controller.show_frame(GRAPH_Page)
        #  print("Faaanal adaptive threshold value for "+ fname +" was set at a value of " + str(selection1)+"\n")
           # print("Faaanal binary threshold value for "+ fname +" was set at a value of " + str(selection2)  +"\n")


class Time_to_Run_Indiv_Thresh(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text="Done setting thresholds!\n\n\n Ready to run the code?! :-)",font=LARGE_FONT)
        label.pack(pady=10,padx=10)
    
        button1=tk.Button(self,text='RUN!',command=lambda:One_thresh_at_a_time_func(controller))#controller,PageTwo))
        button1.pack(anchor=CENTER)
        button1=tk.Button(self,text='PREVIOUS PAGE!',command=lambda:controller.show_frame(Select_Thresholds_YES))#controller,PageTwo))
        button1.pack(anchor="w") 
        #for fname in glob.glob('*.MP4')[:]:
            #print("Feeeenal adaptive threshold value for "+ fname +" was set at a value of " + str(selection1)+"\n")
            #print("Feeenal binary threshold value for "+ fname +" was set at a value of " + str(selection2)  +"\n")
        
        
def One_thresh_to_rule_them_all_func(controller):   
    global threshold_values
    global test_var
    global ADAPTIVE_VAR
    global BINARY_VAR
    global circles
    for video in glob.glob('*.MP4')[:]:
        #first_vidname=glob.glob('*.MP4')[test_var]
        
        #selection1=ADAPTIVE_VAR#threshold_values["TOZERO_threshold_{0}".format(first_vidname)]
        #selection2=BINARY_VAR#threshold_values["Binary_threshold_{0}".format(first_vidname)]
        threshold_values["TOZERO_threshold_{0}".format(video)]=ADAPTIVE_VAR
        threshold_values["Binary_threshold_{0}".format(video)]=BINARY_VAR
        Arena_circles["Arena{0}".format(video)]=circles
        main(video,displayY_N='Y',time_to_analyze=10)
    controller.show_frame(GRAPH_Page)


class Time_to_Run_One_Thresh(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text="Done setting thresholds!\n\n\n Ready to run the code?! :-)",font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1=tk.Button(self,text='RUN!',command=lambda:One_thresh_to_rule_them_all_func(controller))#controller,PageTwo))
        button1.pack(anchor=CENTER)      
        button1=tk.Button(self,text='PREVIOUS PAGE',command=lambda:controller.show_frame(Select_Thresholds_NO))#controller,PageTwo))
        button1.pack(anchor="w") 
        

def select_threshhold_func(videoname,ADAPTIVE_VAR,BINARY_VAR,label_keypoints):
    global Keypoint_X_Y
    global selection1
    global selection2
    global Expecting_area_values
    global Arena_circles
    global circles
    #global radius_expected_area
    
        
    VID_NAME_Iterate=videoname
    
    cap = cv2.VideoCapture(videoname,cv2.IMREAD_GRAYSCALE)
    cap.set(cv2.CAP_PROP_POS_FRAMES,160)
    
    kernel=np.ones((5,5),np.uint8) #size of matrix used for element-wise multiplication+summation of video data
    # Setup SimpleBlobDetector parameters. Detects blobs based on the following parameters
    params = cv2.SimpleBlobDetector_Params()
    
    #Parameters for color
    params.filterByColor = True
    params.blobColor=260
    # Change thresholds
    #params.minThreshold = ?
    #params.maxThreshold = ?
    
    
    # Parameters for Area.
    params.filterByArea = True
    params.minArea = 30
    params.maxArea = 200
    
    # Parameters for Circularity
    params.filterByCircularity = True
    params.minCircularity = 0.3 #<-- ?
    params.maxCircularity = 0.9 #<-- ?
    
    # Parameters for Convexity
    params.filterByConvexity = False
    params.minConvexity = 0#<-- ?
    
    # Parameters for Inertia
    params.filterByInertia = True
    params.minInertiaRatio = 0.01
    
    # Create a detector with the parameters
    detector = cv2.SimpleBlobDetector_create(params)
    selection1 = ADAPTIVE_VAR
    selection2 = BINARY_VAR

    
    while True:
        ret,frame=cap.read()    
        if ret:
            resized_frame=rescale_frame(frame,35)#35 #resizes frame
            grayscale_image=cv2.cvtColor(resized_frame,cv2.COLOR_BGR2GRAY) #grayscale
            Blur_frame=cv2.medianBlur(resized_frame,5)
            grayscale_image2=cv2.cvtColor(Blur_frame,cv2.COLOR_BGR2GRAY) #grayscale
            circles = cv2.HoughCircles(grayscale_image2,cv2.HOUGH_GRADIENT,1,200,param1=50,param2=130,minRadius=0,maxRadius=1000)
            if not np.any(circles):
                print("No Arena, ...I'll just try to draw one")
                Arena_bounding_box = cv2.selectROI("Select ARENA",grayscale_image2,False,True)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                if Arena_bounding_box[2]>Arena_bounding_box[3]:
                    Arena_radius_expected_area=Arena_bounding_box[2]/2
                    cv2.circle(grayscale_image2,(int(Arena_bounding_box[0]+Arena_radius_expected_area),int(Arena_bounding_box[1]+Arena_radius_expected_area)),int(Arena_radius_expected_area),(0,255,0),2)
                    circles=[[(int(Arena_bounding_box[0]+Arena_radius_expected_area),int(Arena_bounding_box[1]+Arena_radius_expected_area),int(Arena_radius_expected_area))]]
                    print("radius of expected area: "+str(Arena_radius_expected_area))
                else:
                    Arena_radius_expected_area=Arena_bounding_box[3]/2
                    cv2.circle(grayscale_image2,(int(Arena_bounding_box[0]+Arena_radius_expected_area),int(Arena_bounding_box[1]+Arena_radius_expected_area)),int(Arena_radius_expected_area),(0,255,0),2)
                    circles=[[(int(Arena_bounding_box[0]+Arena_radius_expected_area),int(Arena_bounding_box[1]+Arena_radius_expected_area),int(Arena_radius_expected_area))]]
                    print("radius of expected area: "+str(Arena_radius_expected_area))
                #circles=np.array([[[657.5,387.5,337.9]]])
            #elif np.any(circles):
             #   circles=circles
            circles = np.uint16(np.around(circles))
            
            print("Arena = "+ str(circles)+"\n")
            
            closed_morphology=cv2.morphologyEx(grayscale_image,cv2.MORPH_CLOSE,kernel) #closing morphology
            ret,TOZERO_threshold_image=cv2.threshold(closed_morphology,selection1,255,cv2.THRESH_TOZERO_INV) #makes binary
            ret,Binary_threshold_image=cv2.threshold(TOZERO_threshold_image,selection2,255,cv2.THRESH_BINARY) #makes binary
            
            
            object_keypoints = detector.detect(TOZERO_threshold_image)
            #print("object_keypoints = "+str(object_keypoints)+"\n")
            image_with_keypoints = cv2.drawKeypoints(TOZERO_threshold_image, object_keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS) #adds keypoints to video
            for i in circles[0,:]:
            #draw the outer circle
                cv2.circle(image_with_keypoints,(i[0],i[1]),int(i[2]-(i[2]*.08)),(0,255,0),2)
            Arena_circles["Arena{0}".format(VID_NAME_Iterate)]=circles
            keypoints=len(object_keypoints)
            print("# of keypoints: "+str(keypoints))
            if keypoints==1:
                for keyPoint in object_keypoints:
                   x = keyPoint.pt[0] #object_keypoints[0].pt[0]
                   y = keyPoint.pt[1] #object_keypoints[0].pt[1]
                   expected_bounding_circle_xyr=(int(x),int(y),20)
                print("(x,y): "+str(x)+str(y))
            if keypoints >=2:
                bounding_box = cv2.selectROI("Select Bounding box",image_with_keypoints,False,True)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                if bounding_box[2]>bounding_box[3]:
                    radius_expected_area=bounding_box[2]/2
                    cv2.circle(image_with_keypoints,(int(bounding_box[0]+radius_expected_area),int(bounding_box[1]+radius_expected_area)),int(radius_expected_area),(255,0,255),2)
                    expected_bounding_circle_xyr=(int(bounding_box[0]+radius_expected_area),int(bounding_box[1]+radius_expected_area),int(radius_expected_area))
                    print("radius of expected area: "+str(radius_expected_area))
                else:
                    radius_expected_area=bounding_box[3]/2
                    cv2.circle(image_with_keypoints,(int(bounding_box[0]+radius_expected_area),int(bounding_box[1]+radius_expected_area)),int(radius_expected_area),(255,0,255),2)
                    expected_bounding_circle_xyr=(int(bounding_box[0]+radius_expected_area),int(bounding_box[1]+radius_expected_area),int(radius_expected_area))
                    print("radius of expected area: "+str(radius_expected_area))
            if keypoints >=1:
                
                for keyPoint in object_keypoints:
                    x = keyPoint.pt[0] #object_keypoints[0].pt[0]
                    y = keyPoint.pt[1] #object_keypoints[0].pt[1]
                    s = keyPoint.size #object_keypoints[0].pt[2]
                    x_c=expected_bounding_circle_xyr[0]
                    y_c=expected_bounding_circle_xyr[1]
                    r_area=expected_bounding_circle_xyr[2]
                    d=((((x-x_c)**2)+((y-y_c)**2))**0.5)
                    if d<r_area:
                        cv2.circle(image_with_keypoints,(int(x),int(y)),int(r_area/2),(250,0,0),2)
                        Keypoint_X_Y["Keypoint{0}".format(VID_NAME_Iterate)]=[x,y,s]
                        
                        print("keypoint at "+str(x)+str(y)+"will be detected to be within" + str(x_c)+str(y_c))
                
                Expecting_area_values["Expecting_area_value_{0}".format(VID_NAME_Iterate)]=expected_bounding_circle_xyr
                

            Blur_frame=cv2.medianBlur(resized_frame,5)
            grayscale_image2=cv2.cvtColor(Blur_frame,cv2.COLOR_BGR2GRAY) #grayscale
            
            cv2.imshow('Binary_threshold_image',Binary_threshold_image)    
            cv2.imshow('TOZERO_threshold_image',image_with_keypoints)
            k=cv2.waitKey(0) & 0xff
            if k==ord('q'):
                break
        else:
            print("no video")
            break
    
    #cap.release()  ---Commenting this out allowed for windows to reopen after new selection
    cv2.destroyAllWindows()
    label_keypoints.config(text = str(keypoints) + ' keypoints detected')


def main(videoname,displayY_N='Y',time_to_analyze=10):
    cap = cv2.VideoCapture(videoname,cv2.IMREAD_GRAYSCALE)#('Practice_4_No_light_test_send.MP4',cv2.IMREAD_GRAYSCALE)
    cap.set(cv2.CAP_PROP_POS_FRAMES,300)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE,0.25)
    global perimeter_over_time_list
    global Timefromframe_list
    global Distance_over_time_list
    global Distance_over_time_array
    global Expecting_area_values
    global Seconds
    global rate
    global itworked
    global Data_array_perimeter
    global Distance_over_time_array
    global Arena_circles
    global Keypoint_X_Y

    itworked=TRUE
    rate=round(cap.get(cv2.CAP_PROP_FPS))
    print("video frame rate = " + str(rate))
    perimeter_over_time_list=[]
    Timefromframe_list=[]
    Distance_over_time_list=[]
    kernel=np.ones((5,5),np.uint8) #size of matrix used for element-wise multiplication+summation of video data
    # Setup SimpleBlobDetector parameters. Detects blobs based on the following parameters
    params = cv2.SimpleBlobDetector_Params()
    
    #Parameters for color
    params.filterByColor = True
    params.blobColor=255
    # Change thresholds
    #params.minThreshold = ?
    #params.maxThreshold = ?
    
    
    # Parameters for Area.
    params.filterByArea = True
    params.minArea = 50
    params.maxArea = 200
    
    # Parameters for Circularity
    params.filterByCircularity = True
    params.minCircularity = 0.3 #<-- ?
    params.maxCircularity = 0.9 #<-- ?
    
    # Parameters for Convexity
    params.filterByConvexity = False
    params.minConvexity = 0#<-- ?
    
    # Parameters for Inertia
    params.filterByInertia = True
    params.minInertiaRatio = 0.01
    
    # Create a detector with the parameters
    detector = cv2.SimpleBlobDetector_create(params)

    stop_at_frame_number=time_to_analyze*rate
    x_0=FALSE
    circles=Arena_circles["Arena{0}".format(videoname)]
    radi=circles[0,:][0][2]
    ShowDistance='Distance traveled is 0'

    while True:    
        ret,frame=cap.read()
        if ret:
            Frame=int(cap.get(cv2.CAP_PROP_POS_FRAMES)) #Frame number for Distance Traveled
            resized_frame=rescale_frame(frame,35)#35 #resizes frame
            grayscale_image=cv2.cvtColor(resized_frame,cv2.COLOR_BGR2GRAY) #grayscale
            #Blur_frame=cv2.medianBlur(resized_frame,5)
            closed_morphology=cv2.morphologyEx(grayscale_image,cv2.MORPH_CLOSE,kernel) #closing morphology
            ret,TOZERO_threshold_image=cv2.threshold(closed_morphology,int(threshold_values['TOZERO_threshold_'+ videoname]),255,cv2.THRESH_TOZERO_INV) #makes binary
            ret,Binary_threshold_image=cv2.threshold(closed_morphology,int(threshold_values['Binary_threshold_'+ videoname]),255,cv2.THRESH_BINARY) #makes binary
            
            #Finding Keypoints
            object_keypoints = detector.detect(TOZERO_threshold_image)
            image_with_keypoints = cv2.drawKeypoints(TOZERO_threshold_image, object_keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS) #adds keypoints to video
            keypoints=len(object_keypoints)
                    
            #retrieving coordinates and size of the blob detected, creating coordinates for cropped video
            if keypoints==1:
                for keyPoint in object_keypoints:
                   x = keyPoint.pt[0] #object_keypoints[0].pt[0]
                   y = keyPoint.pt[1] #object_keypoints[0].pt[1]
                   s = keyPoint.size #object_keypoints[0].pt[2]
                   expected_bounding_circle_xyr=(int(x),int(y),20)
                   cv2.circle(image_with_keypoints,(int(x),int(y)),20,(0,0,250),2)
                   r=Bounds_from_center(x,y)

                
            elif keypoints >1:
                for keyPoint in object_keypoints:
                    x_key = keyPoint.pt[0] #object_keypoints[0].pt[0]
                    y_key = keyPoint.pt[1] #object_keypoints[0].pt[1]
                    s_key = keyPoint.size #object_keypoints[0].pt[1]
                    if Frame == 1:
                        if not Expecting_area_values['Expecting_area_value_'+ videoname]:
                            print("More than one larvae detected but no expected are set up. Set threshold for this video separately")
                            itworked = False
                            break
                        x_c=Expecting_area_values['Expecting_area_value_'+ videoname][0]
                        y_c=Expecting_area_values['Expecting_area_value_'+ videoname][1]
                        r_area=Expecting_area_values['Expecting_area_value_'+ videoname][2]
                    elif Frame > 1 and not x_0:
                        x_c=Expecting_area_values['Expecting_area_value_'+ videoname][0]
                        y_c=Expecting_area_values['Expecting_area_value_'+ videoname][1]
                        r_area=Expecting_area_values['Expecting_area_value_'+ videoname][2]
                    elif Frame > 1 and x_0:
                        x_c=x_0 #Expecting_area_values['Expecting_area_value_'+ videoname][0]
                        y_c=y_0 #Expecting_area_values['Expecting_area_value_'+ videoname][1]
                        r_area= 20 #Expecting_area_values['Expecting_area_value_'+ videoname][2]
                    d=((((x_key-x_c)**2)+((y_key-y_c)**2))**0.5)
                    if d<r_area:
                        cv2.circle(image_with_keypoints,(int(x_key),int(y_key)),20,(250,0,0),2)
                        #print(str(x_key)+str(y_key)+"will be detected to be within" + str(x_c)+str(y_c))
                        x=x_key
                        y=y_key
                        s= s_key
                        r=Bounds_from_center(x,y)
                        expected_bounding_circle_xyr=(int(x),int(y),20)
                        
            
            # Crop image
            image_Cropped = Binary_threshold_image[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
            image_Cropped_Original = resized_frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
            
            #Contours (for finding the perimeter)
            #im2,contours,hierarchy=cv2.findContours(image_Cropped,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #finds contours on cropped image
            contours,hierarchy=cv2.findContours(image_Cropped,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            canvas = cv2.cvtColor(image_Cropped, cv2.COLOR_GRAY2BGR)                  #grayscales image
            #canvas_for_Skel=canvas                                          #Copy for skeletonizing
            cv2.drawContours(image_Cropped_Original,contours,-1,(0,0,250),1)#Draws contours on cropped image of original
            #cv2.drawContours(canvas_for_Skel,contours,-1,(0,0,250),0)       #Draws contours on cropped image of Skel
            canvasOG=rescale_frame(image_Cropped_Original,300)              #rescales frame
            canvas=rescale_frame(canvas,300)                                #rescales frame
            #canvas_for_Skel=rescale_frame(canvas_for_Skel,300)              #rescales frame
            cnt=contours[0]                                                 #?
            
            
            
          #  print("perimeter= "+str(perimeter))
            #First frame will set the starting distance at 0 and set the starting coordinates of the blob (maggot) 
            
            if Frame==1:
                x_0=x 
                y_0=y  #x and y will be used for the next frame
                Totaldistance=0
                Distance_over_time_list.append(Totaldistance)
                x_list=[x_0]
                y_list=[y_0] #x_list and y_list will be used to make the lines to mark the larvae's trail
                ShowDistance='Distance traveled is 0'
                #for the 2nd frame the distance will be calculated using the starting coordinates, and then each 
                #subsequent one will be calculated from the one before
                Blur_frame=cv2.medianBlur(resized_frame,5)
                grayscale_image2=cv2.cvtColor(Blur_frame,cv2.COLOR_BGR2GRAY) #grayscale
                circles = cv2.HoughCircles(grayscale_image2,cv2.HOUGH_GRADIENT,1,200,param1=50,param2=130,minRadius=0,maxRadius=1000)
                
                circles = np.uint16(np.around(circles))
                
                for i in circles[0,:]:
                    #draw the outer circle
                    cv2.circle(image_with_keypoints,(i[0],i[1]),int(i[2]-(i[2]*.08)),(0,255,0),2)
                   # cv2.circle(image_with_keypoints,(i[0],i[1]),i[2],(0,255,0),2)
                    # draw the center of the circle
                    cv2.circle(image_with_keypoints,(i[0],i[1]),2,(0,0,255),3)
                radi=circles[0,:][0][2]
                print("radius of circle = "+ str(radi))
            elif Frame > 1 and not x_0:
                print("no x_0")
                x_0=Keypoint_X_Y["Keypoint{0}".format(videoname)][0]
                y_0=Keypoint_X_Y["Keypoint{0}".format(videoname)][1]
                s=Keypoint_X_Y["Keypoint{0}".format(videoname)][2]
                x_list=[x_0]
                y_list=[y_0]
                Totaldistance=0
                Distance_over_time_list.append(Totaldistance)

            elif Frame > 1 and x_0:   #I think this is where the issue is. 'x' doesn't consistently exist. Path stops being tracked and extra circle stops too. Fix tomorrow!
                x_1=x
                y_1=y
                distance_pix=point_distance(x_0,y_0,x_1,y_1) #calculates distance from last frame to present
                distance=pixels_to_cm(distance_pix,radi)          #convertes the distance into cm
                #print(distance)
                Distance_over_time_list.append(distance)
                Totaldistance=Totaldistance+distance         #adds the distance from the two frames to the cumulative distance
                ShowDistance='Distance traveled is '+ str(round(Totaldistance,2)) + ' cm'   #Will be used to display the distance on the video display
                x_list.append(x_1)  
                y_list.append(y_1)  #x_list and y_list will be used to make the lines to mark the larvae's trail
                #below for loop will draw the lines of the trail on the image
                for i in range(1,len(x_list)):
                    a=x_list[int(i)-1]
                    b=y_list[int(i)-1]
                    c=x_list[int(i)]
                    d=y_list[int(i)]
                    #print(x_list)
                    drawlines(image_with_keypoints,int(a),int(b),int(c),int(d))
                    #global x_0
                    #global y_0
                    x_0=x_1
                    y_0=y_1
                for i in circles[0,:]:
                    #draw the outer circle
                    cv2.circle(image_with_keypoints,(i[0],i[1]),int(i[2]-(i[2]*.08)),(0,255,0),2)
                    #cv2.circle(image_with_keypoints,(i[0],i[1]),i[2],(0,255,0),2)
                    #draw the center of the circle
                    #cv2.circle(image_with_keypoints,(i[0],i[1]),2,(0,0,255),3)
            
                                                 #appends the perimeter length to a list to create a graph 
            
            #Coordinates and radius of detected circle
            x_circ=circles[0,:][0][0]
            y_circ=circles[0,:][0][1]
            radius_circ=int(circles[0,:][0][2])-(int(circles[0,:][0][2]))*.08
            
            d_arena=((((x-x_circ)**2)+((y-y_circ)**2))**0.5)
            if d_arena > radius_circ:
                if Frame ==1:
                    print("Need to setup expected area to ignore noise outside arena. Return to set threshold for this video separately")
                    itworked=False
                    break
                print("The larva has left the arena")
                break
            perimeter = pixels_to_cm(s,radi)#cv2.arcLength(cnt,True),radi)                             #?
            perimeter_over_time_list.append(perimeter)             
            #Labels on videos
            Time=millitomin(cap.get(cv2.CAP_PROP_POS_MSEC))
            Time_display_stamp='Time (min:sec): '+ str(Time)#millitomin(cap.get(cv2.CAP_PROP_POS_MSEC)) #Timestamp to be applied on video display
            Timefromframe_list.append(Time)
            Frame_display_stamp='Frame: ' + str(cap.get(cv2.CAP_PROP_POS_FRAMES)) #Frame label for Display
            font=cv2.FONT_HERSHEY_SIMPLEX
            Yes_list=('Yes','yes','YES','y','Y')
            if displayY_N in Yes_list:
                cv2.putText(image_with_keypoints,'Maggot.py in progress!',(0,50),font,.75,(200,255,255),2,cv2.LINE_AA)
                cv2.putText(image_with_keypoints,Time_display_stamp,(0,100),font,.5,(200,255,255),2,cv2.LINE_AA) #time elapsed label
                cv2.putText(image_with_keypoints,Frame_display_stamp,(0,150),font,.5,(200,255,255),2,cv2.LINE_AA) #Frames elapsed label
                cv2.putText(image_with_keypoints,ShowDistance,(0,200),font,.5,(200,255,255),2,cv2.LINE_AA) #Cumulative distance label
                cv2.putText(image_with_keypoints,videoname,(0,250),font,.5,(200,255,255),2,cv2.LINE_AA) #Cumulative distance label
                
                #cv2.imshow('TOZERO_threshold_image',TOZERO_threshold_image)
                #cv2.imshow('Binary_threshold_image',Binary_threshold_image)
                #cv2.imshow('Grayscale & closed',closed_morphology)
                cv2.imshow('Grayscale, closed_morphology, binarized, and tracked',image_with_keypoints) #displays the video
                #cv2.imshow('Color Threshold',TOZERO_threshold_image)
                
                cv2.imshow('Cropped original video, resized, with contours',canvasOG) #displays original video + Contours
                cv2.imshow("Contours on cropped, binarized, and resized image", canvas)
            #skeletonize(canvas_for_Skel)
            # Display cropped image
            #cv2.imshow("image", image_Cropped)
            Seconds=int(cap.get(cv2.CAP_PROP_POS_MSEC)/1000)
            if Frame==stop_at_frame_number:
                Timeup= str(time_to_analyze)+ " Second video analysis complete, duration: "+ str(Time_display_stamp)
                print(Timeup)
                cv2.imwrite(str(videoname)+"frame%d.png" %Frame, image_with_keypoints)   
                Data_array_perimeter["Perimeter_over_time{0}".format(videoname)]=np.asarray(perimeter_over_time_list)
                Distance_over_time_array["Distance_over_time{0}".format(videoname)]=np.asarray(Distance_over_time_list)         
                break

            k=cv2.waitKey(1) & 0xff
            if k==ord('p'):
                cv2.imwrite(str(videoname)+"frame%d.png" %Frame, image_with_keypoints)
                print('image taken at Frame #'+str(Frame))
            if k==ord('/'):
                print('Point of interest at Frame #'+str(Frame))
            if k==ord('q'):
                print("Video Terminated early, Q-command")
                Data_array_perimeter["Perimeter_over_time{0}".format(videoname)]=np.asarray(perimeter_over_time_list)
                Distance_over_time_array["Distance_over_time{0}".format(videoname)]=np.asarray(Distance_over_time_list)
                break
            if len(object_keypoints)==0:
                x_1=x_0
                y_1=y_0
                print(' No Larvae detected, FRAME SKIPPED')
                
                print(Frame_display_stamp)
                print(Time_display_stamp)
                cv2.imwrite(str(videoname)+"frame%d.png" %Frame, image_with_keypoints)
                Data_array_perimeter["Perimeter_over_time{0}".format(videoname)]=(1,0)
                Distance_over_time_array["Distance_over_time{0}".format(videoname)]=(1,0)
        else:
            Timeup="Video analysis complete, duration: "+ Time_display_stamp
            print(Timeup)
            cv2.imwrite(str(videoname)+"frame%d.png" %Frame, image_with_keypoints)
          #  Data_array_perimeter=np.asarray(perimeter_over_time_list)
           # Distance_over_time_array=np.asarray(Distance_over_time_list)   
            Data_array_perimeter["Perimeter_over_time{0}".format(videoname)]=np.asarray(perimeter_over_time_list)
            Distance_over_time_array["Distance_over_time{0}".format(videoname)]=np.asarray(Distance_over_time_list)         
            break
        
    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    if itworked:
        print(ShowDistance)
        #Total_Distance["Total_distance_for_{0}".format(videoname)]=str(round(Totaldistance,2)) + ' cm'
        print('Time (Min:sec:millisec)'+Time)





app=GUI_Behavior()
app.mainloop()
#%%
#File_1
first_export= open("Number_of_Contractions_read.txt","w+")
first_export.write("Number of Contractions"+"\r\n")
for vidname in glob.glob('*.MP4'):
    if str(vidname) in Num_of_Contractions_distance:
        first_export.write(vidname+' '+str(Num_of_Contractions_distance[vidname])+"\r\n")
    else:
        first_export.write("No data available for"+vidname+"\r\n")
first_export.close()       

#File_2
second_export= open("Number_of_Contractions_just_numbers.txt","w+")
second_export.write("Number of Contractions"+"\r\n")
for vidname in glob.glob('*.MP4'):
    if str(vidname) in Num_of_Contractions_distance:
        second_export.write(Num_of_Contractions_distance[vidname]+"\r\n")
    else:
        second_export.write("No data available for"+vidname+"\r\n")
second_export.close()  

#File_3
third_export=open("Distances_read.txt", "w+")
third_export.write("Total Distance traveled in each video"+"\r\n")
for vidname2 in glob.glob('*.MP4'):
    if str('Total_distance_for_'+vidname2) in Total_Distance:
        third_export.write(vidname2+' '+str(Total_Distance['Total_distance_for_'+vidname2]) +"\r\n")
    else:
        third_export.write("No data available for"+vidname2+"\r\n")
third_export.close()

#File_4
fourth_export=open("Distances_read_just_numbers.txt", "w+")
fourth_export.write("Total Distance traveled in each video"+"\r\n")
for vidname2 in glob.glob('*.MP4'):
    if str('Total_distance_for_'+vidname2) in Total_Distance:
        fourth_export.write(Total_Distance['Total_distance_for_'+vidname2]+"\r\n")
    else:
        fourth_export.write("No data available for"+vidname2+"\r\n")
fourth_export.close()

#Create new folder
New_Folder_Name="Data_folder"
os.mkdir(New_Folder_Name)
#Move files to new folder
exports=['Number_of_Contractions_read.txt','Number_of_Contractions_just_numbers.txt',
          'Distances_read.txt','Distances_read_just_numbers.txt']
for i in exports:
    shutil.move(i, New_Folder_Name)





# %%


# %%
