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
import _thread
import gc

def core1_thread():
    gc.collect()
    global flip, current_change, current_level
    while True:
        handle_events()
        if flip == True:
            render()
            flip = False
        if current_change == True:
            led_current(current_level)
            current_change = False

def led_init():
    i2c.writeto_mem(0x3C, 0x4F, b'\x00')
    i2c.writeto_mem(0x3C, 0x00, b'\x01')
    i2c.writeto_mem(0x3F, 0x4F, b'\x00')
    i2c.writeto_mem(0x3F, 0x00, b'\x01')
    for i in range(0,36):
        i2c.writeto_mem(0x3C, 0x26 + i, b'\x07')
        i2c.writeto_mem(0x3F, 0x26 + i, b'\x07')
    i2c.writeto_mem(0x3C, 0x25, b'\x00')
    i2c.writeto_mem(0x3F, 0x25, b'\x00')
    
def led_current(level):
    if level == 0:
        for i in range(0,36):
            i2c.writeto_mem(0x3C, 0x26 + i, b'\x07')
            i2c.writeto_mem(0x3F, 0x26 + i, b'\x07')
    elif level == 1:
        for i in range(0,36):
            i2c.writeto_mem(0x3C, 0x26 + i, b'\x05')
            i2c.writeto_mem(0x3F, 0x26 + i, b'\x05')
    elif level == 2:
        for i in range(0,36):
            i2c.writeto_mem(0x3C, 0x26 + i, b'\x03')
            i2c.writeto_mem(0x3F, 0x26 + i, b'\x03')
    elif level == 3:
        for i in range(0,36):
            i2c.writeto_mem(0x3C, 0x26 + i, b'\x01')
            i2c.writeto_mem(0x3F, 0x26 + i, b'\x01')
    i2c.writeto_mem(0x3C, 0x25, b'\x00')
    i2c.writeto_mem(0x3F, 0x25, b'\x00')

def render():
    global buffer_60, buffer_63, overscan        
    for i in range(0, 35):
        buffer_60[i] = overscan[chip_60[i]]
        buffer_63[i] = overscan[chip_63[i]]
    i2c.writeto_mem(60, 2, buffer_60)
    i2c.writeto_mem(63, 2, buffer_63)
    i2c.writeto_mem(0x3C, 0x25, b'\x00')
    i2c.writeto_mem(0x3F, 0x25, b'\x00')

def overscan_fill(value):
    global overscan
    temp = int(value / 4)
    for i in range(0, array_size):
        overscan[i] = gama_64[temp]

def overscan_set_at(x, y, value):
    global overscan
    temp = int(value / 4)
    node_offset = get_node_offset(x, y)
    overscan[node_offset] = gama_64[temp]

def draw():
    global button_x, button_y
    global node_value, node_deform, node_rendered, node_lock, node_counter
    global game_level
    global field_width, field_height
    if game_level == 0:
        overscan_fill(0)
        for y in range(0, field_height):
            for x in range(0, field_width):
                node_offset = get_node_offset(x, y)
                button_offset = get_node_offset(button_x, button_y)
                multiplier = int(node_counter[button_offset] / 4)
                if multiplier == 0: multiplier = 1
                temp_value = node_value[node_offset] - (node_deform[node_offset] * multiplier)
                if temp_value < 0: temp_value = 0
                node_rendered[node_offset] = temp_value
                if node_lock[node_offset] == 0:
                    overscan_set_at(x, y, temp_value)
                else:
                    overscan_set_at(x, y, 0)
    if game_level == 1 or game_level == 2 or game_level == 3 or game_level == 7 or game_level == 8 or game_level == 9 or game_level == 10 or game_level == 11 or game_level == 12 or game_level == 13 or game_level == 14:
        overscan_fill(0)
        for y in range(0, field_height):
            for x in range(0, field_width):
                node_offset = get_node_offset(x, y)
                temp_value = node_value[node_offset]
                overscan_set_at(x, y, temp_value)
    if game_level == 4:
        overscan_fill(0)
        for y in range(0, field_height):
            for x in range(0, field_width):
                node_offset = get_node_offset(x, y)
                temp_value = node_value[node_offset]
                overscan_set_at(x, y, temp_value)
    if game_level == 5:
        overscan_fill(0)
        for index in range(0, field_width):
            if node_counter[index] == 1:
                x, y = get_node_coords(node_deform[index])
                overscan_set_at(x, y, 255)
            if node_counter[index] == 2:
                x, y = get_node_coords(node_deform[index])
                overscan_set_at(x, y, 128)
    if game_level == 6:
        overscan_fill(0)
        for y in range(0, field_height):
            for x in range(0, field_width):
                node_offset = get_node_offset(x, y)
                temp_value = node_value[node_offset]
                overscan_set_at(x, y, temp_value)
        for x in range(0, field_width):
            for y in range(0, field_height):
                node_offset = get_node_offset(x, y)
                temp_value = node_value[node_offset]
                if temp_value == 255:
                    temp_delta = 2
                    for yo in range(0, 8):
                        temp_tamp = int(256 / temp_delta)
                        if temp_tamp < 14: temp_tamp = 0
                        temp_delta = temp_delta + 4
                        target_y = y - yo - 1
                        if target_y < 0:
                            target_y = target_y + field_height
                        overscan_set_at(x, target_y, temp_tamp)

def handle_events():
    for x in range(0, 7):
        utime.sleep(bounceDelay)
        if x == 0:
            row7.value(1)
            row1.value(0)
        elif x == 1:
            row1.value(1)
            row2.value(0)
        elif x == 2:
            row2.value(1)
            row3.value(0)
        elif x == 3:
            row3.value(1)
            row4.value(0)
        elif x == 4:
            row4.value(1)
            row5.value(0)
        elif x == 5:
            row5.value(1)
            row6.value(0)
        elif x == 6:
            row6.value(1)
            row7.value(0)
        if(col1.value() == 0):
            coreXfer_buttonStates[x][0] = 1
        else:
            coreXfer_buttonStates[x][0] = 0
        if(col2.value() == 0):
            coreXfer_buttonStates[x][1] = 1
        else:
            coreXfer_buttonStates[x][1] = 0
        if(col3.value() == 0):
            coreXfer_buttonStates[x][2] = 1
        else:
            coreXfer_buttonStates[x][2] = 0
        if(col4.value() == 0):
            coreXfer_buttonStates[x][3] = 1
        else:
            coreXfer_buttonStates[x][3] = 0
        if(col5.value() == 0):
            coreXfer_buttonStates[x][4] = 1
        else:
            coreXfer_buttonStates[x][4] = 0
        if(col6.value() == 0):
            coreXfer_buttonStates[x][5] = 1
        else:
            coreXfer_buttonStates[x][5] = 0
        if(col7.value() == 0):
            coreXfer_buttonStates[x][6] = 1
        else:
            coreXfer_buttonStates[x][6] = 0
        if(col8.value() == 0):
            coreXfer_buttonStates[x][7] = 1
        else:
            coreXfer_buttonStates[x][7] = 0
        if(col9.value() == 0):
            coreXfer_buttonStates[x][8] = 1
        else:
            coreXfer_buttonStates[x][8] = 0
        if(col10.value() == 0):
            coreXfer_buttonStates[x][9] = 1
        else:
            coreXfer_buttonStates[x][9] = 0
    get_button_states()
    
