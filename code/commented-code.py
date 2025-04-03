import machine
import rp2
import utime
import _thread
import gc

def core1_thread():
    """
    Second core thread that handles event processing and display rendering.
    This runs concurrently with the main code to manage I/O operations.
    """
    gc.collect()  # Run garbage collection to free up memory
    global flip, current_change, current_level
    while True:
        handle_events()  # Process button input events
        if flip == True:
            render()  # Update the LED display
            flip = False
        if current_change == True:
            led_current(current_level)  # Update LED brightness/current
            current_change = False

def led_init():
    """
    Initialize the LED matrix drivers via I2C.
    This sets up the IS31FL3731 LED drivers (at addresses 0x3C and 0x3F).
    """
    i2c.writeto_mem(0x3C, 0x4F, b'\x00')  # Disable software shutdown on first chip
    i2c.writeto_mem(0x3C, 0x00, b'\x01')  # Select first frame for first chip
    i2c.writeto_mem(0x3F, 0x4F, b'\x00')  # Disable software shutdown on second chip
    i2c.writeto_mem(0x3F, 0x00, b'\x01')  # Select first frame for second chip
    
    # Set all LEDs to moderate brightness (0x07)
    for i in range(0,36):
        i2c.writeto_mem(0x3C, 0x26 + i, b'\x07')
        i2c.writeto_mem(0x3F, 0x26 + i, b'\x07')
    
    # Update the display
    i2c.writeto_mem(0x3C, 0x25, b'\x00')
    i2c.writeto_mem(0x3F, 0x25, b'\x00')
    
def led_current(level):
    """
    Set LED current (brightness) level for all LEDs.
    
    Args:
        level: Brightness level from 0-3 where:
               0 = Low brightness (0x07)
               1 = Medium-low brightness (0x05)
               2 = Medium-high brightness (0x03)
               3 = High brightness (0x01)
               
    Note: Counter-intuitively, lower values mean higher brightness with the IS31FL3731
    """
    if level == 0:
        for i in range(0,36):
            i2c.writeto_mem(0x3C, 0x26 + i, b'\x07')  # Lowest brightness
            i2c.writeto_mem(0x3F, 0x26 + i, b'\x07')
    elif level == 1:
        for i in range(0,36):
            i2c.writeto_mem(0x3C, 0x26 + i, b'\x05')  # Medium-low brightness
            i2c.writeto_mem(0x3F, 0x26 + i, b'\x05')
    elif level == 2:
        for i in range(0,36):
            i2c.writeto_mem(0x3C, 0x26 + i, b'\x03')  # Medium-high brightness
            i2c.writeto_mem(0x3F, 0x26 + i, b'\x03')
    elif level == 3:
        for i in range(0,36):
            i2c.writeto_mem(0x3C, 0x26 + i, b'\x01')  # Highest brightness
            i2c.writeto_mem(0x3F, 0x26 + i, b'\x01')
    
    # Update the display
    i2c.writeto_mem(0x3C, 0x25, b'\x00')
    i2c.writeto_mem(0x3F, 0x25, b'\x00')

def render():
    """
    Render the current state of the game to the LED matrix.
    This transfers data from the overscan buffer to the LED drivers.
    """
    global buffer_60, buffer_63, overscan       
    
    # Map the overscan buffer to the physical LED layout for each chip
    for i in range(0, 35):
        buffer_60[i] = overscan[chip_60[i]]  # Map data for first chip
        buffer_63[i] = overscan[chip_63[i]]  # Map data for second chip
    
    # Send the data to LED drivers
    i2c.writeto_mem(60, 2, buffer_60)  # Update first chip (I2C address 0x3C/60)
    i2c.writeto_mem(63, 2, buffer_63)  # Update second chip (I2C address 0x3F/63)
    
    # Update the display
    i2c.writeto_mem(0x3C, 0x25, b'\x00')
    i2c.writeto_mem(0x3F, 0x25, b'\x00')

def overscan_fill(value):
    """
    Fill the entire overscan buffer with a specific brightness value.
    
    Args:
        value: Brightness value (0-255) to fill the display with
    """
    global overscan
    temp = int(value / 4)  # Scale value to gamma table index
    for i in range(0, array_size):
        overscan[i] = gama_64[temp]  # Apply gamma correction for better visual appearance

