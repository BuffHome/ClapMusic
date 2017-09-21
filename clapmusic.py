#!/usr/bin/python

import pyaudio
import sys
import vlc
import os
import _thread as thread
from time import sleep
from array import array

#global needed:
clap = 0
flag = 0
normal = 0
ignoreClapFlag = False

#music
folders = ["E:\MusicForDays\Muse"]
numbers = ["./MusicForDays/Coldplay/Coldplay - Clocks.mp3",
		"./MusicForDays/Coldplay/Coldplay - Magic.mp3"]

#scalars:
threshold = 10000 #at what level should it be considered a clap
normalMultiplierDown = 0.002
normalMultiplierUp = 0.25
clapTimeLimit = 6
wait = 2


def playOrPause():
	global list_player
	global ignoreClapFlag
	
	if not list_player.is_playing():
		print("QUEUE MUSIC")
		list_player.play()
		ignoreClapFlag = True
	else:
		print("Pause that shit")
		list_player.pause()
def nextSong():
	global list_player
	
	print("Next song please")
	list_player.next()
	ignoreClapFlag = True

	
	
def waitForClaps(threadName):
	global clap
	global flag
	global wait
	
	sleep(wait)
	print("Found ", clap," claps in the time interval -> ",end="")
	if clap == 2:
		playOrPause()
	elif clap == 3:
		nextSong()
	else:
		print("discard")
	
	
	clap = 0
	flag = 0
#get input from stream
def getInput():
	global stream
	global chunk
	data = stream.read(chunk)
	as_ints = array('h', data)
	return as_ints
#init the stream
def init():
	print("Clap detection initializing");
	global clap
	global flag
	global threshold
	global stream
	global chunk
	global pya
	global list_player
	global media

	chunk = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 44100
	
	max_value = 0
	pya = pyaudio.PyAudio()
	stream = pya.open(format=FORMAT,
		channels=CHANNELS, 
		rate=RATE, 
		input=True,
		output=True,
		frames_per_buffer=chunk)

	print("Setting up media player")
	
	Instance = vlc.Instance()
	
	mediaList = Instance.media_list_new()
	#for med in numbers:
		#mediaList.add_media(Instance.media_new(med))
	for folder in folders:
		for file in os.listdir(folder):
			med = "\\".join([folder,file])
			mediaList.add_media(Instance.media_new(med))
			
			
	list_player = Instance.media_list_player_new()
	list_player.set_media_list(mediaList)	
#main
def main():
	global threshold
	global clap
	global flag
	global pya
	global normal
	global normalMultiplier
	global clapTimeLimit
	global ignoreClapFlag
	
	possibleClap = 0
	clapTimeout = 0
	showStatTimer = 5
	ignoreClapFlagTimer = 200
	ignoreClapFlag = True
	try:
		print("Clap detection started, processing sound...")
		while True:
			max_value = max(getInput())
			
			if ignoreClapFlag:
				if ignoreClapFlagTimer == 0:
					ignoreClapFlagTimer = 200
				ignoreClapFlagTimer -= 1
				if ignoreClapFlagTimer == 0:
					ignoreClapFlag = False
			
			if (possibleClap == 0 and clapTimeout != 0):
				clapTimeout = 0
			if (possibleClap != 0):
				clapTimeout += 1
			if (clapTimeout > clapTimeLimit):
				clapTimeout = 0
				possibleClap = 0
			
			
			if (max_value - normal > threshold):
				if (possibleClap == 0):
					possibleClap = 1
			else:
				if (possibleClap == 1):
					possibleClap = 2
			
			
			if possibleClap == 2 and not ignoreClapFlag:
				possibleClap = 0
				clap += 1
				print("Clap detected (",clap,")\t\t\t\t\t\t\t\t\t\t", end="\r")
				if flag == 0:
					thread.start_new_thread( waitForClaps, ("waitThread",) )
					flag = 1
			
			if clap == 0:
				print("[",end="")
				for x in range(0,80):
					if x * 500 < normal and normal < (x+1) * 500:
						print("N",end="")
					elif x * 500 < (normal + threshold) and (normal + threshold) < (x+1) * 500:
						print("T",end="")
					elif x * 500 < max_value:
						print("=",end="")
					else:
						print(".",end="")
					#print(max_value, "\t", normal, "\t", possibleClap, end="\r")
				print("] - ", ignoreClapFlag, end="\r")
					
					
			if (possibleClap == 0):
				if (max_value > normal):
					normal = (normal + (max_value * normalMultiplierUp)) / (1.0 + normalMultiplierUp)
				else:
					normal = (normal + (max_value * normalMultiplierDown)) / (1.0 + normalMultiplierDown)
			
				
	except (KeyboardInterrupt, SystemExit):
		print("\rExiting")
		stream.stop_stream()
		stream.close()
		pya.terminate()
	
	
	
	
	
	
	
	
	
					
##calling the main method when needed
if __name__ == '__main__':
	init()
	main()