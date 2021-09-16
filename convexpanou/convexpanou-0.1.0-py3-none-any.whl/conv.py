#!/usr/bin/env python
# coding: utf-8

# In[8]:



import matplotlib.pyplot as plt
import numpy as np
import seaborn; seaborn.set()
from panouconv.conv2 import acnhorpoint
from panouconv.conv2 import polar_angle
from panouconv.conv2 import _sorted
from panouconv.conv2 import ccw



#Convex_Hull_Graham#

class convex_hull_graham:
    def __init__(self, datapoints):
        self.datapoints = datapoints
        
    def convex_hull_graham_for_the_plot(self): 
        #this function returns all the points of the convex _hull and it includes the anchorpoint twice. It will be used in the following function plt_graham_convex of the current method in order to plot the convex _hull
        
        anchor_point=acnhorpoint(self.datapoints)
        sorted_datapoints=_sorted(self.datapoints)
        convex_hull = [anchor_point, sorted_datapoints[0]]
        for point in sorted_datapoints[1:]:
            while ccw(convex_hull[-2],convex_hull[-1], point)<=0:
                if len(convex_hull)>2:
                    del convex_hull[-1] # backtrack
                else:
                    break
            if ccw(convex_hull[-2],convex_hull[-1], point)>0:
                convex_hull.append(point)
            elif ccw(convex_hull[-2],convex_hull[-1], point)==0: 
                # if the three points form a straight line, then we erase the second one  #from the on going convex_hull and we add the third one as a point, since it is more far away than the first point
                del convex_hull[-1]
                convex_hull.append(point) 
                
        if convex_hull[1][1]==convex_hull[0][1]:
            # this loop secures that if two or more datasets' points y-value equals = anchorpoint [1], then the first point of the convex hull returned will be anchorpoint and the second one will be the one with the maximum x-value of all  other points with y-value equals = anchorpoint[1]
            sorted_datapoints=np.sort(sorted_datapoints,axis=1)
            i=0
            m=sorted_datapoints[i][1]
            while sorted_datapoints[i][0]==anchor_point[1]:
                i+=1
                m=max(m,sorted_datapoints[i-1][1])
            convex_hull[1][0]=m
            
            while ccw(convex_hull[1],convex_hull[2], convex_hull[3])<=0:
                del convex_hull[2]
        return convex_hull
    
    def convex_hull_from_points(self): 
        #function that returns the set of 2-d points which form the convex hull polygon enclosing all the points of the original 2-d set provided as input
        if len(self.datapoints)<3:
            return self.datapoints
        else:
            convex_hull=self.convex_hull_graham_for_the_plot()
            convex_hull.pop()
            return convex_hull
    
    def plt_graham_convex(self): 
        # function thath plots the whole set of 2-d points provided as input in the method, and forms the convex_hull_polygon that surrounds them
        if len(self.datapoints)<3:
             plt.scatter(self.datapoints[:,0], self.datapoints[:,1])
           
        else:
            
            convex_hull=self.convex_hull_graham_for_the_plot()
            plt.scatter(self.datapoints[:,0], self.datapoints[:,1])
            plt.plot(np.array(convex_hull)[:,0], np.array(convex_hull)[:,1], '-ok')
        

    def point_is_in_polygon(self,point): #function that returns True or False whether a 2-d point lies into a provided convex_hull_polygon
        
        r=np.array(self.datapoints+list(point))
        d=convex_hull_graham(r).convex_hull_from_points()

        y=True
        
        for i in range (len(d)):
            if np.alltrue(np.equal(point[0],d[i])): 
           
                y=False
            
                return y
                break
            else:
                pass
        if y:
            return y
        
    def plt_in_or_out(self,point): #plots the convex_hull_polygon provided as input of  the method as wel as the point provided as input in the function. So we visualise whether the point is in or out the polygon
        
        d=self.datapoints
        d.append(self.datapoints[0])
        plt.scatter(np.array(d)[:,0], np.array(d)[:,1])
        plt.plot(np.array(d)[:,0], np.array(d)[:,1], '-ok')
        plt.scatter(point[0][0],point[0][1],c='r')
        del d[-1]
    
    def do_interesect(self,conv2): #function that returns True or False whether two convex_hull_polygons provided as input (the first one in the method and the second one in the current function) do intersect
        y=False
        d=self.datapoints
        
        for i in range (len(conv2)): #case point(s) of convex hull conv 2 are into convex hull datapoints 
            d.append(conv2[i])
            v=convex_hull_graham(d).convex_hull_from_points()
            del d[-1]
            z=0
            for j in range (len(v)):
                if np.alltrue(np.equal(conv2[i],v[j])):
                     break
                else:
                    z+=1
            if z==len(v):
                y=True
                return y
                break
        
        if not y:   #case point(s) of convex hull datapoints  are into convex hull conv 2
            for i in range (len(d)):
                conv2.append(d[i])
                r=convex_hull_graham(conv2).convex_hull_from_points()
                del conv2[-1]
                z=0
                for j in range (len(r)):  
                    if np.alltrue(np.equal(d[i],r[j])):
                         break
                    else:
                         z+=1     
                if z==len(r):
                    y=True
                    return y
                    break
                    
        if not y: #case of interesection but none of the points of each convex hull polygon is into the other polygon
            r=convex_hull_graham(conv2+d).convex_hull_from_points()
            e=[]
            for i in range (len(r)):
                for j in range (len (d)):
                    z=0
                    if np.alltrue(np.equal(r[i],d[j])): 
                    
                        e.append(1)
                        z=1
                        break
                    else:
                        pass
                if z==0:
                    e.append(z)   
            r=0
            for i in range (len(e)-1):
                if e[i]!=e[i+1]:
                    r+=1
                    if r>2:
                        y=True
                        return y
                        break
        if not y:
            return y
            
    def plt_in_or_out_conv(self,conv2): #plots both convex hull polygons provided as input (the first one in the method and the second one in the current function) in order to visualize possible intersection
        
        d=self.datapoints
        d.append(self.datapoints[0])
        r=conv2
        r.append(conv2[0])
        plt.scatter(np.array(d)[:,0], np.array(d)[:,1])
        plt.scatter(np.array(r)[:,0], np.array(r)[:,1])
        plt.plot(np.array(d)[:,0], np.array(d)[:,1], '-ok')
        plt.plot(np.array(r)[:,0], np.array(r)[:,1], '-or')
        del conv2[-1]
        del d[-1]





