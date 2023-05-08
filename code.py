from adafruit_macropad import MacroPad
from rainbowio import colorwheel
import time
import board
import adafruit_mpu6050

# MPU6050 setup
i2c = board.I2C()  # uses board.SCL and board.SDA
mpu = adafruit_mpu6050.MPU6050(i2c, address=0x68)

# Initialize MacroPad
macropad = MacroPad()  # create the macropad object, (orientation)
macropad.display.auto_refresh = False  # avoid lag
CC_NUM = 74  # select default CC number

# STARTUP #
macropad.display_image("blinka.bmp")
time.sleep(2)

# --- Pixel setup --- #
key_color = colorwheel(170)  # fill with color 
macropad.pixels.brightness = 1
macropad.pixels.fill(key_color)

# --- MIDI variables ---
mode = 0
mode_text = [
    "Key Color", ("Custom #%s" % (CC_NUM)),
      "Pitch Bend", "Custom + Bend", "Transpose", "Choose Key", "Choose Scale"]  # initial text onscreen for each modes
midi_values = [0, 16, 8, 0, 48, 3, 0]  # plus no. to start position

# --- Display text setup ---
text_lines = macropad.display_text("Portable MIDI Macropad")
text_lines[0].text = "Mode: Key Color".format(midi_values[0]+1)  # Patch display offset by 1
text_lines[1].text = "Press knob for modes"
text_lines.show()

last_knob_pos = macropad.encoder  # store knob position state

# Chromatic scale starting with C3 as bottom left keyswitch
midi_notes = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59]

# Scale mode states
majorState = False
minorState = False
majorPentaState = False
minorPentaState = False
bluesState = False
dorianState = False

# Functions to set LED colors for different scales
def reset():
    macropad.pixels.fill(key_color)
def major():
    # Set the LED color for major scale keys
    macropad.pixels[0] = (255, 0, 0) 
    macropad.pixels[2] = (255, 0, 0)
    macropad.pixels[4] = (255, 0, 0)  
    macropad.pixels[5] = (255, 0, 0)  
    macropad.pixels[7] = (255, 0, 0)  
    macropad.pixels[9] = (255, 0, 0)
    macropad.pixels[11] = (255, 0, 0)
def minor():
    # Set the LED color for minor scale keys
    macropad.pixels[0] = (255, 0, 0) 
    macropad.pixels[2] = (255, 0, 0)
    macropad.pixels[3] = (255, 0, 0)  
    macropad.pixels[5] = (255, 0, 0)  
    macropad.pixels[7] = (255, 0, 0)  
    macropad.pixels[8] = (255, 0, 0)
    macropad.pixels[10] = (255, 0, 0)
def majorPenta():
    # Set the LED color for major pentatonic scale keys
    macropad.pixels[0] = (255, 0, 0) 
    macropad.pixels[2] = (255, 0, 0)
    macropad.pixels[4] = (255, 0, 0)  
    macropad.pixels[7] = (255, 0, 0)  
    macropad.pixels[9] = (255, 0, 0)  
def minorPenta():
    # Set the LED color for minor pentatonic scale keys
    macropad.pixels[0] = (255, 0, 0) 
    macropad.pixels[3] = (255, 0, 0)
    macropad.pixels[5] = (255, 0, 0)    
    macropad.pixels[7] = (255, 0, 0)  
    macropad.pixels[10] = (255, 0, 0)
def blues():
    # Set the LED color for blues scale keys
    macropad.pixels[0] = (255, 0, 0) 
    macropad.pixels[3] = (255, 0, 0)
    macropad.pixels[5] = (255, 0, 0)   
    macropad.pixels[6] = (255, 0, 0)
    macropad.pixels[7] = (255, 0, 0)  
    macropad.pixels[10] = (255, 0, 0)
def dorian():
    # Set the LED color for dorian scale keys
    macropad.pixels[0] = (255, 0, 0) 
    macropad.pixels[2] = (255, 0, 0)
    macropad.pixels[3] = (255, 0, 0)   
    macropad.pixels[5] = (255, 0, 0)
    macropad.pixels[7] = (255, 0, 0)  
    macropad.pixels[9] = (255, 0, 0)
    macropad.pixels[10] = (255, 0, 0)

