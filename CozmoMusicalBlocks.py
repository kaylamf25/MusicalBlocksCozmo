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
    except socket_error as msg:
        robot.say_text("socket failed to bind").wait_for_completed()
    cont = True
    
    name = "Playing"
    
    while cont:
        robot.set_lift_height(0).wait_for_completed()
        hasBlock = False
        cubes = None
        cozmo.robot.Robot.start_freeplay_behaviors(robot)
        bytedata = s.recv(4048)
        data = bytedata.decode('utf-8')
        print(str(data))
        if not data:
            cont = False
            s.close()
            quit()
        else:
            cozmo.robot.Robot.stop_freeplay_behaviors(robot)
            print(data)
            instructions = data.split(';')
            if instructions[0] == name:
                print("In name")
                hasBlock = False
                if len(instructions) == 2:  
                    print("Correct length")
                    if instructions[1] == 1:
                        print("1")
                        while not hasBlock:
                            print("In while loop")
                            lookaround = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
                            cubes = robot.world.wait_until_observe_num_objects(num=1, object_type=cozmo.objects.LightCube, timeout=60)
                            lookaround.stop()
                            current_action = robot.pickup_object(cubes[0], num_retries=3)
                            current_action.wait_for_completed()
                            if current_action.has_failed:
                                code, reason = current_action.failure_reason
                                result = current_action.result
                                print("Pickup Cube failed: code=%s reason='%s' result=%s" % (code, reason, result))
                                cubes = None
                                return
                            else:    
                                print("Worked")
                                hasBlock = True                                                
                    elif instructions[1] == 2:
                        #triggers cozmo to celebrate if they have a block or get sad if he doesn't have one
                        if(hasBlock == True):
                            robot.set_lift_height(0).wait_for_completed()
                            robot.drive_straight(cozmo.util.distance_mm(-100), cozmo.util.speed_mmps(100)).wait_for_completed()                            
                            robot.play_anim_trigger(cozmo.anim.Triggers.OnSpeedtapGameCozmoWinHighIntensity).wait_for_completed()
                        else:
                            robot.set_lift_height(0).wait_for_completed()                            
                            robot.play_anim_trigger(cozmo.anim.Triggers.OnSpeedtapGamePlayerWinHighIntensity).wait_for_completed()
                            name = "Out"
                        return
                    elif instructions[1] == 3:
                        #sent if only 1 block was to be found to declare winner
                        if(hasBlock == True):
                            robot.set_lift_height(0).wait_for_completed()
                            robot.drive_straight(cozmo.util.distance_mm(-100), cozmo.util.speed_mmps(100)).wait_for_completed()                            
                            robot.play_anim_trigger(cozmo.anim.Triggers.OnSpeedtapGameCozmoWinHighIntensity).wait_for_completed()                        
                            robot.say_text("Winner").wait_for_completed()
                        else:
                            robot.set_lift_height(0).wait_for_completed()                            
                            robot.play_anim_trigger(cozmo.anim.Triggers.OnSpeedtapGamePlayerWinHighIntensity).wait_for_completed()
                            name = "Out"                        
                elif instructions[0] == "Ready?":
                    s.sendall(b'Ready')
                
                
                
                
                
cozmo.run_program(cozmo_program)