def get_button_states():
    global button_x, button_y, coreXfer_buttonStates_old
    for i in range(0, array_size):
        x, y = get_node_coords(i)
        if coreXfer_buttonStates[x][y] != coreXfer_buttonStates_old[x][y]:
            coreXfer_buttonStates_old[x][y] = coreXfer_buttonStates[x][y]
            
            if coreXfer_buttonStates[x][y] != node_switch_state[i]:
                button_x = x
                button_y = y
                if coreXfer_buttonStates[button_x][button_y] == 0:
                    left_click_up_event(button_x, button_y)
                else:
                    left_click_down_event(button_x, button_y)

def left_click_down_event(x, y):
    global node_switch_state
    node_switch_state[get_node_offset(x, y)] = 1
    if get_node_offset(x, y) == 0:
        global hud_pressed
        hud_pressed = 1

def left_click_up_event(x, y):
    global node_switch_state
    node_switch_state[get_node_offset(x, y)] = 0
    if get_node_offset(x, y) == 0:
        global hud_pressed
        hud_pressed = 0

def get_node_offset(x, y):
    global field_width
    return (y * field_width) + x

def get_node_coords(index):
    global field_width
    y = int(index / field_width)
    x = index - (y * field_width)
    return x, y

def randrange(zero, modulo):
    global ant_random
    step_level_minus_3()
    if modulo == 0: modulo = 1
    return ant_random % modulo

def level_init(level):
    global node_counter, node_switch_state, node_lock, node_velocity, node_value, node_deform
    global button_x, button_y
    global game_level, array_size, game_timeout
    global field_width, field_height
    for node_index in range(0, array_size):
        node_counter[node_index] = 0
        node_switch_state[node_index] = 0
        node_lock[node_index] = 0
        node_velocity[node_index] = 0
        node_value[node_index] = 0
        node_deform[node_index] = 0
    button_x = 0
    button_y = 0
    game_timeout = 0
    if level == -3:
        global ant_rotation, ant_position
        ant_position = (7 * 5) + 4
        ant_rotation = 0
    if level == 0:
        for node_index in range(0, array_size):
            node_value[node_index] = 0
            node_velocity[node_index] = 128 # 0 right, 1 down, 2 left, 3 up
    if level == 1:
        global sub_level_1, column_level_1, left_level_1, right_level_1
        sub_level_1 = 0
        column_level_1 = 0
        left_level_1 = 0
        right_level_1 = 0
    if level == 2:
        global node_level_2
        node_level_2 = array_size
        for node_index in range(0, array_size):
            node_value[node_index] = 64
    if level == 3:
        global node_1_level_3, node_2_level_3, node_3_level_3, node_4_level_3
        node_1_level_3 = array_size
        node_2_level_3 = array_size
        node_3_level_3 = array_size
        node_4_level_3 = array_size
    if level == 4:
        for node_index in range(0, array_size):
            node_counter[node_index] = 7
            node_velocity[node_index] = 1
    if level == 5:
        global started_level_5
        started_level_5 = 0
    if level == 6:
        for xo in range(0, field_width):
            yo = randrange(0, field_height)
            node_value[get_node_offset(xo, yo)] = 255
    if level == 7:
        node_counter[0] = 128
        for node_index in range(0, 6):
            node_lock[node_index] = randrange(0, array_size)
            node_value[node_lock[node_index]] = 128
    if level == 8:
        yo = 0
        for xo in range(0, field_width):
            node_counter[get_node_offset(xo, yo)] = 1
    if level == 9:
        for node_index in range(0, array_size):
            node_deform[node_index] = array_size
        node_deform[0] = randrange(0, array_size)
        node_counter[0] = array_size - 1
        node_counter[1] = array_size
    if level == 10:
        pass
    if level == 11:
        for node_index in range(0, array_size):
            temp_random = randrange(0, 4)
            if temp_random == 0:
                node_velocity[node_index] = 8
            elif temp_random == 1:
                node_velocity[node_index] = 6
            elif temp_random == 2:
                node_velocity[node_index] = 2
            elif temp_random == 3:
                node_velocity[node_index] = 4
            node_counter[node_index] = node_index
            node_value[node_index] = 8
    if level == 12:
        node_deform[0] = randrange(0, array_size)
        node_deform[1] = 64
        node_deform[2] = 128
    if level == 13:
        node_index = 0
        node_deform[node_index] = randrange(0, array_size)
        for node_index in range(1, array_size):
            finished = False
            while finished == False:
                temp_value = randrange(0, array_size)
                check = True
                for node_offset in range(0, node_index):
                    if node_deform[node_offset] == temp_value:
                        check = False
                if check == True:
                    node_deform[node_index] = temp_value
                    finished = True
        node_velocity[0] = 0
    game_level = level

def step():
    global game_level
    if game_level == -3:
        step_level_minus_3()
        return
    if game_level == 0:
        step_level_0()
        return
    if game_level == 1:
        if game_timeout_check() == True:
            level_init(0)
            return
        else:
            step_level_1()
            return
    if game_level == 2:
        if game_timeout_check() == True:
            level_init(1)
            return
        else:
            step_level_2()
            return
    if game_level == 3:
        if game_timeout_check() == True:
            level_init(2)
            return
        else:
            step_level_3()
            return
    if game_level == 4:
        if game_timeout_check() == True:
            level_init(3)
            return
        else:
            step_level_4()
            return
    if game_level == 5:
        if game_timeout_check() == True:
            level_init(4)
            return
        else:
            step_level_5()
            return
    if game_level == 6:
        if game_timeout_check() == True:
            level_init(5)
            return
        else:
            step_level_6()
            return
    if game_level == 7:
        if game_timeout_check() == True:
            level_init(6)
            return
        else:
            step_level_7()
            return    
    if game_level == 8:
        if game_timeout_check() == True:
            level_init(7)
            return
        else:
            step_level_8()
            return
    if game_level == 9:
        if game_timeout_check() == True:
            level_init(8)
            return
        else:
            step_level_9()
            return
    if game_level == 10:
        if game_timeout_check() == True:
            level_init(9)
            return
        else:
            step_level_10()
            return    
    if game_level == 11:
        if game_timeout_check() == True:
            level_init(10)
            return
        else:
            step_level_11()
            return
    if game_level == 12:
        if game_timeout_check() == True:
            level_init(11)
            return
        else:
            step_level_12()
            return
    if game_level == 13:
        if game_timeout_check() == True:
            level_init(12)
            return
        else:
            step_level_13()
            return
    if game_level == 14:
        step_level_14()
        return

