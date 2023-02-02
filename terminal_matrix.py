#! /usr/bin/env python3

# Orginal Author: Joao S. O. Bueno
# gwidion@gmail.com
# GPL. v3.0

# Modified by: SwedishHack
# berglundgary@gmail.com
# Feb 2, 2023
# Reason for change: 
#   Rewrite to work with and without ANSI graphics with CHANGE_COLORS Boolean switch
#   Modified the language characters
#   Change output to be entire screen frame in one sys.stdout.write command
#   Added dictionaries for colors
#   Added ability to switch between monochrome (CHANGE_COLORS = False) and color (CHANGE_COLORS = True) output
#   Color output uses four colors letters now instead of two

CHANGE_COLORS = True

FRAME_DELAY = 0.1 # this is used to keep the output to maximum of 10 frames a second

RAND_START = 80 # 1 in n chance to start
RAND_BREAK = 10 # average length of break
RAND_CHANGE = 2 # 1 in n chance to change current character
RAND_LEN_INCREASE = 10 # 1 in n chance to increase length
RAND_FALL_DROP = 2 # 1 in n chance to fall if broken free

import shutil
import sys
import time
import random
import os
import numpy as np

getchars = lambda start, end: [chr(i) for i in range(start, end)]

latin = getchars(0x21, 0x7F)
greek = getchars(0x38E, 0x3A2) + getchars(0x3A3, 0x400)
hebrew = getchars(0x5D0, 0x5EB)
cyrillic = getchars(0x400, 0x500)

chars= latin + greek + cyrillic + hebrew 

