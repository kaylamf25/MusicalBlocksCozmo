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
    
    name = "Playing"
    readyIsDone = False
    GameOver = False
    hasBlock = False
    cubes = None    
    robot.set_lift_height(0).wait_for_completed()
    robot.set_head_angle(degrees(0)).wait_for_completed()
    
    while cont:
        #cozmo.robot.Robot.start_freeplay_behaviors(robot)
        bytedata = s.recv(4048)
        data = bytedata.decode('utf-8')
        print(str(data))
        if not data:
            cont = False
            s.close()
            quit()
        else:
            #cozmo.robot.Robot.stop_freeplay_behaviors(robot)
            #robot.say_text("message received").wait_for_completed()
            instructions = data.split(';')
            #robot.say_text("Split data").wait_for_completed()
            GameOver = False;
            #robot.say_text("Before name check").wait_for_completed()
            if instructions[0] == name:
                #robot.say_text("my name").wait_for_completed()
                if len(instructions) == 2: 
                    #robot.say_text("Length 2").wait_for_completed()
                    if instructions[1] == "1":
                        #robot.say_text("Before has block").wait_for_completed()
                        #robot.say_text("Before while loop").wait_for_completed()
                        while (not hasBlock) and (not GameOver):
                            #robot.say_text("In while loop").wait_for_completed()
                            lookaround = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
                            cubes = robot.world.wait_until_observe_num_objects(num=1, object_type=cozmo.objects.LightCube, timeout=20)
                            lookaround.stop()
                            if cubes[0] != None:
                                current_action = robot.pickup_object(cubes[0], num_retries=1)
                                current_action.wait_for_completed()
                                if current_action.has_failed:
                                    code, reason = current_action.failure_reason
                                    result = current_action.result
                                    print("Pickup Cube failed: code=%s reason='%s' result=%s" % (code, reason, result))
                                    cubes = None
                                else:    
                                    s.sendall(b'BlockFound')    
                                    hasBlock = True
                            #robot.say_text("Ran program").wait_for_completed()
                            bytedata = s.recv(4048)
                            data = bytedata.decode('utf-8')
                            print(str(data))
                            if data:
                                instructions = data.split(';')
                                if instructions[1] == "2":
                                    GameOver = True
                                elif instructions[1] == "3":
                                    GameOver = True                                                                
                    elif instructions[1] == "2":
                        GameOver = True
                        robot.say_text("In phase 2").wait_for_completed()
                        #triggers cozmo to celebrate if they have a block or get sad if he doesn't have one
                        if(hasBlock == True):
                            robot.set_lift_height(0).wait_for_completed()
                            robot.drive_straight(cozmo.util.distance_mm(-100), cozmo.util.speed_mmps(100)).wait_for_completed()                            
                            robot.play_anim_trigger(cozmo.anim.Triggers.OnSpeedtapGameCozmoWinHighIntensity).wait_for_completed()
                        else:
                            robot.set_lift_height(0).wait_for_completed()                            
                            robot.play_anim_trigger(cozmo.anim.Triggers.OnSpeedtapGamePlayerWinHighIntensity).wait_for_completed()
                            name = "Out"
                    elif instructions[1] == "3":
                        GameOver = True
                        robot.say_text("In phase 3").wait_for_completed()
                        #sent if only 1 block was to be found to declare winner
                        if(hasBlock == True):
                            robot.set_lift_height(0).wait_for_completed()
                            robot.drive_straight(cozmo.util.distance_mm(-100), cozmo.util.speed_mmps(100)).wait_for_completed()                            
                            robot.play_anim('anim_keepaway_wingame_02').wait_for_completed()                        
                            robot.say_text("Winner").wait_for_completed()
                            return
                        else:
                            robot.set_lift_height(0).wait_for_completed()                            
                            robot.play_anim('anim_keepaway_losegame_02').wait_for_completed()
                            name = "Out"  
                            return
            elif ((instructions[0] == "Ready?") and (not readyIsDone)):
                s.sendall(b'Ready')
                readyIsDone = True
                
    
                
                
                
                
                
                
cozmo.run_program(cozmo_program)