def game_timeout_check():
    global game_level, game_timeout, game_timed
    if game_timed == True:
        game_timeout = game_timeout + 1
        if game_timeout >= 1000:
            return True
        else:
            return False

def step_level_minus_3():
    global ant_position, ant_rotation, ant_count, ant_random, ant_value
    global node_value, field_width, field_height, array_size
    rotation = ant_rotation
    if ant_value[ant_position] == 255:
        ant_value[ant_position] = 0
        rotation = rotation + 1
        if rotation > 3: rotation = 0
    if ant_value[ant_rotation] == 0:
        ant_value[ant_position] = 255
        rotation = rotation - 1
        if rotation < 0: rotation = 3
    ant_rotation = rotation
    x, y = get_node_coords(ant_position)
    if ant_rotation == 0: x = x + 1
    if ant_rotation == 1: y = y + 1
    if ant_rotation == 2: x = x - 1
    if ant_rotation == 3: y = y - 1
    if x >= field_width:
        x = 0
        y = y - 1
    if y < 0: y = field_height - 1
    if y >= field_height:
        y = 0
        x = x - y
    if x < 0: x = field_width - 1
    ant_position = get_node_offset(x, y)
    ant_count = ant_count + 1
    last_random = ant_random
    ant_random = 0
    temp_random = [0] * field_height
    for yo in range(0, field_height):
        temp_value = 0
        for xo in range(0, field_width):
            if ant_value[get_node_offset(xo, yo)] == 255:
                temp_value = temp_value + (1 << xo)
        temp_random[yo] = temp_value
    for yo in range(0, field_height):
        ant_random = ant_random + temp_random[yo]
    for yo in range(0, field_height):
        ant_random = ant_random + (temp_random[yo] << (ant_count % 8))
    ant_random = ant_random ^ ant_count
    if last_random > 0:
        ant_random = ant_random ^ last_random

def step_level_0():
    global node_value, node_velocity, node_deform, node_lock, array_size
    pressed = False
    for node_index in range(0, array_size):
        if node_switch_state[node_index] == 1:
            node_value[node_index] = 0
            node_lock[node_index] = 255
            pressed = True
    if pressed == True:
        if node_deform[0] < 255:
            node_deform[0] = node_deform[0] + 1
        if node_deform[0] > 0:
            finished = True
            for node_index in range(0, array_size):
                if node_value[node_index] > 0:
                    finished = False
                    temp_value = node_value[node_index]
                    temp_value = temp_value - node_deform[0]
                    if temp_value < 0:
                        temp_value = 0
                    node_value[node_index] = temp_value
        if finished == True:
            level_init(1)
    else:
        if node_deform[0] > 0:
            node_deform[0] = node_deform[0] - 1
        if node_value[0] > 127:
            for node_index in range(0, array_size):
                temp_value = node_value[node_index]
                temp_value = temp_value + 32
                if temp_value > 255:
                    temp_value = 255
                node_value[node_index] = temp_value
        elif node_value[0] < 128:
            for node_index in range(0, array_size):
                temp_value = node_value[node_index]
                temp_value = temp_value - 32
                if temp_value < 0:
                    temp_value = 0
                node_value[node_index] = temp_value
        for node_index in range(0, array_size):
            temp_value = node_velocity[node_index]
            temp_random = randrange(0, 3)
            if temp_random == 0:
                temp_value = temp_value + 1
            elif temp_random == 1:
                temp_value = temp_value - 1
            else:
                pass
            if temp_value > 130:
                temp_value = 130
            if temp_value < 125:
                temp_value = 125
            node_velocity[node_index] = temp_value
            temp_value = node_value[node_index]
            if node_velocity[node_index] > 127:
                if node_lock[node_index] == 0:
                    temp_value = temp_value + 64
                else:
                    node_lock[node_index] = node_lock[node_index] - 1
            else:
                temp_value = temp_value - 64
            if temp_value > 255:
                temp_value = 255
            if temp_value < 0:
                temp_value = 0
            node_value[node_index] = temp_value

def step_level_1():
    global game_timeout
    global sub_level_1, column_level_1, left_level_1, right_level_1, first_node_level_1, node_value
    global array_size
    global field_width, field_height
    if sub_level_1 == 0:
        for node_index in range(0, array_size):
            if node_switch_state[node_index] == 1:
                game_timeout = 0
                column_level_1 = button_x
                first_node_level_1 = node_index
                sub_level_1 = 1
                return
    if sub_level_1 == 1:
        for yo in range(0, field_height):
            node_index = get_node_offset(column_level_1, yo)
            node_value[node_index] = 255
        sub_level_1 = 2
        return
    if sub_level_1 == 2:
        if node_switch_state[first_node_level_1] == 0:
            for yo in range(0, field_height):
                node_index = get_node_offset(column_level_1, yo)
                node_value[node_index] = 0
            sub_level_1 = 0
            return
        if column_level_1 == (field_width - 1) or column_level_1 == 0: return
        left_level_1 = 0
        right_level_1 = 0
        for xo in range(0, column_level_1):
            for yo in range(0, field_height):
                if node_switch_state[get_node_offset(xo, yo)] == 1: # press in left area
                    game_timeout = 0
                    left_level_1 = 1
        for xo in range(column_level_1 + 1, field_width):
            for yo in range(0, field_height):
                if node_switch_state[get_node_offset(xo, yo)] == 1: # press in right area
                    game_timeout = 0
                    right_level_1 = 1
        fill_level_1()
        if left_level_1 == 1 and right_level_1 == 1: # switch to next level
            level_init(2)
            return

