import numpy as np
import matplotlib.pyplot as plt

# direct to python 3 library-- env dependent
import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages')

import mido
from mido import MidiFile
import os.path
from os import path

# Constants defined- no UI yet
PATH_TO_MIDI = '/Users/elizamacneal/Desktop/piano_project/MIDIs/june.mid'
PATH_TO_IMAGE = '../shading.nosync/june.png'

def generate_roll():

    # check for roll pre-existence
    if path.exists(PATH_TO_ROLL):
        print('Roll already exists')
        return

    # load MIDI file
    try:
        mid = MidiFile(PATH_TO_MIDI)
    except IOError:
        print('IOError: MIDI file not located at input path')
        return

    # locate piano track
    piano_track_no = 1
    for i, track in enumerate(mid.tracks):
        if track.name == 'PIANO':
            piano_track_no = i
            break
    
    # get overall length-- i.e. image size
    time = 0
    for msg in mid.tracks[piano_track_no]:
        time += msg.time
    
    # generate image array
    roll = np.zeros((200, int(time/40.0)))
    
    # create holes
    switches = np.zeros((1, 88))
    time = 0
    for msg in mid.tracks[piano_track_no]:
        time += int(msg.time/40.0)
        if msg.type == 'note_on':
            channel = 200 - (msg.note - 20 + 5)*2
            if msg.velocity != 0:
                # punch hole opening
                roll[channel][time] = 1
            else:
                # fill in hole remainder
                index = time
                while roll[channel][index] != 1:
                    roll[channel][index] = 1
                    index -= 1

    # save image
    plt.imsave(PATH_TO_IMAGE, roll, cmap="gray", vmin=0, vmax=1)

def update_transmission_file():
    
    # TODO: retrieve transmission file
    return

generate_roll()
update_transmission_file()