import RPi.GPIO as GPIO
import time

class ULN2003():
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    #defining how long to wait between steps:
    motor_latency=0.005
    
    def __init__(self, pins, latency=motor_latency, half_step=True):
        self.pins=pins
        self.latency=latency
        if half_step:
            #half-step (step in cycle, pin output)
            self.sequence=[[1,0,0,0],
                           [1,1,0,0],
                           [0,1,0,0],
                           [0,1,1,0],
                           [0,0,1,0],
                           [0,0,1,1],
                           [0,0,0,1],
                           [1,0,0,1]]
        else:
            #full-step (step in cycle, pin output)
            self.sequence=[[1,1,0,0],
                          [0,1,1,0],
                          [0,0,1,1],
                          [1,0,0,1]]
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for p in range(len(self.pins)):
            GPIO.setup(self.pins[p],GPIO.OUT)
        
    def read_pins(self):
        config=[]
        for p in range(len(self.pins)):
            config.append(GPIO.input(self.pins[p]))
        return config
        
    def cycle(self,sequence):
        for i in range(len(sequence)):
            for p in range(len(self.pins)):
                GPIO.output(self.pins[p],sequence[i][p])
            time.sleep(self.latency)
        return None
    
    def step(self,n=1):
        sequence=self.sequence
        
        sign=n/abs(n)
        if sign<0:
            sequence=sequence[::-1]
        n=abs(n)
        
        config=self.read_pins() #determining where in the cycle we currently are
        cycle_index=len(sequence)-1 #initialising the cycle index
        
        for i in range(len(sequence)):
            if config==sequence[i]:
                cycle_index=i
                
        n_before=max(0, min(n, len(sequence) - cycle_index - 1)) #number of steps still required to be at the begning of the next cycles (clipped to be less than n)
        n_after=(n - n_before)%len(sequence) #the number of steps that will occur after the full cycles are executed
        n_cycles=(n-n_before-n_after)//len(sequence) #the number of full cycles stepping by n will encompass
        
        for j in range(n_before):
            for p in range(len(self.pins)):
                GPIO.output(self.pins[p],sequence[cycle_index+j+1][p])
            time.sleep(self.latency)
            
        for k in range(n_cycles):
            self.cycle(sequence)
            
        for l in range(n_after):
            for p in range(len(self.pins)):
                GPIO.output(self.pins[p],sequence[l][p])
            time.sleep(self.latency)
            
        return None