def overscan_set_at(x, y, value):
    """
    Set a specific LED at coordinates (x, y) to a brightness value.
    
    Args:
        x, y: Coordinates of the LED
        value: Brightness value (0-255)
    """
    global overscan
    temp = int(value / 4)  # Scale value to gamma table index
    node_offset = get_node_offset(x, y)  # Convert coordinates to buffer index
    overscan[node_offset] = gama_64[temp]  # Set with gamma correction

def draw():
    """
    Main drawing function that updates the LED display based on the current game level.
    Each game level has its own specific drawing logic.
    """
    global button_x, button_y
    global node_value, node_deform, node_rendered, node_lock, node_counter
    global game_level
    global field_width, field_height
    
    # Level 0: Ripple/wave effect
    if game_level == 0:
        overscan_fill(0)  # Clear display
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
    
    # Levels 1-3, 7-14: Simple value-based display
    if game_level == 1 or game_level == 2 or game_level == 3 or game_level == 7 or game_level == 8 or game_level == 9 or game_level == 10 or game_level == 11 or game_level == 12 or game_level == 13 or game_level == 14:
        overscan_fill(0)  # Clear display
        for y in range(0, field_height):
            for x in range(0, field_width):
                node_offset = get_node_offset(x, y)
                temp_value = node_value[node_offset]
                overscan_set_at(x, y, temp_value)
    
    # Level 4: Direct display of node values
    if game_level == 4:
        overscan_fill(0)  # Clear display
        for y in range(0, field_height):
            for x in range(0, field_width):
                node_offset = get_node_offset(x, y)
                temp_value = node_value[node_offset]
                overscan_set_at(x, y, temp_value)
    
    # Level 5: Custom display based on node_counter and node_deform
    if game_level == 5:
        overscan_fill(0)  # Clear display
        for index in range(0, field_width):
            if node_counter[index] == 1:
                x, y = get_node_coords(node_deform[index])
                overscan_set_at(x, y, 255)  # Bright pixel
            if node_counter[index] == 2:
                x, y = get_node_coords(node_deform[index])
                overscan_set_at(x, y, 128)  # Medium pixel
    
    # Level 6: Display with special "comet tail" effect
    if game_level == 6:
        overscan_fill(0)  # Clear display
        # First draw all regular pixels
        for y in range(0, field_height):
            for x in range(0, field_width):
                node_offset = get_node_offset(x, y)
                temp_value = node_value[node_offset]
                overscan_set_at(x, y, temp_value)
        
        # Then add the "comet tail" effect for bright pixels
        for x in range(0, field_width):
            for y in range(0, field_height):
                node_offset = get_node_offset(x, y)
                temp_value = node_value[node_offset]
                if temp_value == 255:  # If this is a full-brightness pixel
                    temp_delta = 2
                    # Draw a fading trail upward
                    for yo in range(0, 8):
                        temp_tamp = int(256 / temp_delta)
                        if temp_tamp < 14: temp_tamp = 0
                        temp_delta = temp_delta + 4
                        target_y = y - yo - 1
                        if target_y < 0:
                            target_y = target_y + field_height
                        overscan_set_at(x, target_y, temp_tamp)

def handle_events():
    """
    Scan the button matrix and detect button presses.
    This function implements a 7×10 button matrix scan.
    """
    # Cycle through rows and read columns to detect button presses
    for x in range(0, 7):
        utime.sleep(bounceDelay)  # Small delay to avoid switch bounce
        
        # Enable one row at a time by setting it LOW (active)
        if x == 0:
            row7.value(1)  # Disable previous row
            row1.value(0)  # Enable current row
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
        
        # Read all columns to detect button presses for current row
        # A button is pressed when its column reads LOW (0)
        if(col1.value() == 0):
            coreXfer_buttonStates[x][0] = 1  # Mark as pressed
        else:
            coreXfer_buttonStates[x][0] = 0  # Mark as not pressed
            
        # Repeat for all columns
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
            
    get_button_states()  # Process the detected button states
    