# colors for ANSI dictionaries
# https://learn.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences?redirectedfrom=MSDN#text-formatting
TEXT_BR_COLOR = {
    "BLACK": "\033[90m",
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
    "WHITE": "\033[97m",
    "NORM": "\033[0m",
}
TEXT_NORM_COLOR = {
    "BLACK": "\033[30m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "WHITE": "\033[37m",
    "NORM": "\033[39m",
}

def init():
    '''
    This function does initalization before running
    '''
    global col_count, row_count
    col_count, row_count = shutil.get_terminal_size()
    os.system("color")  # enables ansi escape characters in terminal
    print("\033[?25l")  # Hides cursor
    
    # col_count -= 1
    row_count -= 2
    # col_count = 90
    # row_count = 30

def end():
    '''
    The function clean up after running
    '''
    print("\033[m")   # reset attributes
    print("\033[?25h")  # Show cursor

def update_cols(cols):
    '''
    This function controls the logic of creating and lengthening the string columns
    '''
    
    for col in range(len(cols)):
        # if whole col is blank
        # print(f'cols[col]:{cols[col]}')
        if cols[col].isspace():
            # randomly start one
            if random.randrange(col_count) < 1:
                cols[col] = random.choice(chars) + cols[col][:-1]
        else:            
            # if broke free from top 
            if cols[col][0].isspace():
                # randomly fall if broke free
                if random.randrange(RAND_FALL_DROP) < 1:
                    cols[col] = ' ' + cols[col][:-1]
                # randomly start another one
                if random.randrange(RAND_START) < 1:
                    cols[col] = random.choice(chars) + cols[col][:-1]
            else:                
                row = cols[col].find(' ')
                if row == -1:
                    row = 0
                # randomly break free better chance as it grews or if reach bottom 
                if random.randrange(row) > RAND_BREAK or row + 1 == row_count:
                    cols[col] = ' ' + cols[col][:-1]
                else:
                    # randomly increase length
                    if random.randrange(RAND_LEN_INCREASE) < 1:
                        cols[col] = cols[col][:row] + random.choice(chars) + cols[col][row:-1]
                    else:
                        # randomly change character if it didn't drop
                        if random.randrange(RAND_CHANGE) < 1:
                            cols[col] = cols[col][:row-1] + random.choice(chars) + cols[col][row:]
                            
    return cols

def make_screen_frame(cols):
    '''
    This function wraps all the columns in to a single string to print to the screen as entire frame
    This fucntion colors the output with ANSI ESC sequence 
    '''
    screen_frame = ''
    
    if CHANGE_COLORS == False:
        for row in range(row_count):         
            for col in range(len(cols)):
                screen_frame += cols[col][row]
            screen_frame += TEXT_NORM_COLOR['GREEN'] + '\n'
            
    else:
        char_color = np.zeros((col_count,row_count), dtype=int)
        screen_frame = TEXT_NORM_COLOR['GREEN']
        for row in range(row_count-1,-1,-1):   
            screen_frame = '\n' + screen_frame
            for col in range(col_count-1,-1,-1):
                
                if cols[col][row] == ' ':
                    if TEXT_NORM_COLOR['GREEN'] == screen_frame[:5]:
                        screen_frame = TEXT_NORM_COLOR['GREEN'] + cols[col][row] + screen_frame[5:]
                    else:
                        screen_frame = TEXT_NORM_COLOR['GREEN'] + cols[col][row] + screen_frame
                    char_color[col][row] = 0
                else:
                    if row == row_count-1:
                        if TEXT_NORM_COLOR['GREEN'] == screen_frame[:5]:
                            screen_frame = TEXT_NORM_COLOR['GREEN'] + cols[col][row] + screen_frame[5:]
                        else:
                            screen_frame = TEXT_NORM_COLOR['GREEN'] + cols[col][row] + screen_frame
                            
                        char_color[col][row] = 1
                        
                    elif char_color[col][row+1] == 0:
                        if TEXT_BR_COLOR['WHITE'] == screen_frame[:5]:
                            screen_frame = TEXT_BR_COLOR['WHITE'] + cols[col][row] + screen_frame[5:]
                        else:
                            screen_frame = TEXT_BR_COLOR['WHITE'] + cols[col][row] + screen_frame
                            
                        char_color[col][row] = 4
                        
                    elif char_color[col][row+1] == 4:
                        if TEXT_NORM_COLOR['WHITE'] == screen_frame[:5]:
                            screen_frame = TEXT_NORM_COLOR['WHITE'] + cols[col][row] + screen_frame[5:]
                        else:
                            screen_frame = TEXT_NORM_COLOR['WHITE'] + cols[col][row] + screen_frame
                            
                        char_color[col][row] = 3
                        
                    elif char_color[col][row+1] == 3:
                        if TEXT_BR_COLOR['GREEN'] == screen_frame[:5]:
                            screen_frame = TEXT_BR_COLOR['GREEN'] + cols[col][row] + screen_frame[5:]
                        else:
                            screen_frame = TEXT_BR_COLOR['GREEN'] + cols[col][row] + screen_frame
                            
                        char_color[col][row] = 2
                        
                    elif char_color[col][row+1] == 2:
                        if TEXT_NORM_COLOR['GREEN'] == screen_frame[:5]:
                            screen_frame = TEXT_NORM_COLOR['GREEN'] + cols[col][row] + screen_frame[5:]
                        else:
                            screen_frame = TEXT_NORM_COLOR['GREEN'] + cols[col][row] + screen_frame
                            
                        char_color[col][row] = 1
                        
                    else:
                        if TEXT_NORM_COLOR['GREEN'] == screen_frame[:5]:
                            screen_frame = TEXT_NORM_COLOR['GREEN'] + cols[col][row] + screen_frame[5:]
                        else:
                            screen_frame = TEXT_NORM_COLOR['GREEN'] + cols[col][row] + screen_frame
                            
                        char_color[col][row] = 1
                    
    return screen_frame
            
def main():
    '''
    Main function state machine
    '''
    cols= [' ' * row_count] * col_count
    screen_frame = ''
    
    # clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    if CHANGE_COLORS == True:
        # store the cursor postion at home position
        print("\033[s")
    
    while True:
        # get start time for frame delay
        start_time = time.perf_counter()
        cols = update_cols(cols)
        
        screen_frame = make_screen_frame(cols)
        
        if CHANGE_COLORS == True:
            # move cursor postion back to home position
            print("\033[u")
        else:
            # clear the screen
            os.system('cls' if os.name == 'nt' else 'clear')
        
        # send out the stdout 
        sys.stdout.write(screen_frame)
        
        # sys.stdout.flush()
        
        while time.perf_counter() < (start_time + FRAME_DELAY):
            pass
        # time.sleep(FRAME_DELAY)        

def doit():
    try:
        init()
        main()
        
    except KeyboardInterrupt:
        pass
    finally:
        end()

if __name__=="__main__":
    doit()