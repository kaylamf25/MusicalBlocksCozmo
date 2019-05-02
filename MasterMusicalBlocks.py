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

while roundNumber > 0:
    numOfCozmos = int(input("Enter the number of Cozmos playing: "))
    numOfBlocks = int(input("Enter the number of blocks this round: ")) 
    readyCount = 0;
    while readyCount<numOfCozmos and (roundNumber == 1):
        s.sendall(b'Ready?')  
        bytedata = s.recv(4048)
        data = bytedata.decode('utf-8')
        print(data)
        instructions = data.split(';')
        if instructions[0] == 'Ready': #if a cozmo finds a block it should get into here
            readyCount = readyCount + 1 
        elif instructions[0] == 'ReadyReady':
            readyCount = readyCount + 2
    print("Begin")
    waitTime = random.randint(10,20)
    startTime = random.randint(0, 211-waitTime)
    print("Wait time: ",waitTime)    
    print("Start time: ",startTime)
    pygame.mixer.init()
    pygame.mixer.music.load('The_Hampster_Dance.mp3') #211 seconds long
    s.sendall(b'Music')
    time.sleep(1)
    waitTimeString = str(waitTime)
    b= bytes(waitTimeString,'utf-8')
    s.sendall(b)
    #s.sendall(str.encode(waitTime))
    #s.sendall(b"" + str(waitTime) + b"")
    #s.send(str.encode(waitTime))
    pygame.mixer_music.play(start=startTime)
    time.sleep(waitTime)
    s.sendall(b'Stop')
    time.sleep(1)
    s.sendall(b'Look') #start looking
    pygame.mixer_music.stop()
    
    while (not(blocksFound==numOfBlocks)):
        if listen == True:
            bytedata = s.recv(4048)
            data = bytedata.decode('utf-8')
            print(data)
            instructions = data.split(';')
            if instructions[0] == 'BlockFound': #if a cozmo finds a block it should get into here
                blocksFound = blocksFound + 1            
            else:
                listen = True
                s.sendall(b'Look')
        
    listenCount = 0
    while listenCount<numOfCozmos:
        s.sendall(b'Listening?')  
        bytedata = s.recv(4048)
        data = bytedata.decode('utf-8')
        print(data)
        instructions = data.split(';')
        if instructions[0] == 'Listening': 
            listenCount = listenCount + 1 
        elif instructions[0] == 'ListeningListening':
            listenCount = listenCount + 2    
    
    listenCount = 0
    if(numOfBlocks == 1):
        time.sleep(1)
        s.sendall(b'GameOver')
        roundNumber = 0    
        blocksFound = 0
    else:
        time.sleep(1)
        s.sendall(b'RoundOver') #post game celebration or sad and name change3  
        blocksFound = 0 #set the amount of blocks found back to 0 for the next round
        roundNumber = roundNumber + 1