def get_button_states():
    """
    Process button state changes and trigger appropriate events.
    This detects changes in button states and calls the corresponding event handlers.
    """
    global button_x, button_y, coreXfer_buttonStates_old
    
    # Check each button in the matrix
    for i in range(0, array_size):
        x, y = get_node_coords(i)  # Convert index to coordinates
        
        # If button state has changed
        if coreXfer_buttonStates[x][y] != coreXfer_buttonStates_old[x][y]:
            coreXfer_buttonStates_old[x][y] = coreXfer_buttonStates[x][y]  # Update old state
            
            # If the button's actual state differs from its tracked state
            if coreXfer_buttonStates[x][y] != node_switch_state[i]:
                button_x = x  # Store the coordinates of the button
                button_y = y
                
                # Call appropriate event handler based on press/release
                if coreXfer_buttonStates[button_x][button_y] == 0:
                    left_click_up_event(button_x, button_y)  # Button was released
                else:
                    left_click_down_event(button_x, button_y)  # Button was pressed

def left_click_down_event(x, y):
    """
    Handle button press events.
    
    Args:
        x, y: Coordinates of the pressed button
    """
    global node_switch_state
    # Mark button as pressed
    node_switch_state[get_node_offset(x, y)] = 1
    
    # Special handling for HUD button (top-left corner)
    if get_node_offset(x, y) == 0:
        global hud_pressed
        hud_pressed = 1

def left_click_up_event(x, y):
    """
    Handle button release events.
    
    Args:
        x, y: Coordinates of the released button
    """
    global node_switch_state
    # Mark button as released
    node_switch_state[get_node_offset(x, y)] = 0
    
    # Special handling for HUD button (top-left corner)
    if get_node_offset(x, y) == 0:
        global hud_pressed
        hud_pressed = 0

def get_node_offset(x, y):
    """
    Convert (x, y) coordinates to a buffer index.
    
    Args:
        x, y: Coordinates in the display grid
    
    Returns:
        index: The corresponding index in the buffer arrays
    """
    global field_width
    return (y * field_width) + x

def get_node_coords(index):
    """
    Convert a buffer index to (x, y) coordinates.
    
    Args:
        index: Index in the buffer arrays
    
    Returns:
        x, y: The corresponding coordinates in the display grid
    """
    global field_width
    y = int(index / field_width)
    x = index - (y * field_width)
    return x, y

def randrange(zero, modulo):
    """
    Generate a pseudo-random number.
    This uses the Langton's Ant simulation as a source of randomness.
    
    Args:
        zero: Ignored parameter (for compatibility with Python's randrange)
        modulo: Upper bound for the random value
    
    Returns:
        A pseudo-random number between 0 and modulo-1
    """
    global ant_random
    step_level_minus_3()  # Advance the Langton's Ant simulation to generate randomness
    if modulo == 0: modulo = 1  # Avoid division by zero
    return ant_random % modulo  # Return value within the requested range