def fill_level_1():
    global node_value, column_level_1, left_level_1, right_level_1
    global field_width, field_height
    if column_level_1 == (field_width - 1) or column_level_1 == 0: return
    if left_level_1 == 1:
        for xo in range(0, column_level_1):
            for yo in range(0, field_height):
                node_index = get_node_offset(xo, yo)
                node_value[node_index] = 255
    else:
        for xo in range(0, column_level_1):
            for yo in range(0, field_height):
                node_index = get_node_offset(xo, yo)
                node_value[node_index] = 0
    if right_level_1 == 1:
        for xo in range(column_level_1 + 1, field_width):
            for yo in range(0, field_height):
                node_index = get_node_offset(xo, yo)
                node_value[node_index] = 255
    else:
        for xo in range(column_level_1 + 1, field_width):
            for yo in range(0, field_height):
                node_index = get_node_offset(xo, yo)
                node_value[node_index] = 0

def step_level_2():
    global game_timeout
    global node_level_2, node_value, node_velocity, node_switch_state
    global array_size
    finished = True
    for node_index in range(0, array_size):
        if node_value[node_index] > 0:
            finished = False
    if finished == True:
        level_init(3)
        return
    if node_level_2 == array_size:
        temp_random = randrange(0, array_size)
        if node_value[temp_random] == 64:
            node_level_2 = temp_random
        return
    else:
        if node_value[node_level_2] == 64:
            node_velocity[node_level_2] = 131
            node_value[node_level_2] = 65
            return
        if node_value[node_level_2] == 255:
            node_velocity[node_level_2] = 125
            node_value[node_level_2] = 254
            return
        if node_velocity[node_level_2] == 125 and node_value[node_level_2] == 65:
            node_value[node_level_2] = 64
            node_level_2 = array_size
            return
        temp_velocity = node_velocity[node_level_2] - 128
        temp_value = node_value[node_level_2]
        temp_value = temp_value + temp_velocity
        if temp_value < 64: temp_value = 64
        if temp_value > 255: temp_value = 255
        node_value[node_level_2] = temp_value
        if node_switch_state[node_level_2] == 1:
            game_timeout = 0
            if node_value[node_level_2] > 64:
                node_value[node_level_2] = 0
                node_level_2 = array_size

def step_level_3():
    global game_timeout
    global node_1_level_3, node_2_level_3, node_3_level_3, node_4_level_3
    global node_value, node_switch_state
    global array_size
    if node_1_level_3 != array_size:
        if node_switch_state[node_1_level_3] == 0:
            node_value[node_1_level_3] = 0
            node_1_level_3 = array_size
            if node_2_level_3 != array_size:
                node_value[node_2_level_3] = 0
                node_2_level_3 = array_size
            if node_3_level_3 != array_size:
                node_value[node_3_level_3] = 0
                node_3_level_3 = array_size
            return
    if node_2_level_3 != array_size:
        if node_switch_state[node_2_level_3] == 0:
            node_value[node_2_level_3] = 0
            node_2_level_3 = array_size
            if node_1_level_3 != array_size:
                node_value[node_1_level_3] = 0
                node_1_level_3 = array_size
            if node_3_level_3 != array_size:
                node_value[node_3_level_3] = 0
                node_3_level_3 = array_size
            return
    if node_3_level_3 != array_size:
        if node_switch_state[node_3_level_3] == 0:
            node_value[node_3_level_3] = 0
            node_3_level_3 = array_size
            if node_1_level_3 != array_size:
                node_value[node_1_level_3] = 0
                node_1_level_3 = array_size
            if node_2_level_3 != array_size:
                node_value[node_2_level_3] = 0
                node_2_level_3 = array_size
            return
    if node_1_level_3 == array_size:
        for node_index in range(0, array_size):
            if node_switch_state[node_index] == 1:
                game_timeout = 0
                node_1_level_3 = node_index
                node_value[node_1_level_3] = 64
                return
    if node_2_level_3 == array_size:
        for node_index in range(0, array_size):
            if node_index != node_1_level_3:
                if node_switch_state[node_index] == 1:
                    game_timeout = 0
                    x1, y1 = get_node_coords(node_1_level_3)
                    x2, y2 = get_node_coords(node_index)
                    if x1 == x2 and y2 < y1:
                        node_2_level_3 = node_index
                        if node_1_level_3 < array_size:
                            node_value[node_1_level_3] = 128
                        node_value[node_2_level_3] = 64
                        return
    if node_3_level_3 == array_size:
        for node_index in range(0, array_size):
            if node_index != node_1_level_3 and node_index != node_2_level_3:
                if node_switch_state[node_index] == 1:
                    game_timeout = 0
                    x1, y1 = get_node_coords(node_2_level_3)
                    x2, y2 = get_node_coords(node_index)
                    if y1 == y2 and x2 > x1:
                        node_3_level_3 = node_index
                        node_value[node_1_level_3] = 192
                        node_value[node_2_level_3] = 128
                        node_value[node_3_level_3] = 64
                        return
    if node_4_level_3 == array_size:
        for node_index in range(0, array_size):
            if node_index != node_1_level_3 and node_index != node_2_level_3 and node_index != node_3_level_3:
                if node_switch_state[node_index] == 1:
                    game_timeout = 0
                    x1, y1 = get_node_coords(node_3_level_3)
                    x2, y2 = get_node_coords(node_index)
                    x3, y3 = get_node_coords(node_1_level_3)
                    if x1 == x2 and y2 > y1:
                        if y2 == y3:
                            node_4_level_3 = node_index
                            node_value[node_1_level_3] = 255
                            node_value[node_2_level_3] = 255
                            node_value[node_3_level_3] = 255
                            level_init(4)
                            return

def step_level_4():
    global game_timeout
    global array_size, node_value, node_switch_state, node_lock, node_counter, node_velocity, node_deform
    for node_index in range(0, array_size):
        click = False
        if node_switch_state[node_index] == 1:
            game_timeout = 0
            click = True
            node_switch_state[node_index] = 0
            temp_value = node_lock[node_index]
            temp_value = temp_value + 1
            if temp_value > 7:
                temp_value = 7
            node_lock[node_index] = temp_value
            if node_lock[node_index] == 1:
                node_velocity[node_index] = 2
        temp_target = 7 + (node_lock[node_index] * (node_velocity[node_index] - 1))
        temp_value = node_counter[node_index]
        temp_value = temp_value + (node_velocity[node_index] - 1)
        if (node_velocity[node_index] - 1) == 1:
            if temp_value < temp_target:
                temp_value = temp_value + 1
            else:
                node_velocity[node_index] = 0
        elif (node_velocity[node_index] - 1) == -1:
            if temp_value > temp_target:
                temp_value = temp_value - 1
            else:
                node_velocity[node_index] = 2
        node_counter[node_index] = temp_value
        temp_value = gama_16[node_counter[node_index]]
        if temp_value == 0:
            level_init(5)
            return
        else:
            node_value[node_index] = temp_value

