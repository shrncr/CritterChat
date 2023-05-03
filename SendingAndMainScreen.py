import RPi.GPIO as GPIO
import uuid #for random file names
import PIL
from database import *
import pyaudio
import wave
from play import playPressedFunc
#for the camera
from picamera import PiCamera
#make your camera
camera=PiCamera()
import pygame, sys
from pygame.locals import *
from time import sleep
from database import * #YOUR database file
import numpy as np
import pyautogui
from tkinter import *

#we had gpio buttons for sending and playing
GPIO.setmode(GPIO.BCM)

button1 = 17
GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
button2 = 4
GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#basic initial variables
run = False #check if msg should be recording (used in the drawing option)
sendPressed = False #whether send button pressed or not
tempFileName = "" #global-- changes with each sent message


#screenshot
def ss():
    global tempFileName
    tempFileName = str(uuid.uuid4())
    pyautogui.screenshot("{}.png".format(tempFileName))

def get_filename_from_cd(cd):
    if not cd:
        print("not")
        return(None)
    fname = re.findall('filename=(.+)'. cd)
    if len(fname) == 0:
        print("nnn")
        return(None)
    return fname[0]



#When the send button is pressed, changes the global "sendpressed" boolean to true
def sendPressedFunc(channel):
    print("SP")
    global sendPressed
    sendPressed = True

#continuously checks inside of the drawing screen if the drawing screen should still be up. Stops running if send button gets pressed
#redundant code. should change...
def getRun(): 
    global run
    global sendPressed
    if sendPressed == True:
        run = False
        pressed = False
        sendPressed =False #NEW LINE ADDED
        
#opens drawing screen when prompted. closes when send button pressed
def startDraw(): 
    fps = 60
    timer = pygame.time.Clock()
    width = 800
    height = 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Critter Draw')
    global run
    global t
    run = True
    activeSize = 15
    activeColor = [0,0,0,0]
    painting = []
    screen.fill([255,255,255,255])
    while run:
        mouse = pygame.mouse.get_pos()
        timer.tick(180)
        getRun()
        for event in pygame.event.get():
            if event.type == pygame.QUIT : ##must check in here
                run = False
            if pygame.mouse.get_pressed()[0]:
                painting.append((activeColor, mouse, activeSize))
                for i in range(len(painting)):
                    pygame.draw.circle(screen, painting[i][0], painting[i][1], painting[i][2])
        pygame.display.flip()
    ss()
    pygame.quit()
    return(r'{}.png'.format(tempFileName)) #when made into variable, the file is returned

#records video until send button pressed
def startRec(): 
    global tempFileName
    tempFileName = str(uuid.uuid4())
    camera.start_preview()
    camera.start_recording('/home/pi/{}.h264'.format(tempFileName))
    global run
    run = True
    while run:
        getRun()
    camera.stop_recording()
    camera.stop_preview()
    return('{}.h264'.format(tempFileName))
        


#starts audio message when prompted
def startAud():
    #all details of what is recording the audio
    
    form_1 = pyaudio.paInt16 # 16-bit resolution
    chans = 1 # 1 channel
    samp_rate = 44100 # 44.1kHz sampling rate
    chunk = 8192 # 2^12 samples for buffer
    record_secs = 5 # seconds to record
    dev_index = 1 # device index found by p.get_device_info_by_index(ii)
    global tempFileName
    tempFileName = str(uuid.uuid4())
    wav_output_filename = '{}.wav'.format(tempFileName)

    audio = pyaudio.PyAudio() #instantiate pyaudio obj

    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=chunk)
    frames = []

    # continuously add audio chunks to array
    for ii in range(0,int((samp_rate/chunk)*record_secs)):
        data = stream.read(chunk)
        frames.append(data)

    #end the process
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save the audio frames as .wav file
    wavefile = wave.open(wav_output_filename,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()
    sleep(.02)

    return(wav_output_filename)

#function will be called after the choice gui opens and the user taps on which type of message they'd like to send
def startMessage(choice):
    global run
    if choice == None:
        return(None)
    #each elif follows same logic
    elif choice == "Drawing": #if drawing button pressed
        pic = startDraw() #saves media, returns media's filename
        repoURL = putMedia(pic) #puts file onto github and returns the repo's url
        add_comment(repoURL, 1) #adds media's repo's url to the db and signals which pi sent it
        os.remove(pic) #removes media from your own pi to save space
    elif choice == "Video":
        vid = startRec()
        repoURL = putMedia(vid)
        print(repoURL)
        add_comment(repoURL, 1) #adds repo's url for file to the mongo db and signals which pi sent it
        os.remove(vid)
        
    elif choice == "Audio":
        aud = startAud()
        repoURL = putMedia(aud)
        print(repoURL)
        add_comment(repoURL, 1) #adds repo's url for file to the mongo db and signals which pi sent it
        os.remove(aud)


#when pushed sendpressed, connect sendpressed func
GPIO.add_event_detect(4,GPIO.FALLING,callback=sendPressedFunc)
#when pushed playpressed, connect playpressed func
GPIO.add_event_detect(17,GPIO.FALLING,callback=playPressedFunc)

choice = None

class Startscreen(Frame):
    
    def __init__(self, window):
        
        Frame.__init__(self, window)
        self.Button1=Button(window,text="VIDEO Message",bg="grey",command=lambda:self.chooseType("Video"))#connection to transition screan                                                               
        self.Button1.pack(fill=BOTH,expand=True)
        
        self.Button2=Button(window,text="Audio Message",bg="red",command=lambda:self.chooseType("Audio"))#connection to transition screan
        self.Button2.pack(fill=BOTH,expand=True)
        
        self.Button3=Button(window,text="Screen recording",bg="yellow",command=lambda:self.chooseType("Drawing"))#connection to transition screan
        self.Button3.pack(fill=BOTH,expand=True)
    
    def chooseType(self,x): #button pressed, connects the function to start message. also redundant :(
        global choice
        choice=x
        print(choice)
        startMessage(choice)
    
#create window             
window = Tk()
window.geometry('800x480+0+0')
window.title("Critter Chat")
g = Startscreen(window)


window.mainloop()