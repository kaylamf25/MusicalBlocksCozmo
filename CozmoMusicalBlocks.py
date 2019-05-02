import cozmo
import socket
import errno
import time
import random
import pygame
from socket import error as socket_error
import asyncio
import collections
import math
import warnings
from cozmo.util import degrees, distance_mm, speed_mmps

def cozmo_program(robot: cozmo.robot.Robot):
    #connect to network
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket_error as msg:
        robot.say_text("socket failed" + msg).wait_for_completed()
    ip = "10.0.1.10"
    port = 5000
    try:
        s.connect((ip, port))
        robot.say_text("Ready").wait_for_completed()
    except socket_error as msg:
        robot.say_text("socket failed to bind").wait_for_completed()
    cont = True
    
    #set the global variables
    readyIsDone = False
    hasBlock = False
    listenNotDone = True;
    
    #set cozmo to the standard position
    robot.set_lift_height(0).wait_for_completed()
    robot.set_head_angle(degrees(0)).wait_for_completed()
    
    #check for ready
    bytedata = s.recv(4048)
    data = bytedata.decode('utf-8')
    print(str(data))   
    if not data:
        cont = False
        s.close()
        quit()
    else:
        instructions = data.split(';')    
        if ((instructions[0] == "Ready?") and (not readyIsDone)):
            s.sendall(b'Ready') 
            readyIsDone = True            
    
    #game loop constantly listening
    while cont:
        #listening
        bytedata = s.recv(4048)
        data = bytedata.decode('utf-8')
        print(str(data))   
        if not data:
            cont = False
            s.close()
            quit()
        else:        
            #parse message if data
            instructions = data.split(';')
                    
            #elif Music start
            if instructions[0] == "Music":
                listenNotDone = True
                bytedata = s.recv(4048)
                data = bytedata.decode('utf-8')
                print(str(data))   
                instructions = data.split(';')
                temp = int(instructions[0])
                temp = temp*300             #dances by spinning
                robot.turn_in_place(degrees(temp)).wait_for_completed()  
                   

            #elif Look for a block if one hasn't already been found
            elif instructions[0] == "Look" and not hasBlock:
                cubes = None
                lookaround = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
                cubes = robot.world.wait_until_observe_num_objects(num=1, object_type=cozmo.objects.LightCube, timeout=20)
                lookaround.stop()
                if (not(len(cubes) ==0)): #if there is a cube try to pick it up
                    current_action = robot.pickup_object(cubes[0], num_retries=1)
                    current_action.wait_for_completed()
                    if current_action.has_failed: #block not found
                        code, reason = current_action.failure_reason
                        result = current_action.result
                        print("Pickup Cube failed: code=%s reason='%s' result=%s" % (code, reason, result))
                        s.sendall(b'NotFound')
                    else: #block found
                        s.sendall(b'BlockFound')    
                        hasBlock = True 
                else: #no cubes were seen
                    s.sendall(b'NotFound')

            #elif game over with or without a block (last round)
            elif instructions[0] == "GameOver":
                if(hasBlock == True):
                    robot.set_lift_height(0).wait_for_completed()
                    robot.set_head_angle(degrees(0)).wait_for_completed()
                    robot.drive_straight(cozmo.util.distance_mm(-100), cozmo.util.speed_mmps(100)).wait_for_completed()                            
                    robot.play_anim('anim_keepaway_wingame_02').wait_for_completed()                        
                    robot.say_text("Winner").wait_for_completed()
                    hasBlock = False;
                    return
                else:
                    robot.set_lift_height(0).wait_for_completed()  
                    robot.set_head_angle(degrees(0)).wait_for_completed()
                    robot.play_anim('anim_keepaway_losegame_02').wait_for_completed()
                    name = "Out"
                    return       
            #elif round over with or without a block
            elif instructions[0] == "RoundOver":
                if(hasBlock == True):
                    robot.set_lift_height(0).wait_for_completed()
                    robot.set_head_angle(degrees(0)).wait_for_completed()
                    robot.drive_straight(cozmo.util.distance_mm(-100), cozmo.util.speed_mmps(100)).wait_for_completed()                            
                    robot.play_anim('anim_keepaway_wingame_02').wait_for_completed()
                    hasBlock = False
                else:
                    robot.set_lift_height(0).wait_for_completed() 
                    robot.set_head_angle(degrees(0)).wait_for_completed()
                    robot.play_anim('anim_keepaway_losegame_02').wait_for_completed()
                    name = "Out"
                    return    
                
            #A way to make sure they're all listening for commands before sending them
            elif instructions[0] == "Listening?" and listenNotDone:
                s.sendall(b"Listening")
                listenNotDone = False;
                
cozmo.run_program(cozmo_program)