def level_init(level):
    """
    Initialize a game level.
    This resets game state and sets up the specific configuration for each level.
    
    Args:
        level: The level number to initialize
    """
    global node_counter, node_switch_state, node_lock, node_velocity, node_value, node_deform
    global button_x, button_y
    global game_level, array_size, game_timeout
    global field_width, field_height
    
    # Reset all node states
    for node_index in range(0, array_size):
        node_counter[node_index] = 0
        node_switch_state[node_index] = 0
        node_lock[node_index] = 0
        node_velocity[node_index] = 0
        node_value[node_index] = 0
        node_deform[node_index] = 0
    
    # Reset button position and game timeout
    button_x = 0
    button_y = 0
    game_timeout = 0
    
    # Level -3: Langton's Ant random number generator
    if level == -3:
        global ant_rotation, ant_position
        ant_position = (7 * 5) + 4  # Start position
        ant_rotation = 0  # Start direction
    
    # Level 0: Initial demo/start screen
    if level == 0:
        for node_index in range(0, array_size):
            node_value[node_index] = 0
            node_velocity[node_index] = 128  # Initial velocity
    
    # Level 1: Binary division puzzle
    if level == 1:
        global sub_level_1, column_level_1, left_level_1, right_level_1
        sub_level_1 = 0
        column_level_1 = 0
        left_level_1 = 0
        right_level_1 = 0
    
    # Level 2: Whack-a-mole style game
    if level == 2:
        global node_level_2
        node_level_2 = array_size
        for node_index in range(0, array_size):
            node_value[node_index] = 64  # Set dim background
    
    # Level 3: Connect-the-dots puzzle
    if level == 3:
        global node_1_level_3, node_2_level_3, node_3_level_3, node_4_level_3
        node_1_level_3 = array_size
        node_2_level_3 = array_size
        node_3_level_3 = array_size
        node_4_level_3 = array_size
    
    # Level 4: Brightness adjustment puzzle
    if level == 4:
        for node_index in range(0, array_size):
            node_counter[node_index] = 7
            node_velocity[node_index] = 1
    
    # Level 5: Moving target game
    if level == 5:
        global started_level_5
        started_level_5 = 0
    
    # Level 6: Falling particles simulation
    if level == 6:
        for xo in range(0, field_width):
            yo = randrange(0, field_height)
            node_value[get_node_offset(xo, yo)] = 255  # Place bright pixels at random positions
    
    # Level 7: Memory game with hidden patterns
    if level == 7:
        node_counter[0] = 128
        for node_index in range(0, 6):
            node_lock[node_index] = randrange(0, array_size)
            node_value[node_lock[node_index]] = 128
    
    # Level 8: Column clearing game
    if level == 8:
        yo = 0
        for xo in range(0, field_width):
            node_counter[get_node_offset(xo, yo)] = 1
    
    # Level 9: Snake-like game
    if level == 9:
        for node_index in range(0, array_size):
            node_deform[node_index] = array_size
        node_deform[0] = randrange(0, array_size)
        node_counter[0] = array_size - 1
        node_counter[1] = array_size
    
    # Level 10 doesn't have special initialization
    if level == 10:
        pass
    
    # Level 11: Multiple moving objects
    if level == 11:
        for node_index in range(0, array_size):
            temp_random = randrange(0, 4)
            if temp_random == 0:
                node_velocity[node_index] = 8  # Up
            elif temp_random == 1:
                node_velocity[node_index] = 6  # Right
            elif temp_random == 2:
                node_velocity[node_index] = 2  # Down
            elif temp_random == 3:
                node_velocity[node_index] = 4  # Left
            node_counter[node_index] = node_index
            node_value[node_index] = 8
    
    # Level 12: Path drawing puzzle
    if level == 12:
        node_deform[0] = randrange(0, array_size)
        node_deform[1] = 64
        node_deform[2] = 128
    
    # Level 13: Pattern memorization game
    if level == 13:
        # Create a shuffled array of positions
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
        
    # Set the current game level
    game_level = level

