#connect to network
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
    
    readyIsDone = False
    hasBlock = False
    
    robot.set_lift_height(0).wait_for_completed()
    robot.set_head_angle(degrees(0)).wait_for_completed()
    

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
    
    
    while cont:
        bytedata = s.recv(4048)
        data = bytedata.decode('utf-8')
        print(str(data))   
        if not data:
            cont = False
            s.close()
            quit()
        else:        
            #parse message
            instructions = data.split(';')
            #if Ready to play
            if ((instructions[0] == "Ready?") and (not readyIsDone)):
                s.sendall(b'Ready') 
                readyIsDone = True         
            #elif Music start
            elif instructions[0] == "Music":
                #do dance for length

            #elif Look for a block
            elif instructions[0] == "Look" and not hasBlock:
                #look for a block
                cubes = None
                lookaround = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
                cubes = robot.world.wait_until_observe_num_objects(num=1, object_type=cozmo.objects.LightCube, timeout=10)
                lookaround.stop()
                if (not(cubes == None)) or len(cubes) ==0:
                    current_action = robot.pickup_object(cubes[0], num_retries=4)
                    current_action.wait_for_completed()
                    if current_action.has_failed:
                        code, reason = current_action.failure_reason
                        result = current_action.result
                        print("Pickup Cube failed: code=%s reason='%s' result=%s" % (code, reason, result))
                        s.sendall(b'NotFound')
                    else:
                        s.sendall(b'BlockFound')    
                        hasBlock = True 
                else:
                    s.sendall(b'NotFound')

            #elif game over with or without a block
            elif instructions[0] == "GameOver":
                if(hasBlock == True):
                    robot.set_lift_height(0).wait_for_completed()
                    robot.drive_straight(cozmo.util.distance_mm(-100), cozmo.util.speed_mmps(100)).wait_for_completed()                            
                    robot.play_anim('anim_keepaway_wingame_02').wait_for_completed()                        
                    robot.say_text("Winner").wait_for_completed()
                    hasBlock = False;
                    return
                else:
                    robot.set_lift_height(0).wait_for_completed()                            
                    robot.play_anim('anim_keepaway_losegame_02').wait_for_completed()
                    name = "Out"
                    return                
            elif instructions[0] == "RoundOver":
                if(hasBlock == True):
                    robot.set_lift_height(0).wait_for_completed()
                    robot.drive_straight(cozmo.util.distance_mm(-100), cozmo.util.speed_mmps(100)).wait_for_completed()                            
                    robot.play_anim('anim_keepaway_wingame_02').wait_for_completed()
                    hasBlock = False
                else:
                    robot.set_lift_height(0).wait_for_completed()                            
                    robot.play_anim('anim_keepaway_losegame_02').wait_for_completed()
                    name = "Out"
                    return                
