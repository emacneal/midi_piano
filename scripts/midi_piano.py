# direct to python 3 library-- env dependent
import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages')

import maya.cmds as cmds
import mido
from mido import MidiFile

# constants: 'bpm' default (MIDI time in delta ticks, thus actually bpm/3) and num frames for key release animation
BPM_DEFAULT = 40.0
RELEASE_TIME = 3.0

# create UI
window = cmds.window(title='Midi Player Piano', widthHeight=(400, 250))
layout = cmds.rowColumnLayout(nc = 1, cw = [1, 400], rs = [1, 5])

# create path text field
ptf_text = cmds.text(label='Enter the full path to the MIDI file:')
ptf_input = cmds.textField(aie=True)

# create bpm text field
bpm_text = cmds.text(label='BPM (optional, default 120):')
bpm_input = cmds.textField(aie=True)

def animate_midi(*_):
    print('Opening MIDI file...')
    # open midi file
    try:
        mid = MidiFile(cmds.textField(ptf_input, query=True, text=True))
    except IOError:
        print('IOError: MIDI file not located at input path')
        return
    # clear all existing keyframes and set initial keyframe
    for i in range(1, 89):
        key = 'n' + str(i)
        cmds.select(key)
        cmds.cutKey(key, time=(1, 10000))
        cmds.setKeyframe(key, v = 0, attribute = 'rotateX', t=1)
    bpm = BPM_DEFAULT
    # define bpm
    if not cmds.textField(bpm_input, query=True, text=True):
        bpm = BPM_DEFAULT
    else:
        try:
            # divide bpm by 3 for MIDI delta tick logic
            bpm = float(cmds.textField(bpm_input, query=True, text=True))/3.0
        except ValueError:
            print('ValueError: BPM input must be a number')
            return
    print('Keyframing notes...')
    # sum event times and set keyframes for note on/off
    time = 0
    
    # locate piano track
    piano_track_no = 0
    for i, track in enumerate(mid.tracks):
        if track.name == 'PIANO':
            piano_track_no = i
            break
    
    # iterate over midi messages and keyframe notes
    for msg in mid.tracks[1]:
        time += msg.time
        if msg.type == 'note_on':
            key = 'n' + str(msg.note - 20)
            cmds.select(key)
            if msg.velocity != 0:
                note_down(key, time, msg.velocity, bpm)
            else:
                note_up(key, time, bpm)
        else:
            if msg.type == 'note_off':
                key = 'n' + str(msg.note - 20)
                cmds.select(key)
                note_up(key, time, bpm)
    print('Complete!')

# keyframe velocity informed note press
def note_down(note_object, time, velocity, bpm):
    cmds.select(note_object)
    cmds.setKeyframe(note_object, v = 0, attribute = 'rotateX', t=time/bpm)
    cmds.setKeyframe(note_object, v = 10, attribute = 'rotateX', t=(time+velocity)/bpm)
    
# keyframe speed defined note release
def note_up(note_object, time, bpm):
    cmds.select(note_object)
    cmds.setKeyframe(note_object, v = 10, attribute = 'rotateX', t=time/bpm)
    cmds.setKeyframe(note_object, v = 0, attribute = 'rotateX', t=time/bpm+RELEASE_TIME)
   
# make executable on enter/return 
cmds.textField( ptf_input, edit=True, enterCommand=animate_midi)
cmds.textField( bpm_input, edit=True, enterCommand=animate_midi)

# create execution button
animate_button = cmds.button(label='Animate', command=animate_midi)

#create clear key frames button
def clear_keyframes(*_):
    for i in range(1, 89):
        key = 'n' + str(i)
        cmds.select(key)
        cmds.cutKey(key, time=(1, 100000))
        cmds.setAttr(key + '.rx', 0)
    print('Piano key frames cleared.')
clear_button = cmds.button(label= 'Clear key frames', command = clear_keyframes)

# create mp3 path text field
mp3_text = cmds.text(label='Enter the full path to an mp3 file (optional):')
mp3_input = cmds.textField(aie=True)

# add audio node for mp3 input
def add_audio(*_):
    cmds.sound(file=cmds.textField( mp3_input, query=True, text=True), name='sound_file')
    cmds.timeControl( 'timeControl1', edit=True, sound='sound_file' )
cmds.textField( mp3_input, edit=True, enterCommand=add_audio)

# create close button
def close_window(*_):
    cmds.deleteUI(window)
close_button = cmds.button(label= 'Close', command = close_window)

# open UI
cmds.showWindow(window)