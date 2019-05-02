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

#connect to network
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

#set global variables
roundNumber = 1
blocksFound = 0
listen = True

#While loop counting through the rounds. When the game is over it sets it to 0 which breaks the loop
while roundNumber > 0:
    numOfCozmos = int(input("Enter the number of Cozmos playing: ")) #User enters number of cozmos still playing or starting
    numOfBlocks = int(input("Enter the number of blocks this round: ")) #User enters the number of blocks to be found
    #check to make sure they're all ready to begin only in the first round
    readyCount = 0;
    while readyCount<numOfCozmos and (roundNumber == 1):
        s.sendall(b'Ready?')  
        bytedata = s.recv(4048)
        data = bytedata.decode('utf-8')
        print(data)
        instructions = data.split(';')
        if instructions[0] == 'Ready': #if a cozmo finds a block it should get into here
            readyCount = readyCount + 1 
        elif instructions[0] == 'ReadyReady': #safe guards if it collects 2 at once which happens surprisingly often
            readyCount = readyCount + 2
    #game play begins
    print("Begin")
    waitTime = random.randint(10,20) #randomized run time for the song
    startTime = random.randint(0, 211-waitTime) #randomized start time
    print("Wait time: ",waitTime)  
    print("Start time: ",startTime)
    #get the song ready
    pygame.mixer.init()
    pygame.mixer.music.load('The_Hampster_Dance.mp3') #211 seconds long
    s.sendall(b'Music') #tell the cozmos the music is coming
    time.sleep(1)
    #tell the cozmos how long to spin for
    waitTimeString = str(waitTime)
    b= bytes(waitTimeString,'utf-8') #convert string to bytes
    s.sendall(b)
    #start the song and wait for the wait time to stop
    pygame.mixer_music.play(start=startTime)
    time.sleep(waitTime)
    #s.sendall(b'Stop') #this line is probably not necessary
    time.sleep(2)
    #tell them to look
    s.sendall(b'Look')
    #stop the music
    pygame.mixer_music.stop()
    
    while (not(blocksFound==numOfBlocks)): #until the blocks are found listen to the cozmos
        if listen == True:
            bytedata = s.recv(4048)
            data = bytedata.decode('utf-8')
            print(data)
            instructions = data.split(';')
            if instructions[0] == 'BlockFound': #if a cozmo finds a block it should get into here
                blocksFound = blocksFound + 1            
            else: #if not it should tell them to look still
                listen = True
                s.sendall(b'Look')
    
    #this section is like ready to just be sure they're paying attention
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
    listenCount = 0 #reset the variable
    
    #check to see if game is over or round is over and send appropriate messages while reseting important variables
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