def step_level_4_average(index):
    global node_value, field_width, field_height
    x, y = get_node_coords(index)
    osum = 0
    for oy in range(y - 1, y + 2):
        for ox in range(x - 1, x + 2):
            if oy < 0 or oy > (field_height - 1) or ox < 0 or ox > (field_width - 1):
                oval = 128
            else:
                if oy == y and ox == x:
                    oval = 0
                else:
                    oval = node_value[get_node_offset(ox, oy)]
            osum = osum + oval
    omean = int(osum / 8)
    return omean

def step_level_5():
    global game_timeout
    global started_level_5, array_size, node_switch_state, field_width, node_deform, field_height, node_counter
    if started_level_5 == 0:
        for node_index in range(0, array_size):
            if node_switch_state[node_index] == 1:
                game_timeout = 0
                started_level_5 = 1
                for index in range(0, field_width):
                    node_deform[index] = node_index
                    node_counter[index] = 1
    if started_level_5 == 1:
        finished = True
        for node_index in range(0, array_size):
            if node_switch_state[node_index] == 1:
                game_timeout = 0
                finished = False
        if finished == True:
            started_level_5 = 2
    if started_level_5 == 2:
        for index in range(0, field_width):
            node_index = node_deform[index]
            if node_counter[index] == 1:
                if node_switch_state[node_index] == 1:
                    game_timeout = 0
                    node_counter[index] = 2
        for index in range(0, field_width):
            if node_counter[index] == 1:
                bx, by = get_node_coords(node_deform[index])
                if randrange(0, 64) == 0: bx = bx + 1
                if randrange(0, 64) == 0: bx = bx - 1
                if randrange(0, 64) == 0: by = by + 1
                if randrange(0, 64) == 0: by = by - 1
                if bx >= field_width: bx = field_width - 1
                if bx < 0: bx = 0
                if by >= field_height: by = field_height - 1
                if by < 0: by = 0
                node_deform[index] = get_node_offset(bx, by)
        for index in range(0, field_width):
            if node_counter[index] == 2:
                for node_index in range(0, field_width):
                    if node_index != index:
                        if node_counter[node_index] == 1:
                            if node_deform[node_index] == node_deform[index]:
                                node_counter[index] = 1
        finished = True
        for index in range(0, field_width):
            if node_counter[index] != 2:
                finished = False
        if finished == True:
            level_init(6)
            return

def step_level_6():
    global game_timeout
    global node_value, node_switch_state, array_size, field_height, array_size
    for node_index in range(0, array_size):
        if node_switch_state[node_index] == 1:
            game_timeout = 0
            if node_value[node_index] == 255:
                node_value[node_index] = 0
    finished = True
    for node_index in range(0, array_size):
        if node_value[node_index] == 255:
            finished = False
    if finished == True:
        level_init(7)
        return
    for node_index in range(array_size - 1, -1, -1):
        if node_value[node_index] == 255:
            if randrange(0, 12) == 0:
                node_value[node_index] = 0
                ox, oy = get_node_coords(node_index)
                oy = oy + 1
                if oy == field_height:
                    oy = 0
                node_value[get_node_offset(ox, oy)] = 255

def step_level_7():
    global game_timeout
    global node_counter, node_value, node_lock, node_switch_state
    if node_counter[0] > 0:
        node_counter[0] = node_counter[0] - 1
        if node_counter[0] == 0:
            for node_index in range(0, 6):
                node_value[node_lock[node_index]] = 0
    else:
        for node_index in range(0, array_size):
            if node_switch_state[node_index] == 1:
                game_timeout = 0
                node_switch_state[node_index] = 0
                if node_value[node_index] > 0:
                    node_value[node_index] = 0
                else:
                    node_value[node_index] = 128
        finished = True
        for node_index in range(0, 6):
            if node_value[node_lock[node_index]] == 0:
                finished = False
        for node_index in range(0, array_size):
            if node_value[node_index] > 0:
                temp_value = False
                for temp_index in range(0, 6):
                    if node_lock[temp_index] == node_index:
                        temp_value = True
                if temp_value == True:
                    pass
                else:
                    finished = False
        if finished == True:
            level_init(8)
            return

def step_level_8():
    global game_timeout
    global array_size, field_width, field_width, node_counter, node_value, node_switch_state
    for node_index in range(0, array_size):
        if node_switch_state[node_index] == 1:
            game_timeout = 0
            px, py = get_node_coords(node_index)
            node_offset = get_node_offset(px, 0)
            temp_value = node_counter[node_offset]
            temp_value = temp_value - 1
            if temp_value < 0: temp_value = 0
            node_counter[node_offset] = temp_value
            node_switch_state[node_index] = 0
    for xo in range(0, field_width):
        if randrange(0, 100) == 0:
            node_offset = get_node_offset(xo, 0)
            temp_value = node_counter[node_offset]
            temp_value = temp_value + 1
            if temp_value > field_height: temp_value = field_height
            node_counter[node_offset] = temp_value
    for xo in range(0, field_width):
        node_offset = get_node_offset(xo, 0)
        temp_value = node_counter[node_offset]
        for yo in range(0, (field_height - 1)):
            if (temp_value - 1) >= yo:
                node_value[get_node_offset(xo, ((field_height - 1) - yo))] = 128
            else:
                node_value[get_node_offset(xo, ((field_height - 1) - yo))] = 0
    finished = True
    for xo in range(0, field_width):
        node_offset = get_node_offset(xo, 0)
        if node_counter[node_offset] != 0:
            finished = False
    if finished == True:
        level_init(9)
        return

def step_level_9():
    global game_timeout
    global array_size, node_deform, node_counter, node_switch_state, node_value
    global field_width, field_height
    for node_index in range(0, array_size):
        node_value[node_index] = 0
    for node_index in range(0, array_size):
        if node_switch_state[node_index] == 1:
            game_timeout = 0
            node_counter[1] = node_index
            node_switch_state[node_index] = 0
    if randrange(0, 1) == 0:
        xo, yo = get_node_coords(node_deform[0])
        temp_random = randrange(0, 4)
        if temp_random == 0:
            xo = xo + 1
            if xo >= field_width: xo = field_width - 1
        if temp_random == 1:
            xo = xo - 1
            if xo < 0: xo = 0
        if temp_random == 2:
            yo = yo + 1
            if yo >= field_height: yo = field_height - 1
        if temp_random == 3:
            yo = yo - 1
            if yo < 0: yo = 0
        node_offset = get_node_offset(xo, yo)
        if node_offset != node_deform[0] and node_offset != node_deform[1]:
            for node_index in range((array_size - 1), 0, -1):
                node_deform[node_index] = node_deform[node_index -1]
            node_deform[0] = node_offset
            if node_deform[0] == node_counter[1]:
                if node_counter[0] > 1:
                    node_counter[0] = node_counter[0] - 1
                else:
                    level_init(10)
                    return
                node_counter[1] = array_size
    for node_index in range((array_size - 1), -1, -1):
        if node_index < node_counter[0]:
            node_offset = node_deform[node_index]
            if node_offset < array_size:
                node_value[node_offset] = 150 - (node_index * 2)
    node_value[node_deform[0]] = 150
    if node_counter[1] < array_size:
        node_value[node_counter[1]] = 255

