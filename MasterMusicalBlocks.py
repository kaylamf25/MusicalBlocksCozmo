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

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket_error as msg:
    print("socket failed" + msg).wait_for_completed()
ip = "10.0.1.10"
port = 5000
 
try:
    s.connect((ip, port))
except socket_error as msg:
    print("socket failed to bind").wait_for_completed()
cont = True 

roundNumber = 1
blocksFound = 0
listen = True

waitTime = random.randint(5,15)
print(waitTime)
time.sleep(waitTime)
s.sendall(b'Playing;1') #start looking

while roundNumber > 0:
    numOfCozmos = int(input("Enter the number of Cozmos playing: "))
    numOfBlocks = int(input("Enter the number of blocks this round: ")) 
    readyCount = 0;
    while(readyCount<numOfCozmos):
        s.sendall(b'Ready?')  
        bytedata = s.recv(4048)
        data = bytedata.decode('utf-8')
        print(data)
        instructions = data.split(';')
        if instructions[0] == 'Ready': #if a cozmo finds a block it should get into here
            readyCount = readyCount + 1          
    print("Begin")
    waitTime = random.randint(10,45)
    startTime = random.randint(0, 211-waitTime)
    print("Wait time: ",waitTime)    
    print("Start time: ",startTime)
    pygame.mixer.init()
    pygame.mixer.music.load('The_Hampster_Dance.mp3') #211 seconds long
    pygame.mixer_music.play(start=startTime)
    time.sleep(waitTime)
    s.sendall(b'Playing;1') #start looking
    pygame.mixer_music.stop()    
    if listen == True:
        bytedata = s.recv(4048)
        data = bytedata.decode('utf-8')
        print(data)
        instructions = data.split(';')
        if instructions[0] == 'BlockFound': #if a cozmo finds a block it should get into here
            blocksFound = blocksFound + 1            
    else:
        listen = True
        
    if blocksFound == numOfBlocks:
        s.sendall(b'Playing;2') #post game celebration or sad and name change
        if(blocksFound == 1):
            s.sendall(b'Playing;3')
            roundNumber = 0;
            return
        else:
            blocksFound = 0; #set the amount of blocks found back to 0 for the next round
            roundNumber = roundNumber + 1
        continue
