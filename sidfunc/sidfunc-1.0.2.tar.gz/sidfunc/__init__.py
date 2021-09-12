import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.image as im
from PIL import Image, ImageFont, ImageDraw
import scipy.stats as stats
sns.set_color_codes(palette='deep')

def plotmultiple(colnames,df,fz,plttype,orient='h',hue=None):
    """
    colnames= list of name of columns of dataframe you want plot for eg. ['sex','region']
    df=pd.DataFrame object
    fz=tuple of size of figure eg. (10,20) 
    plttype=type of plot required eg. 'count','box','swarm','hist'
    in case other than given plottype passed, boxplot will be plotted.
    orient='v'or'h'
    hue=categorical variable by which plot should be categorised eg. hue='sex'
    """
    plt.ioff()
    n=len(colnames)
    b=int(n/2)
    c=1
    plt.figure(figsize=fz)
    for i in colnames:
        plt.subplot(n,b,c)
        if(plttype=='count'):
            if(hue!=None):
                sns.countplot(df[hue],df[i],orient=orient)
            else:
                sns.countplot(df[i],orient=orient)
        elif(plttype=='box'):
            if(hue!=None):
                sns.boxplot(df[hue],df[i],orient=orient)
            else:
                sns.boxplot(df[i],orient=orient)
        elif(plttype=='swarm'):
            if(hue!=None):
                sns.swarmplot(df[hue],df[i],orient=orient)
            else:
                sns.swarmplot(df[i],orient=orient)
        elif(plttype=='hist'):
            if(hue!=None):
                sns.distplot(df[hue],df[i])
            else:
                sns.distplot(df[i])
        else:
            sns.boxplot(df[i],orient=orient)
        c=c+1
    plt.tight_layout()
    plt.show()

def draw_text(text,size,textcolor='b',bkc=(255, 255, 255),bksize=(500,50)):
    '''
    text = string = Text to draw
    size = int = font size of text to draw
    textcolor : 'r','g','b','y'
    bkc : (255,255,255) takes RGB value
    bksize : length X width of figure
    '''
    img = Image.new('RGB', bksize, color = bkc)
    font = ImageFont.truetype("arial",size)
    d = ImageDraw.Draw(img)
    c=(0,0,0)
    if(textcolor=='r'):
            c=(255,0,0)
    elif(textcolor=='g'):
            c=(0,128,0)
    elif(textcolor=='b'):
            c=(0,0,255)
    elif(textcolor=='y'):
            c=(255,255,0)
    d.text((10,10), text,font=font,fill=c)
    plt.imshow(img)
    plt.axis(False)
    plt.show()