def step_level_10():
    global game_timeout
    global node_value, node_switch_state, field_width, field_height
    for node_index in range(0, array_size):
        if node_switch_state[node_index] == 1:
            node_switch_state[node_index] = 0
            game_timeout = 0
            if node_value[node_index] == 0:
                node_value[node_index] = 128
            else:
                node_value[node_index] = 0
            x, y = get_node_coords(node_index)
            for oy in range(y - 1, y + 2):
                for ox in range(x - 1, x + 2):
                    if oy < 0 or oy > (field_height - 1) or ox < 0 or ox > (field_width - 1):
                        pass
                    else:
                        if oy == y and ox == x:
                            pass
                        else:
                            temp_index = get_node_offset(ox, oy)
                            if node_value[temp_index] == 0:
                                node_value[temp_index] = 128
                            else:
                                node_value[temp_index] = 0
    finished = True
    for node_index in range(0, array_size):
        if node_value[node_index] < 1:
            finished = False
    if finished == True:
        level_init(11)
        return

def step_level_11():
    global game_timeout
    global array_size, node_lock, node_value, node_velocity, node_switch_state, node_deform, field_width, field_height
    for node_index in range(0, array_size):
        if node_switch_state[node_index] == 1:
            game_timeout = 0
            node_switch_state[node_index] = 0
            if node_deform[node_index] == 0:
                node_deform[node_index] = 1
    node_lock[0] = node_lock[0] + 1
    if node_lock[0] < 16:
        return
    else:
        node_lock[0] = 0
    for node_index in range(0, array_size):
        if node_deform[node_index] == 1:
            if node_index & 1 == 1:
                if node_counter[node_index] > array_size:
                    node_counter[node_index] = array_size
                if node_counter[node_index] < 0:
                    node_counter[node_index] = 0
                temp_value = node_value[node_counter[node_index]]
                temp_value = temp_value + 64
                if temp_value > 255: temp_value = 255
                node_value[node_counter[node_index]] = temp_value
    finished = True
    for node_index in range(0, array_size):
        if node_value[node_index] != 255:
            finished = False
    if finished == True:
        level_init(12)
        return
    for node_index in range(0, array_size):
        if node_deform[node_index] == 1:
            if node_index & 1 == 0:
                if node_counter[node_index] > array_size:
                    node_counter[node_index] = array_size
                if node_counter[node_index] < 0:
                    node_counter[node_index] = 0
                temp_value = node_value[node_counter[node_index]]
                temp_value = temp_value - 16
                if temp_value < 0: temp_value = 0
                node_value[node_counter[node_index]] = temp_value
    for node_index in range(0, array_size):
        if node_deform[node_index] == 1:
            if randrange(0, 8) == 0:
                if node_velocity[node_index] == 4:
                    node_velocity[node_index] = 8
                elif node_velocity[node_index] == 2:
                    node_velocity[node_index] = 4
                elif node_velocity[node_index] == 6:
                    node_velocity[node_index] = 2
                elif node_velocity[node_index] == 8:
                    node_velocity[node_index] = 6
    for node_index in range(0, array_size):
        if node_deform[node_index] == 1:
            xo, yo = get_node_coords(node_counter[node_index])
            if node_velocity[node_index] == 8:
                yo = yo - 1
                if yo < 0: yo = field_height - 1
            elif node_velocity[node_index] == 6:
                xo = xo + 1
                if xo >= field_width: xo = 0
            elif node_velocity[node_index] == 2:
                yo = yo + 1
                if yo >= field_height: yo = 0
            elif node_velocity[node_index] == 4:
                xo = xo - 1
                if xo < 0: xo = field_width - 1
            node_counter[node_index] = get_node_offset(xo, yo)

def step_level_12():
    global game_timeout
    global node_deform, node_value, array_size, node_switch_state, node_velocity
    if node_deform[2] == 128:
        node_deform[1] = node_deform[1] + 1
        if node_deform[1] >= 192:
            node_deform[1] = 192
            node_deform[2] = 127
    elif node_deform[2] == 127:
        node_deform[1] = node_deform[1] - 1
        if node_deform[1] <= 64:
            node_deform[1] = 64
            node_deform[2] = 128
    finished = True
    for node_index in range(0, array_size):
        if node_velocity[node_index] == 0 and node_index != node_deform[0]:
            finished = False
    if finished == True:
        level_init(13)
        return
    xh, yh = get_node_coords(node_deform[0])
    for node_index in range(0, array_size):
        if node_switch_state[node_index] == 1:
            game_timeout = 0
            node_switch_state[node_index] = 0
            if node_index == node_deform[0]:
                for node_offset in range(0, array_size):
                    node_velocity[node_offset] = 0
            else:
                xo, yo = get_node_coords(node_index)
                if xo == xh:
                    if yh > yo:
                        for y in range(yh - 1, yo - 1, -1):
                            if node_velocity[get_node_offset(xh, y)] == 63:
                                break
                            else:
                                node_velocity[get_node_offset(xh, y)] = 63
                                node_deform[0] = get_node_offset(xh, y)
                    elif yh < yo:
                        for y in range(yh + 1, yo + 1, 1):
                            if node_velocity[get_node_offset(xh, y)] == 63:
                                break
                            else:
                                node_velocity[get_node_offset(xh, y)] = 63
                                node_deform[0] = get_node_offset(xh, y)
                elif yo == yh:
                    if xh > xo:
                        for x in range(xh - 1, xo - 1, -1):
                            if node_velocity[get_node_offset(x, yh)] == 63:
                                break
                            else:
                                node_velocity[get_node_offset(x, yh)] = 63
                                node_deform[0] = get_node_offset(x, yh)
                    elif xh < xo:
                        for x in range(xh + 1, xo + 1, 1):
                            if node_velocity[get_node_offset(x, yh)] == 63:
                                break
                            else:
                                node_velocity[get_node_offset(x, yh)] = 63
                                node_deform[0] = get_node_offset(x, yh)
    for node_index in range(0, array_size):
        node_value[node_index] = node_velocity[node_index]
    node_value[node_deform[0]] = node_deform[1]