while True:
    if mode == 1:    # Continuous Control (CC) and Custom modes
        x, y, _ = mpu.acceleration   # Read accelerometer values for X and Y axis
        control_change_value = min(max(127-(int(x * 4) + 64), 0), 127) # scale x acceleration to control change value, ensuring it stays within the valid range (0-127)
        macropad.midi.send(macropad.ControlChange(CC_NUM, control_change_value)) # Send control change message with the calculated value
        text_lines[0].text = ("Mode: %s %d" % (mode_text[mode], control_change_value)) # Update display with mode and control change value

    if mode == 2:   # Pitch Bend Gyro Mode
        x, y, _ = mpu.acceleration # Read accelerometer values for X and Y axis
        pitch_bend_value = min(max(16383-(int(x * 1024) + 8192), 0), 16383) # scale x acceleration to pitch bend value, ensuring it stays within the valid range
        macropad.midi.send(macropad.PitchBend(pitch_bend_value))  # send pitch bend message
        text_lines[0].text = "Pitch Bend: {}".format(pitch_bend_value)  # Update display with mode and pitch bend value

    if mode == 3:  # CC/Custom + PitchBend
        x, y, _ = mpu.acceleration  # Read accelerometer values for X and Y axis
        control_change_value = min(max(127-(int(y * 4) + 64), 0), 127)  # scale y acceleration to control change value, ensuring it stays within the valid range (0-127)
        macropad.midi.send(macropad.ControlChange(CC_NUM, control_change_value))    # Send control change message with the calculated value
        pitch_bend_value = min(max(16383-(int(x * 1024) + 8192), 0), 16383) # scale x acceleration to pitch bend value, ensuring it stays within the valid range
        macropad.midi.send(macropad.PitchBend(pitch_bend_value))  # send pitch bend message
        text_lines[0].text = "CC: {}, Pitch: {}".format(control_change_value, pitch_bend_value)   # Update display with mode and pitch bend value as well as control change value

    while macropad.keys.events:  # check for key press and release
        key_event = macropad.keys.events.get()
        if key_event:
            if key_event.pressed:  # check for key press
                key = key_event.key_number  # get key number from key event
                macropad.midi.send(macropad.NoteOn(midi_notes[key], 120))  # send midi noteon
                macropad.pixels[key] = colorwheel(30)  # light up different color
                text_lines[1].text = "NoteOn:{}".format(midi_notes[key]) # write the note onscreen

            if key_event.released:  # check for release
                key = key_event.key_number # get key number from key event
                macropad.midi.send(macropad.NoteOff(midi_notes[key], 0))  # send midi noteoff
            # Update LED color depending on the scale state. If pressed key is red from selected scale, 
            # it will turn red again, otherwise LED will turn back to current key_color
                if majorState == True:                      # if major scale is selected
                    if key in [0,2,4,5,7,9,11]:             # if keys in selected scale is pressed
                        macropad.pixels[key] = (255, 0, 0)  # keys would return back to red
                    else:
                        macropad.pixels[key] = key_color    # else return to key_color
                elif minorState == True:
                    if key in [0,2,3,5,7,8,10]:
                        macropad.pixels[key] = (255, 0, 0)
                    else:
                        macropad.pixels[key] = key_color
                elif majorPentaState == True:
                    if key in [0,2,4,7,9]:
                        macropad.pixels[key] = (255, 0, 0)
                    else:
                        macropad.pixels[key] = key_color
                elif minorPentaState == True:
                    if key in [0,3,5,7,10]:
                        macropad.pixels[key] = (255, 0, 0)
                    else:
                        macropad.pixels[key] = key_color
                elif bluesState == True:
                    if key in [0,3,5,6,7,10]:
                        macropad.pixels[key] = (255, 0, 0)
                    else:
                        macropad.pixels[key] = key_color
                elif dorianState == True:
                    if key in [0,2,3,5,7,9,10]:
                        macropad.pixels[key] = (255, 0, 0)
                    else:
                        macropad.pixels[key] = key_color
                else:            
                    macropad.pixels[key] = key_color  # if no scale is selected, return to color set by encoder bank value (key_color)
                text_lines[1].text = "NoteOff:{}".format(midi_notes[key])

    macropad.encoder_switch_debounced.update()      # check the knob switch for press or release
    if macropad.encoder_switch_debounced.pressed:   # check knob switch for press
        mode = (mode+1) % 7 # total modes is 7      # text if mode is selected
        if mode == 0:   
            text_lines[0].text = ("Mode: %s %d" % (mode_text[mode], midi_values[mode]+1))
        elif mode == 1:
            text_lines[0].text = ("Mode: %s %d" % (mode_text[mode], int(midi_values[mode]*4.1)))
        elif mode == 2:
            text_lines[0].text = ("Mode: %s %d" % (mode_text[mode], midi_values[mode]-8))
        elif mode == 3:
            text_lines[0].text = ("Mode: Custom + Bend")
        elif mode == 4:
            text_lines[0].text = ("Mode: %s %d" % (mode_text[mode], midi_values[mode]-48))
        elif mode == 5:
            text_lines[0].text = ("Mode: %s %d" % (mode_text[mode], midi_values[mode]-3))
        else:
            text_lines[0].text = ("Mode: Choose Scale")
        macropad.red_led = macropad.encoder_switch 
        text_lines[1].text = " "  # clear the note line

    if macropad.encoder_switch_debounced.released:  # check knob switch for release
        macropad.red_led = macropad.encoder_switch

    if last_knob_pos is not macropad.encoder:  # knob has been turned
        knob_pos = macropad.encoder  # read encoder
        knob_delta = knob_pos - last_knob_pos  # compute knob_delta since last read
        last_knob_pos = knob_pos  # save new reading

        if mode == 0:  # Change key color
            midi_values[mode] = min(max(midi_values[mode] + knob_delta, 0), 127)  # delta + minmax
            key_color = colorwheel(midi_values[mode]+120)  # change key_color
            macropad.pixels.fill(key_color)
        # if a scale is selected, changing key_color would return lights to red depending on selected scale
            if majorState == True:  # if major scale is selected,
                major()             # return major keys to red
            elif minorState == True:
                minor()
            elif majorState == True:
                majorPenta()
            elif minorPentaState == True:
                minorPenta()
            elif bluesState == True:
                blues()
            elif dorianState == True:
                dorian()
            text_lines[0].text = ("Mode: %s %d" % (mode_text[mode], midi_values[mode]+1))

        if mode == 4 :  # Transpose
            midi_values[mode] = min(max(midi_values[mode] + knob_delta, 0), 96)
            text_lines[0].text = ("Mode: %s %d" % (mode_text[mode], midi_values[mode]-48))
            midi_notes = [midi_values[mode] + i for i in range(12)]

        if mode == 5 :  # Key
            midi_values[mode] = min(max(midi_values[mode] + knob_delta, 0), 11)
            key_names = ["A", "A#/Bb", "B", "C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab"]
            midi_notes_offsets = [45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56]
            
            text_lines[0].text = f"Choose Key: {key_names[midi_values[mode]]}"
            midi_notes = [midi_notes_offsets[midi_values[mode]] + i for i in range(12)]

        if mode == 6:   # Scale
            midi_values[mode] = min(max(midi_values[mode] + knob_delta, 0), 6)
            text_lines[1].text = ("Choose Scale")
        # "if" functions that turns off red lights from previous scales and turns off all scaleStates except the one selected
            if midi_values[mode] == 0: 
                text_lines[0].text = ("Chromatic Scale")
                majorState = False
                minorPentaState = False
                for i in range(12):
                    macropad.pixels[i] = key_color # set all pixels to key_color
            elif midi_values[mode] == 1:
                text_lines[0].text = ("Ionian Scale")
                majorState = True
                minorState = False
                majorPentaState = False
                minorPentaState = False
                bluesState = False
                dorianState = False
                reset()
                major()
            elif midi_values[mode] == 2:
                text_lines[0].text = ("Natural Minor Scale")
                majorState = False
                minorState = True
                majorPentaState = False
                minorPentaState = False
                bluesState = False
                dorianState = False
                reset()
                minor()
            elif midi_values[mode] == 2:
                text_lines[0].text = ("Major Pentatonic Scale")
                minorState = False
                majorState = False
                majorPentaState = True
                minorPentaState = False
                bluesState = False
                dorianState = False
                reset()
                majorPenta()
            elif midi_values[mode] == 3:
                text_lines[0].text = ("Minor Pentatonic Scale")
                majorState = False
                minorState = False
                majorPentaState = False
                minorPentaState = True
                bluesState = False
                dorianState = False
                reset()
                minorPenta()
            elif midi_values[mode] == 4:
                text_lines[0].text = ("Blues Scale")
                majorState = False
                minorState = False
                majorPentaState = False
                minorPentaState = False
                bluesState = True
                dorianState = False
                reset()
                blues()
            elif midi_values[mode] == 5:
                text_lines[0].text = ("Dorian Scale")
                majorState = False
                minorState = False
                majorPentaState = False
                minorPentaState = False
                bluesState = False
                dorianState = True
                reset()
                dorian()
            
        last_knob_pos = macropad.encoder   # records last/current knob position of rotary encoder

    macropad.display.refresh()  # refresh display
