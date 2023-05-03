import urllib.request
import moviepy
from moviepy.editor import *
import pygame
import vlc
import os
from database import *
from PIL import Image
from time import sleep

def playPressedFunc():
    msgs, vids = get_from_other_pi(0) #get messages and vids from pi
    skel = "https://raw.githubusercontent.com/shrncr/Media/main/" #use this for when you download files
    inc = 0
    for vid in vids: #for each vid from the other pi
        vid = str(vid) #cast to string
        fName = vid[53:-2] #cut the string into just the filename. This will depend on the length of your media repo name and such
        msgURL = skel + fName #get the real url for the file in your media repo
        r = requests.get(msgURL, allow_redirects = True) #get the contents from this url!
        
        if ".h264" in vid: #if the message was a video
            open('tempVid.h264', 'wb').write(r.content) #download as file
            #open and play in vlc player
            player = vlc.MediaPlayer(r"tempVid.h264")
            player.play()
            #let it play for a bit
            sleep(5)
            #delete the vid
            os.remove(r'tempVid.h264')
        if ".png" in vid: #if img file
            open('tempPic.png', 'wb').write(r.content) #download as file
            #open and show pic
            img = Image.open(r'tempPic.png') 
            img.show()
            #let it show for a bit, then delete
            sleep(3)
            os.remove(r'tempPic.png')
        if ".wav" in vid: #if audio file
            open('tempAud.wav', 'wb').write(r.content) #download as file
            #open and play in vlc
            player = vlc.MediaPlayer(r"tempAud.wav")
            player.play()
            #delete after
            os.remove(r'tempAud.wav')
        #cut ONLY the comment id out from the "msgs" variable. line 46 splices the front off and the next line takes the end portion off
        spliceFront= str((msgs[inc]))[18:]
        comment_id = spliceFront[:(spliceFront.index(')') - 1)]
        #delete comment of message that just played from the database so it cannot be accessed again.
        delete_comment(comment_id)
        #inc variable for knowing which msg youre on
        inc+= 1

