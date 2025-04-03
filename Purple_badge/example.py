# Copyright (C) 2025 tymkrs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of tymkrs shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from tymkrs.

import machine
import rp2
import utime

############
# LED Driver

def led_init():
    i2c.writeto_mem(0x3C, 0x4F, b'\x00')     # reset all regs to power on defaults (see datasheet)
    i2c.writeto_mem(0x3C, 0x00, b'\x01')     # turn off global shutdown (bit 0 = 0 = shutdown 1 = normal operation)
    i2c.writeto_mem(0x3F, 0x4F, b'\x00')     # reset all regs to power on defaults (see datasheet)
    i2c.writeto_mem(0x3F, 0x00, b'\x01')     # turn off global shutdown (bit 0 = 0 = shutdown 1 = normal operation)
    
    # enable each and set current level of each channel to 1/4 power
    # b'\x01' = 1/1 | b'\x03' = 1/2 | b'\x05' = 1/3 | b'\x07' = 1/4
    for i in range(0,36):
        i2c.writeto_mem(0x3C, 0x26 + i, b'\x07')
        i2c.writeto_mem(0x3F, 0x26 + i, b'\x07')
        
    # latch / apply all changes to the outputs of the driver chips
    i2c.writeto_mem(0x3C, 0x25, b'\x00')
    i2c.writeto_mem(0x3F, 0x25, b'\x00')

def render():
    global buffer_60, buffer_63, raster
    
    # reorder the raster array into the buffer which will sent to the chip
    for i in range(0, 35):
        buffer_60[i] = raster[chip_60[i]]
        buffer_63[i] = raster[chip_63[i]]
    # send all of the values for the switch leds to the driver chips
    i2c.writeto_mem(60, 2, buffer_60)
    i2c.writeto_mem(63, 2, buffer_63)
    
    # send the values for the two ice blue leds to the driver chips
    global indicator_a, indicator_b
    i2c.writeto_mem(60, 1, indicator_a)
    i2c.writeto_mem(63, 1, indicator_b)
    
    # latch / apply all changes to the outputs of the driver chips
    i2c.writeto_mem(0x3C, 0x25, b'\x00')
    i2c.writeto_mem(0x3F, 0x25, b'\x00')

def raster_fill(value): # fill the whole raster with a value
    global raster
    temp = int(value / 4) # divide the value to change the range from 0-255 to 0-63
    for i in range(0, array_size):
        raster[i] = gama_64[temp] # use the gama correction lookup table to get the corrected value

def raster_set_at(x, y, value): # set the value of a specific pixel in the raster array
    global raster
    temp = int(value / 4) # divide the value to change the range from 0-255 to 0-63
    node_offset = get_node_offset(x, y) # convert the x, y coordinate into a linear offset
    raster[node_offset] = gama_64[temp] # use the gama correction lookup table to get the corrected value

##################
# UI Event Handler

def handle_events(): # scan the switch matrix
    for x in range(0, 7):
        utime.sleep(bounceDelay)
        # select line
        if x == 0:
            row7.value(1) # deselect last row
            row1.value(0) # select this row
        elif x == 1:
            row1.value(1) # deselect last row
            row2.value(0) # select this row 
        elif x == 2:
            row2.value(1) # deselect last row
            row3.value(0) # select this row 
        elif x == 3:
            row3.value(1) # deselect last row
            row4.value(0) # select this row 
        elif x == 4:
            row4.value(1) # deselect last row
            row5.value(0) # select this row 
        elif x == 5:
            row5.value(1) # deselect last row
            row6.value(0) # select this row 
        elif x == 6:
            row6.value(1) # deselect last row
            row7.value(0) # select this row 
        # get button states
        if(col1.value() == 0):
            button_states_new[x][0] = 1
            #print("R",buttonRow,"C1", sep="")
        else:
            button_states_new[x][0] = 0
        if(col2.value() == 0):
            button_states_new[x][1] = 1
            #print("R",buttonRow,"C2", sep="")
        else:
            button_states_new[x][1] = 0
        if(col3.value() == 0):
            button_states_new[x][2] = 1
            #print("R",buttonRow,"C3", sep="")
        else:
            button_states_new[x][2] = 0
        if(col4.value() == 0):
            button_states_new[x][3] = 1
            #print("R",buttonRow,"C4", sep="")
        else:
            button_states_new[x][3] = 0
        if(col5.value() == 0):
            button_states_new[x][4] = 1
            #print("R",buttonRow,"C5", sep="")
        else:
            button_states_new[x][4] = 0
        if(col6.value() == 0):
            button_states_new[x][5] = 1
            #print("R",buttonRow,"C6", sep="")
        else:
            button_states_new[x][5] = 0
        if(col7.value() == 0):
            button_states_new[x][6] = 1
            #print("R",buttonRow,"C7", sep="")
        else:
            button_states_new[x][6] = 0
        if(col8.value() == 0):
            button_states_new[x][7] = 1
            #print("R",buttonRow,"C8", sep="")
        else:
            button_states_new[x][7] = 0
        if(col9.value() == 0):
            button_states_new[x][8] = 1
            #print("R",buttonRow,"C9", sep="")
        else:
            button_states_new[x][8] = 0
        if(col10.value() == 0):
            button_states_new[x][9] = 1
            #print("R",buttonRow,"C10", sep="")
        else:
            button_states_new[x][9] = 0
    # copy button states to game engine / fire events
    get_button_states()
    
