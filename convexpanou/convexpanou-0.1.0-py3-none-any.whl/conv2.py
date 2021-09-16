from math import atan2
import numpy as np

def acnhorpoint(datapoints):
#finds the point of a 2-d array with the lowest value of y. If min (y) is the same in two or more points, it returns the points among them #with the lowest value of x'''
    anchor_point = datapoints[0]
    for i in range(1,len(datapoints)):
        if datapoints[i][1] < anchor_point[1]:
            anchor_point = datapoints[i]
        elif datapoints[i][1] == anchor_point[1] and datapoints[i][0] < anchor_point[0]:
            anchor_point = datapoints[i]
    return (anchor_point)

def polar_angle(p0, p1):
#calculates the angle between p0 and p1 in radius. The angle is between -pi and pi radius
    y_span=p0[1]-p1[1]
    x_span=p0[0]-p1[0]
    return atan2(y_span,x_span) 


def _sorted(datapoints):
    #sorts the points of a 2-d array by polar angle
    anchor_point=acnhorpoint(datapoints)
    datapoints_angles = []
    origin = [0,0]
    for _, point in enumerate(datapoints):
        datapoints_angles.append([point[0],point[1], polar_angle(anchor_point, point)]) #creates a list of (number of datapoints) elements each of is a list of 3 numbers. The value of x of the point, the value of y and the polar angle between the point and the anchorpoint of the datapoints

    datapoints_angles = np.array(datapoints_angles)    
    datapoints_angles = datapoints_angles[datapoints_angles[:,2].argsort()] # the array is sorted by the polar angle of each point with the anchorpoint
    while datapoints_angles[len(datapoints_angles)-1][2]!=0: #we implement the code on every point but the anchor point
        datapoints_angles=np.roll(datapoints_angles,3)

    return datapoints_angles[:,(0,1)] #  The function solely just the points sorted by polar angle

def ccw(a, b, c):
#calculates the counter - clock wiseness between 3 2-d points (a,b,c). If ccw >0 then the path a-b-c is counterclockwise. If it is 0 then it is  a straight line
    return (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
