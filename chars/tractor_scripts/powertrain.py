import bge

def power(cont):
    trac = cont.owner['handle']
    
    gas = cont.sensors['gas']
    reverse = cont.sensors['reverse']
    
    if gas.positive:
        trac.forward()
    elif reverse.positive:
        trac.backward()
    else:
        trac.setPower(0)
        
def steering(cont):
    car = cont.owner

    turn = 0.3
    
    steerLeft = cont.sensors['left']
    steerRight = cont.sensors['right']
    if steerLeft.positive:
        turn = turn
    elif steerRight.positive:
        turn = -turn
    else:
        turn = 0.0

    trac = car['handle']
    trac.steer(turn)