def get_button_states(): # check for any new changes in the state of the switches
    global button_x, button_y, button_states_old
    for i in range(0, array_size):
        x, y = get_node_coords(i)
        if button_states_new[x][y] != button_states_old[x][y]:
            button_states_old[x][y] = button_states_new[x][y]
            if button_states_new[x][y] != node_switch_state[i]:
                button_x = x
                button_y = y
                if button_states_new[button_x][button_y] == 0:
                    left_click_up_event(button_x, button_y)
                else:
                    left_click_down_event(button_x, button_y)

def left_click_down_event(x, y): # copy the event to the switch state array
    global node_switch_state
    node_switch_state[get_node_offset(x, y)] = 1

def left_click_up_event(x, y): # copy the event to the switch state array
    global node_switch_state
    node_switch_state[get_node_offset(x, y)] = 0

############################
# Memory Interface Functions

def get_node_offset(x, y): # convert from a 2D offset to a 1D offset
    global field_width
    return (y * field_width) + x

def get_node_coords(index): # convert from a 1D offset to a 2D offset
    global field_width
    y = int(index / field_width)
    x = index - (y * field_width)
    return x, y

############################################
# Entry Point / Global Variables / Main Loop

# Rendering Engine Global Variables

field_width =			7
field_height =			10
array_size =			field_width * field_height

raster =				bytearray(array_size)

chip_60 = 				[66, 59, 52, 45, 38, 65, 58, 51, 44, 37, 30, 23, 16, 9, 2, 64, 57, 50, 43, 36, 29, 22, 15, 8, 1, 63, 56, 49, 42, 35, 28, 21, 14, 7, 0]
chip_63 = 				[6, 13, 20, 27, 34, 41, 48, 55, 62, 69, 5, 12, 19, 26, 33, 40, 47, 54, 61, 68, 4, 11, 18, 25, 32, 39, 46, 53, 60, 67, 3, 10, 17, 24, 31]

buffer_60 = 			bytearray(35)
buffer_63 = 			bytearray(35)

gama_64 =				[0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 29, 32, 35, 38, 41, 44, 47, 50, 53, 57, 61, 65, 69, 73, 77, 81, 85, 89, 94, 99, 104, 109, 114, 119, 124, 129, 134, 140, 146, 152, 158, 164, 170, 176, 182, 188, 195, 202, 209, 216, 223, 230, 237, 244, 251, 255]

gama_32 = 				[0, 1, 2, 4, 6, 10, 13, 18, 22, 28, 33, 39, 46, 53, 61, 69, 78, 86, 96, 106, 116, 126, 138, 149, 161, 173, 186, 199, 212, 226, 240, 255]
gama_16 =				[0, 2, 6, 13, 22, 33, 46, 61, 78, 96, 116, 138, 161, 186, 212, 240]
addrMap = 				[[0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C],[0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C],[0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C],[0x3F,0x3F,0x3F,0x3F,0x3F,0x3C,0x3C,0x3C,0x3C,0x3C],[0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F],[0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F],[0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F]]
LEDmap = 				[[36,35,34,33,32,31,30,29,28,27],[26,25,24,23,22,21,20,19,18,17],[16,15,14,13,12,11,10,9,8,7],[32,33,34,35,36,6,5,4,3,2],[22,23,24,25,26,27,28,29,30,31],[12,13,14,15,16,17,18,19,20,21],[2,3,4,5,6,7,8,9,10,11]]