def step():
    """
    Advance the game state by one step.
    This calls the appropriate level-specific step function based on the current game level.
    """
    global game_level
    
    # Langton's Ant for randomness
    if game_level == -3:
        step_level_minus_3()
        return
        
    # Main menu/intro screen
    if game_level == 0:
        step_level_0()
        return
        
    # Level 1: Binary division puzzle
    if game_level == 1:
        if game_timeout_check() == True:
            level_init(0)  # Back to menu if timeout
            return
        else:
            step_level_1()
            return
            
    # Level 2: Whack-a-mole
    if game_level == 2:
        if game_timeout_check() == True:
            level_init(1)  # Go to previous level if timeout
            return
        else:
            step_level_2()
            return
            
    # Level 3: Connect-the-dots
    if game_level == 3:
        if game_timeout_check() == True:
            level_init(2)  # Go to previous level if timeout
            return
        else:
            step_level_3()
            return
            
    # Level 4: Brightness adjustment
    if game_level == 4:
        if game_timeout_check() == True:
            level_init(3)  # Go to previous level if timeout
            return
        else:
            step_level_4()
            return
            
    # Level 5: Moving target game
    if game_level == 5:
        if game_timeout_check() == True:
            level_init(4)  # Go to previous level if timeout
            return
        else:
            step_level_5()
            return
            
    # Level 6: Falling particles
    if game_level == 6:
        if game_timeout_check() == True:
            level_init(5)  # Go to previous level if timeout
            return
        else:
            step_level_6()
            return
            
    # Level 7: Memory game
    if game_level == 7:
        if game_timeout_check() == True:
            level_init(6)  # Go to previous level if timeout
            return
        else:
            step_level_7()
            return    
            
    # Level 8: Column clearing
    if game_level == 8:
        if game_timeout_check() == True:
            level_init(7)  # Go to previous level if timeout
            return
        else:
            step_level_8()
            return
            
    # Level 9: Snake-like game
    if game_level == 9:
        if game_timeout_check() == True:
            level_init(8)  # Go to previous level if timeout
            return
        else:
            step_level_9()
            return
            
    # Level 10: Light toggling puzzle
    if game_level == 10:
        if game_timeout_check() == True:
            level_init(9)  # Go to previous level if timeout
            return
        else:
            step_level_10()
            return    
            
    # Level 11: Moving objects maze
    if game_level == 11:
        if game_timeout_check() == True:
            level_init(10)  # Go to previous level if timeout
            return
        else:
            step_level_11()
            return
            
    # Level 12: Path drawing
    if game_level == 12:
        if game_timeout_check() == True:
            level_init(11)  # Go to previous level if timeout
            return
        else:
            step_level_12()
            return
            
    # Level 13: Pattern memorization
    if game_level == 13:
        if game_timeout_check() == True:
            level_init(12)  # Go to previous level if timeout
            return
        else:
            step_level_13()
            return
            
    # Level 14: Free play mode
    if game_level == 14:
        step_level_14()
        return

def game_timeout_check():
    """
    Check if the game has timed out.
    
    Returns:
        True if the game has timed out, False otherwise
    """
    global game_level, game_timeout, game_timed
    if game_timed == True:
        game_timeout = game_timeout + 1
        if game_timeout >= 1000:  # Timeout after 1000 steps (~30 seconds at 30fps)
            return True
        else:
            return False
    # If game is not timed, never timeout
    return False

def step_level_minus_3():
    """
    Step function for the Langton's Ant simulation used for random number generation.
    Implements a cellular automaton that generates pseudo-random patterns.
    """
    global ant_position, ant_rotation, ant_count, ant_random, ant_value
    global node_value, field_width, field_height, array_size
    
    # Get current state and determine movement
    rotation = ant_rotation
    if ant_value[ant_position] == 255:  # If cell is "on"
        ant_value[ant_position] = 0  # Turn it "off"
        rotation = rotation + 1  # Turn right
        if rotation > 3: rotation = 0
    if ant_value[ant_rotation] == 0:  # If cell is "off"
        ant_value[ant_position] = 255  # Turn it "on"
        rotation = rotation - 1  # Turn left
        if rotation < 0: rotation = 3
    
    ant_rotation = rotation
    
    # Move the ant forward in the current direction
    x, y = get_node_coords(ant_position)
    if ant_rotation == 0: x = x + 1  # Right
    if ant_rotation == 1: y = y + 1  # Down
    if ant_rotation == 2: x = x - 1  # Left
    if ant_rotation == 3: y = y - 1  # Up
    
    # Handle wrapping around the edges
    if x >= field_width:
        x = 0
        y = y - 1
    if y < 0: y = field_height - 1
    if y >= field_height:
        y = 0
        x = x - y
    if x < 0: x = field_width - 1
    
    # Update ant position and counter
    ant_position = get_node_offset(x, y)
    ant_count = ant_count + 1
    
    # Generate a random number based on the current ant pattern
    last_random = ant_random
    ant_random = 0
    temp_random = [0] * field_height
    
    # Calculate a hash based on the current pattern
    for yo in range(0, field_height):
        temp_value = 0
        for xo in range(0, field_width):
            if ant_value[get_node_offset(xo, yo)] == 255:
                temp_value = temp_value + (1 << xo)  # Bitwise representation of row
        temp_random[yo] = temp_value
    
    # Combine the row values into a single random number
    for yo in range(0, field_height):
        ant_random = ant_random + temp_random[yo]
    
    