def step_level_13():
    global game_timeout
    global node_velocity, node_value, node_deform, node_switch_state, array_size
    if node_velocity[0] == 0:
        node_velocity[0] = 1
        node_velocity[1] = 0
        node_velocity[2] = 0
        for node_index in range(0, array_size):
            node_value[node_index] = 0
        return
    if node_velocity[0] == 1:
        if node_velocity[2] < 8:
            node_velocity[2] = node_velocity[2] + 1
        else:
            node_velocity[2] = 0
            if node_velocity[1] < array_size:
                temp_value = node_velocity[1]
                node_offset = node_deform[temp_value]
                node_value[node_offset] = 16
                temp_value = temp_value + 1
                node_velocity[1] = temp_value
            else:
                if node_velocity[3] < 2:
                    node_velocity[3] = node_velocity[3] + 1
                else:
                    node_velocity[3] = 0
                    node_velocity[0] = 2
                    node_velocity[1] = 0
        return
    if node_velocity[0] == 2:
        for node_index in range(0, array_size):
            if node_switch_state[node_index] == 1:
                game_timeout = 0
                node_switch_state[node_index] = 0
                temp_value = node_velocity[1]
                node_offset = node_deform[temp_value]
                if node_index == node_offset:
                    node_value[node_offset] = 255
                    temp_value = temp_value + 1
                    if temp_value >= array_size:
                        level_init(14)
                        return
                    else:
                        node_velocity[1] = temp_value
                else:
                    node_velocity[1] = 0
                    node_velocity[2] = 0
                    node_velocity[0] = 3
        return
    if node_velocity[0] == 3:
        if node_velocity[2] < 8:
            node_velocity[2] = node_velocity[2] + 1
        else:
            if node_velocity[1] < array_size:
                if node_value[node_velocity[1]] > 0:
                    node_value[node_velocity[1]] = 0
                node_velocity[1] = node_velocity[1] + 1
            else:
                node_velocity[1] = 0
                node_velocity[0] = 0
        return

def step_level_14():
    global node_value
    for node_index in range(0, array_size):
        if node_switch_state[node_index] == 1:
            node_switch_state[node_index] = 0
            temp_value = node_value[node_index]
            temp_value = temp_value + 32
            if temp_value > 255: temp_value = 0
            node_value[node_index] = temp_value

def check_vendor_code(code): # Play cool cracktro music
    var_A = code # Adjusting Bell Curves
    var_B = 0 # Aligning Covariance Matrices
    var_C = var_A & 0b1 # Attempting to Lock Back-Buffer
    var_A = var_A >> 1 # Building Data Trees
    for index in range(0, 6): # Calculating Inverse Probability Matrices
        var_B = var_B + (var_A & 0b1) # Compounding Inert Tessellations
        var_A = var_A >> 1 # Iterating Cellular Automata
    var_D = (var_B & 0b1) == var_C # Obfuscating Quigley Matrix
    var_A = code # Reconfiguring User Mental Processes
    var_B = 0 # Resolving GUID Conflict
    var_C = (var_A >> 5) + 1 # Retrieving from Back Store
    var_A = ((var_A >> 1) & 0b001111) >> (4 - var_C) # Sequencing Particles
    for index in range(0, var_C): # Setting Universal Physical Constants
        var_B = var_B + (var_A & 0b1) # Time-Compressing Simulator Clock
        var_A = var_A >> 1 # Unable to Reveal Current Activity
    return ((var_B & 0b1) == 1) & var_D # Reticulating Splines

def hud_init():
    global hud_value, array_size, hud_code
    hud_value = [0] * array_size
    hud_code = randrange(0, 32)

def hud_draw():
    global unlocked, vendor_code_entry, game_level
    overscan_fill(0)
    if unlocked == True:
        x, y = get_node_coords(game_level + 7)
        overscan_set_at(x, y, 255)
        for node_index in range(28, 43):
            x, y = get_node_coords(node_index)
            overscan_set_at(x, y, 32)
        for node_index in range(63, 67):
            x, y = get_node_coords(node_index)
            overscan_set_at(x, y, (node_index - 62) * 32)
        x, y = get_node_coords(55)
        overscan_set_at(x, y, 16)
        x, y = get_node_coords(62)
        if game_timed == True:
            overscan_set_at(x, y, 255)
        else:
            overscan_set_at(x, y, 16)
    else:
        if game_level >= 0 and game_level <= 13:
            x, y = get_node_coords(game_level)
            overscan_set_at(x, y, 255)
        for node_index in range(21,70):
            x, y = get_node_coords(node_index)
            overscan_set_at(x, y, vendor_code_entry[node_index])
        for node_index in range(14, 21):
            x, y = get_node_coords(node_index)
            overscan_set_at(x, y, 32)
        temp_value = 0
        for node_index in range(0, 7):
            if vendor_code_pass[node_index] == True:
                temp_value = temp_value + 1
        if temp_value > 0:
            x, y = get_node_coords(temp_value + 13)
            overscan_set_at(x, y, 128)  

def hud_step():
    global unlocked, vendor_code_entry, node_switch_state, game_timed
    if unlocked == True:
        for node_index in range(28, 43):
            if node_switch_state[node_index] == 1:
                node_switch_state[node_index] = 0
                temp_value = node_index - 28
                level_init(temp_value)
        for node_index in range(63, 67):
            if node_switch_state[node_index] == 1:
                global current_level, current_change
                node_switch_state[node_index] = 0
                temp_value = node_index - 63
                current_level = temp_value
                current_change = True
        if node_switch_state[55] == 1:
            node_switch_state[55] = False
            unlocked = False
        if node_switch_state[62] == 1:
            node_switch_state[62] = 0
            if game_timed == True:
                game_timed = False
            else:
                game_timed = True
    else:
        for node_index in range(21,70):
            if node_switch_state[node_index] == 1:
                node_switch_state[node_index] = 0
                if vendor_code_entry[node_index] == 0:
                    vendor_code_entry[node_index] = 128
                else:
                    vendor_code_entry[node_index] = 0
                hud_code_check()

def hud_code_check():
    codes = bytearray(7)
    finished = True
    for i in range(0, 7):
        codes[i] = hud_code_get(i)
        if check_vendor_code(codes[i]) == 1:
            vendor_code_pass[i] = True
        else:
            vendor_code_pass[i] = False
            finished = False
    for i in range(0, 7):
        for index in range(0, 7):
            if index != i:
                if codes[i] == codes[index]:
                    finished = False
    if finished == True:
        global unlocked
        unlocked = True
        