indicator_a =			bytearray(1)
indicator_b =			bytearray(1)
indicator_a[0] =		0
indicator_b[0] =		69

# UI Global Variables

button_x =				0
button_y =				0

node_switch_state =		bytearray(array_size)

bounceDelay = 			0.001

button_states_new =		[[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]]
button_states_old =		[[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]]

row1 =					machine.Pin(2, machine.Pin.OUT, value=1)
row2 =					machine.Pin(3, machine.Pin.OUT, value=1)
row3 =					machine.Pin(4, machine.Pin.OUT, value=1)
col10 =					machine.Pin(5, machine.Pin.IN)
col8 =					machine.Pin(6, machine.Pin.IN)
col6 =					machine.Pin(7, machine.Pin.IN)
col4 =					machine.Pin(8, machine.Pin.IN)
col3 =					machine.Pin(9, machine.Pin.IN)
col2 =					machine.Pin(10, machine.Pin.IN)
col1 =					machine.Pin(11, machine.Pin.IN)
row5 =					machine.Pin(12, machine.Pin.OUT, value=1)
row6 =					machine.Pin(13, machine.Pin.OUT, value=1)
row7 =					machine.Pin(14, machine.Pin.OUT, value=1)
row4 =					machine.Pin(22, machine.Pin.OUT, value=1)
led =					machine.Pin(25, machine.Pin.OUT)
col5 =					machine.Pin(26, machine.Pin.IN)
col7 =					machine.Pin(27, machine.Pin.IN)
col9 =					machine.Pin(28, machine.Pin.IN)

# Bouncing Ball Demo Global Variables

velocity_a =			69
velocity_b =			-7

x_position =			0
y_position =			0

x_modifier =			1
y_modifier =			1

# set up and start the led chips
i2c = 					machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0), freq=100000)
led_init()

# main loop
while True:

    handle_events()
    
    # check for and handle any new switch presses
    for node_index in range(0, array_size):
        if node_switch_state[node_index] == 1: # if this switch is pressed
            node_switch_state[node_index] = 0 # unpress it
            
            raster[get_node_offset(x_position, y_position)] = 0 # turn off led at old ball position
            
            x_position, y_position = get_node_coords(node_index) # move ball position to this switch position
            
            # fix ball direction to not point off the edge of the screen
            if x_position == 0:
                x_modifier = 1
            if x_position == field_width - 1:
                x_modifier = -1
            if y_position == 0:
                y_modifier = 1
            if y_position == field_height - 1:
                y_modifier = -1
    
    # apply the ball direction to the ball position
    x_position = x_position + x_modifier
    y_position = y_position + y_modifier
    
    # reverse the ball direction if at an edge
    if x_position >= (field_width - 1) or x_position <= 0:
        x_modifier = x_modifier * -1
    if y_position >= (field_height - 1) or y_position <= 0:
        y_modifier = y_modifier * -1
        
    # fully turn on the led at the ball position
    raster[get_node_offset(x_position, y_position)] = 255
    
    # turn down the brightness of all of the switch leds
    for node_index in range(0, array_size):
        if raster[node_index] > 15:
            raster[node_index] = raster[node_index] - 16
        elif raster[node_index] > 0:
            raster[node_index] = raster[node_index] - 1
    
    # add sparkles to the screen based on the state of the ice blue leds
    #for i in range(0, indicator_b[0]):
    #    raster[indicator_a[0] % array_size] = raster[indicator_a[0] % array_size] + 1
    
    # apply the modifiers to the ice blue leds
    indicator_a[0] = indicator_a[0] + velocity_a
    indicator_b[0] = indicator_b[0] + velocity_b
    
    # apply any changes to the raster to the button leds
    # and the new brightness values to the ice blue leds
    render()
    
    # limit the frame rate of the demo
    utime.sleep(.03)
    
    
    
    