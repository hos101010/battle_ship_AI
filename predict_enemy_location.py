import numpy as np
import sys
import math
import argparse
from math import cos, sin, sqrt, atan2
from numpy import array, dot
from numpy.linalg import pinv

"""class EKF(object):

    def __init__(self):
        self.init_data(queue)

    def run_EKF(self):
        for i in range(100):"""

def sumMatrix(A,B):
    answer=[]
    for i in range(len(A)):
        answer.append(A[i]+B[i])
    return answer

class Queue(list):
    def __init__(self):
        self.Queue_item=[]
    def Enqueue(self,x):
        self.append(x)
        return None
    def Dequeue(self):
        item_length=len(self.Queue_item)
        if item_length<1:
            print ("error")
            return False
        #result=self.Queue_item[0]
        del self.Queue_item[0]
        #return result

def ekf_predict(xp,P,dt):
    
    h=xp[2]
    v=xp[3]
    w=xp[4]
    r=v/w
    
    sinh = sin(h)
    sinhwdt = sin(h + w*dt)
    cosh = cos(h)
    coshwdt = cos(h + w*dt)

    G = array(
       [[1, 0, -r*cosh + r*coshwdt],
        [0, 1, -r*sinh + r*sinhwdt],
        [0, 0, 1]])

    V = array(
        [[(-sinh + sinhwdt)/w, v*(sin(h)-sinhwdt)/(w**2) + v*coshwdt*dt/w],
         [(cosh - coshwdt)/w, -v*(cosh-coshwdt)/(w**2) + v*sinhwdt*dt/w],
         [0, dt]])


    # covariance of motion noise in control space
    M = array([[0.001*v**2 + 0.001*w**2, 0],
               [0, 0.001*v**2 + 0.001*w**2]])


    xp = sumMatrix(xp,[r*cosh - r*coshwdt,-r*sinh + r*sinhwdt,w*dt,0,0])
    P = dot(G, P).dot(G.T) + dot(V, M).dot(V.T)

    return xp, P

    
def main():
    
    data_queue=Queue()
    data_queue.Enqueue([10,22,math.pi/8.0,3,0.1])
    data_queue.Enqueue([15,32,math.pi/8.0,4,0.1])
    data_queue.Enqueue([15,12,math.pi/8.0,5,0.1])
    data_queue.Enqueue([17,40,math.pi/8.0,6,0.1])
    data_queue.Enqueue([42,33,math.pi/8.0,7,0.1])

    dt=0.1
    P = np.diag([1., 1., 1.])
    
    for i in range(5):
        xp=data_queue[i]
        print xp
        for j in range(10):
            xp,P=ekf_predict(xp,P,dt)
        print xp

if __name__ == "__main__":
    main()