def hud_code_get(index):
    global vendor_code_entry
    temp_values = bytearray(7)
    for i in range(0, 7):
        node_index = (index * 7) + 21 + i
        temp_values[i] = vendor_code_entry[node_index] 
    temp_value = 0
    for i in range(0, 7):
        if temp_values[i] == 0:
            temp_value = temp_value << 1
        else:
            temp_value = temp_value << 1 | 0b1
    return temp_value

field_width =           7
field_height =          10
array_size =            field_width * field_height

overscan =				bytearray(array_size)

button_x =              0
button_y =              0

node_value =            bytearray(array_size)
node_lock =             bytearray(array_size)
node_deform =           bytearray(array_size)
node_counter =          bytearray(array_size)
node_velocity =         bytearray(array_size)
node_switch_state =     bytearray(array_size)
node_rendered =         bytearray(array_size)

hud_value =             bytearray(array_size)
vendor_code_entry = 	bytearray(array_size)
vendor_code_pass =		bytearray(7)

badge_type = 			1
unlocked =				False

ant_value =             bytearray(array_size)
ant_rotation =          0
ant_position =          0
ant_random =            0
ant_count =             0

sub_level_1 =           0
column_level_1 =        0
left_level_1 =          0
right_level_1 =         0
first_node_level_1 =    0

node_level_2 =          0

node_1_level_3 =        0
node_2_level_3 =        0
node_3_level_3 =        0
node_4_level_3 =        0

started_level_5 =       0

level_init(-3)
game_level = 0
game_timeout = 0
game_timed = True
level_init(game_level)

game_mode = 0
hud_code = 0
hud_pressed = 0
hud_was_pressed = 0
hud_counter = 0
fake_press = False

chip_60 = 				[66, 59, 52, 45, 38, 65, 58, 51, 44, 37, 30, 23, 16, 9, 2, 64, 57, 50, 43, 36, 29, 22, 15, 8, 1, 63, 56, 49, 42, 35, 28, 21, 14, 7, 0]
chip_63 = 				[6, 13, 20, 27, 34, 41, 48, 55, 62, 69, 5, 12, 19, 26, 33, 40, 47, 54, 61, 68, 4, 11, 18, 25, 32, 39, 46, 53, 60, 67, 3, 10, 17, 24, 31]

buffer_60 = 			bytearray(35)
buffer_63 = 			bytearray(35)

bounceDelay = 			0.001
gama_64 =				[0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 29, 32, 35, 38, 41, 44, 47, 50, 53, 57, 61, 65, 69, 73, 77, 81, 85, 89, 94, 99, 104, 109, 114, 119, 124, 129, 134, 140, 146, 152, 158, 164, 170, 176, 182, 188, 195, 202, 209, 216, 223, 230, 237, 244, 251, 255]
gama_32 = 				[0, 1, 2, 4, 6, 10, 13, 18, 22, 28, 33, 39, 46, 53, 61, 69, 78, 86, 96, 106, 116, 126, 138, 149, 161, 173, 186, 199, 212, 226, 240, 255]
gama_16 =				[0, 2, 6, 13, 22, 33, 46, 61, 78, 96, 116, 138, 161, 186, 212, 240]
addrMap = 				[[0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C],[0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C],[0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C,0x3C],[0x3F,0x3F,0x3F,0x3F,0x3F,0x3C,0x3C,0x3C,0x3C,0x3C],[0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F],[0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F],[0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F,0x3F]]
LEDmap = 				[[36,35,34,33,32,31,30,29,28,27],[26,25,24,23,22,21,20,19,18,17],[16,15,14,13,12,11,10,9,8,7],[32,33,34,35,36,6,5,4,3,2],[22,23,24,25,26,27,28,29,30,31],[12,13,14,15,16,17,18,19,20,21],[2,3,4,5,6,7,8,9,10,11]]

coreXfer_buttonStates = [[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]]
coreXfer_buttonStates_old = [[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]]

row1 = machine.Pin(2, machine.Pin.OUT, value=1)
row2 = machine.Pin(3, machine.Pin.OUT, value=1)
row3 = machine.Pin(4, machine.Pin.OUT, value=1)
col10 = machine.Pin(5, machine.Pin.IN)
col8 = machine.Pin(6, machine.Pin.IN)
col6 = machine.Pin(7, machine.Pin.IN)
col4 = machine.Pin(8, machine.Pin.IN)
col3 = machine.Pin(9, machine.Pin.IN)
col2 = machine.Pin(10, machine.Pin.IN)
col1 = machine.Pin(11, machine.Pin.IN)
row5 = machine.Pin(12, machine.Pin.OUT, value=1)
row6 = machine.Pin(13, machine.Pin.OUT, value=1)
row7 = machine.Pin(14, machine.Pin.OUT, value=1)
row4 = machine.Pin(22, machine.Pin.OUT, value=1)
led = machine.Pin(25, machine.Pin.OUT)
col5 = machine.Pin(26, machine.Pin.IN)
col7 = machine.Pin(27, machine.Pin.IN)
col9 = machine.Pin(28, machine.Pin.IN)

i2c = 					machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0), freq=100000)
led_init()

current_change = False
current_level = 0
flip = False

core1_thread = _thread.start_new_thread(core1_thread, ())

while True:
    gc.collect()
    step_level_minus_3()
    if hud_pressed == 1:
        hud_was_pressed = 1
        temp_check = True
        for node_index in range(1, array_size):
            if node_switch_state[node_index] == 1:
                temp_check = False
        if temp_check == True:
            hud_counter = hud_counter + 1
            if hud_counter > 255:
                node_switch_state[0] = 0
                hud_counter = 0
                hud_was_pressed = 0
                hud_pressed = 0
                if game_mode == 0:
                    game_mode = 1
                    hud_init()
                else:
                    game_mode = 0
            else:
                continue
        else:
            hud_counter = 0
            hud_was_pressed = 0
            hud_pressed = 0
            node_switch_state[0] = 1
            fake_press = True
    else:
        if hud_was_pressed == 1:
            hud_was_pressed = 0
            hud_counter = 0
            node_switch_state[0] = 1
            fake_press = True
        else:
            pass
    if game_mode == 0:
        step()
        draw()
        if fake_press == True:
            fake_press = False
            node_switch_state[0] = 0
    else:
        hud_step()
        hud_draw()
    flip = True
    utime.sleep(.03)
