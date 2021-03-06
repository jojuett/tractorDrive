# file tractor.py
# author: Andrew Reisner <andrew@reisner.co>
# This class makes it easy to interact with the 
# bullet vehicle physics
import bge
from math import acos
import mathutils
from time import time

class Vehicle(bge.types.KX_GameObject):
    
    def __init__(self,old_owner):
        self.active = False
                
        self.stuckCount = 0
        self.vel = []

    def setup(self,settings):
        
        self.settings = settings
        self.startTime = time()
        
        self.initPhysics()
        
        self.initTires()
        
        self.addTires()
        
        self.initSusp()
        
    def initSusp(self):
        settings = self.settings
        for i in range(4):
            self.vid.setTyreFriction(settings.TIRE_GRIP[i],i)
            self.vid.setSuspensionCompression(settings.TIRE_SUSP['compression'][i],i)
            self.vid.setSuspensionDamping(settings.TIRE_SUSP['damping'][i],i)
            self.vid.setSuspensionStiffness(settings.TIRE_SUSP['stiffness'][i],i)
            self.vid.setRollInfluence(settings.ROLL_INFLUENCE[i],i)
        
    def initPhysics(self):
        phid = self.getPhysicsId()
        constraint = bge.constraints.createConstraint(phid,0,11)
        cid = constraint.getConstraintId()
        self.vid = bge.constraints.getVehicleConstraint(cid)
        self['vehicleID'] = self.vid
        
    def initTires(self):
        settings = self.settings
        scene = bge.logic.getCurrentScene()
        objs = scene.objects
        self.tires = (objs[settings.TIRE_OBJS[0]],
                      objs[settings.TIRE_OBJS[1]],
                      objs[settings.TIRE_OBJS[2]],
                      objs[settings.TIRE_OBJS[3]])

    def addTires(self):
        settings = self.settings
        for i in range(4):
            self.vid.addWheel(self.tires[i],
                              settings.TIRE_POS[i],
                              settings.TIRE_SUSP['angle'][i],
                              settings.TIRE_AXIS[i],
                              settings.TIRE_SUSP['height'][i],
                              settings.TIRE_RADIUS[i],
                              settings.TIRE_STEER[i])
    
    def setPower(self,power):
        for i in range(4):
            self.vid.applyEngineForce(power,i)
            
    def getSpeed(self):
        return -1*self.getLinearVelocity(True)[1]
            
    def forward(self):
        self.setPower(self.settings.FORWARD_POWER)
    
    def backward(self):
        self.setPower(-1*self.settings.BACKWARD_POWER)
        
    def steer(self,value):
        #print("Steer:",value)
        settings = self.settings
        for i in range(4):
            if (settings.TIRE_STEER[i]):
                self.vid.setSteeringValue(value,i)
                
    def timedOut(self):
        if time() - self.startTime > self.settings.TIMEOUT:
            return True
        else:
            return False
        
    def flipped(self):
        '''
        returns true if we detect that the tractor
        flipped beyond a given threshold and false
        otherwise
        '''
        # get angle between global and local z value
        val = self.getAxisVect((0,0,1)) 
        cos_val = val[2]/(val[0]**2 + val[1]**2 + val[2]**2)**(.5)
        theta = acos(cos_val)
        if theta > self.settings.FLIP_THRESH:
            return True
        else:
            return False
        
    def stuck(self):
        '''
        returns true if we detect hat the tractor
        is stuck on an object. 
        '''
        if self.active:
            resolution = 300
            threshold = .5
            if (self.stuckCount == resolution):
                average = sum(self.vel)/len(self.vel)
                if (average) < threshold:
                    return True
                self.stuckCount = 0
                self.vel = []
            else:
                self.stuckCount += 1
                self.vel.append(self.getLinearVelocity().magnitude)
            return False
        else:
            return False


def power(cont):
    trac = cont.owner
    
    gas = cont.sensors['gas']
    reverse = cont.sensors['reverse']
    
    if gas.positive:
        trac.forward()
    elif reverse.positive:
        trac.backward()
    else:
        trac.setPower(0)
        
def steering(cont):
    trac = cont.owner

    turn = 0.3
    
    steerLeft = cont.sensors['left']
    steerRight = cont.sensors['right']
    if steerLeft.positive:
        turn = turn
    elif steerRight.positive:
        turn = -turn
    else:
        turn = 0.0

    trac.steer(turn)