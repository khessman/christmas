# @Date:   2020-11-17T20:19:55+01:00
# @Email:  kalle.hessman@gmail.com
# @Filename: blaj4.py
# @Last modified time: 2020-11-22T21:57:39+01:00

'''
Dependencies:
    * ansicolors *
     - install with python -m pip install ansicolors
Letters or other objects to draw is included in the file object.py
'''

import os
import sys
import time
import random
import objects
import datetime as dt
from colors import color,blue, green, white, yellow,red

import ctypes
from ctypes import c_long, c_ulong
gHandle = ctypes.windll.kernel32.GetStdHandle(c_long(-11))


def moveCursor (y, x):
   """move cursor to position indicated by x and y."""
   value = x + (y << 16)
   ctypes.windll.kernel32.SetConsoleCursorPosition(gHandle, c_ulong(value))


'''
PARAMETERS BELOW:
'''
FRAME_RATE=50
DEBUG = ""
size_x,size_y = 200,60
bkg=' '
flake="*"
small_flake='°'
rain="'"
heavy_rain='/'
current_flake=flake
wind_dir=0
wind_speed=1
wind_speed_inc=1
wind_dir_inc=1
wind_speed_time =time.time()
wind_dir_time=time.time()
weather_time=time.time()
current_weather=0



object_list=[
            # objects.testimage,
            # objects.object1,
            objects.candle1_base,
            objects.candle1,
            objects.candle1_flame,

            objects.candle2_base,
            objects.candle2,
            objects.candle2_flame,

            objects.candle3_base,
            objects.candle3,
            objects.candle3_flame,

            objects.candle4_base,
            objects.candle4,
            objects.candle4_flame,

            objects.G,
            objects.O,
            objects.D,
            objects.J,
            objects.U,
            objects.L,
            objects.krans
            ]



class OutOfBoundsError(Exception): pass

class cell:
    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.tile=bkg
        self.hasChanged=False
        self.type='background'
        self.frozen = False
        self.color='#ffffff'

#create the grid
grid = []
for y in range(size_y):
    row=[]
    for x in range(size_x):
        row.append(cell(x,y))
    grid.append(row)



def generate_flakes(number):
    seed=random.randint(0, number)
    row=0
    #reset row 0
    for i in range(len(grid[0])):
        cell = grid[0][i]
        cell.tile=bkg
        cell.type='background'
        cell.frozen = False
    #generate flakes on row 0
    for i in range(seed):
        col = random.randint(0, size_x-1)
        grid[row][col].tile=current_flake
        grid[row][col].color='#ffffff'
        cell.hasChanged = True

def update_snow():
    #scanning from bottom to top
    for row in range(len(grid)-1,0,-1):
        for col in range(len(grid[y])):
            cell = grid[row][col]
            cellAbove = grid[row-1][col]
            ground = len(grid)-1
            # If cell is frozen then dont touch it...
            if cell.frozen == True:
                #this is a hotfix to make sure we dont freeze a rain tile.Fix the rootcause of this instead!
                if cell.tile != flake:
                    cell.tile=bkg
                    cell.hasChanged=True
                #..unless its rain that is falling.
                if cellAbove.tile == rain:
                    cell.frozen = False
                    cell.tile=bkg
                    cell.hasChanged=True
                    continue

                # But check if the tile above it is a flake, then freeze that too...
                if cellAbove.tile == flake and cellAbove.frozen==False:
                    cellAbove.frozen = True
                    cellAbove.color = (random.randint(100,205),random.randint(200,255),255)
                    cellAbove.hasChanged = True
                    # DEBUG="flakefreeze"
                continue

            # check if the flake lands on object, then freeze it...
            if cell.type == 'object' and cellAbove.tile == flake and cellAbove.frozen==False:
                cellAbove.frozen = True
                cellAbove.color = (random.randint(100,205),random.randint(200,255),255)
                cellAbove.hasChanged = True
                continue

            # check if the flake lands on the ground, then freeze it...
            if row ==ground and cell.tile == flake and cell.frozen==False:
                cell.frozen = True
                cell.color = (random.randint(100,205),random.randint(200,255),255)
                cell.hasChanged = True
                # DEBUG="groundfreeze"
                continue


            # cell has passed all freeze tests, now scroll it down to the ground or onto an object.
            #if cells are background then dont bother...
            if cell.type == 'background' and cellAbove.type == 'background':
                 #compare tile above and current tile,if they are different then scroll.
                if cellAbove.tile != cell.tile:
                    cell.tile = cellAbove.tile
                    cell.color = cellAbove.color
                    cell.hasChanged = True

def update_objects():
    for obj in object_list: # for each object...
        start_x = obj['x']  # x pos of current obj
        start_y = obj['y']  # y pos of current obj
        try:
            for y in range(len(obj['rows'])):#for each row of object
                for x in range(len(obj['rows'][y])): #for each col of row
                    cell = grid[start_y+y][start_x+x]
                    if obj['rows'][y][x] == ' ':    #found a blank in the tile to draw? Make it transparent
                        if cell.type !='object':
                            # cell.type = 'background'
                            cell.tile=bkg
                    else:
                        if cell.tile == obj['rows'][y][x]:
                            cell.hasChanged = False
                            continue
                        else:
                            cell.tile = obj['rows'][y][x]
                            cell.type = 'object'
                            cell.color = obj['color']
                            cell.hasChanged = True
        except IndexError:
            raise OutOfBoundsError(f"Obj {obj['id']} is out of screen (x:{obj['x']},y:{obj['y']})")

def draw_object(obj):
    start_x = obj['x']  # x pos of current obj
    start_y = obj['y']  # y pos of current obj
    try:
        for y in range(len(obj['rows'])):#for each row of object
            for x in range(len(obj['rows'][y])): #for each col of row
                cell = grid[start_y+y][start_x+x]
                if obj['rows'][y][x] == ' ':    #found a blank in the tile to draw? Make it transparent
                    if cell.type !='object':
                        # cell.type = 'background'
                        cell.tile=bkg
                else:
                    if cell.tile == obj['rows'][y][x]:
                        cell.hasChanged = False
                        continue
                    else:
                        cell.tile = obj['rows'][y][x]
                        cell.type = 'object'
                        cell.color = obj['color']
                        cell.hasChanged = True
    except IndexError:
        raise OutOfBoundsError(f"Obj {obj['id']} is out of screen (x:{obj['x']},y:{obj['y']})")

def wind(velocity,direction):
    global current_flake,DEBUG

    if velocity*direction==0:return #now wind, no reason to do calculations

    for row in range(1,len(grid)):
        if direction < 0:   #blow west
            for col in range(len(grid[row])):
                cell = grid[row][col]
                try:
                    cellToLeft = grid[row][col+(direction*velocity)]
                    cellToRight = grid[row][col-(direction*velocity)]
                except IndexError:
                    continue
                # Check if there's a rollover problem ahead and kill the flake before it hits the wall
                if col == 1:
                    cell.tile=bkg
                    cell.hasChanged=True
                    continue

                if cell.type == 'background' and cell.tile == current_flake and cell.frozen == False and cellToLeft.frozen == False: #current cell is a flake and not frozen
                    # make sure we dont move a flake into an object or rollover from left to right side of screen(due to list rollover)
                    if cellToLeft.type !='object' and cellToLeft.type !='fire' and col+(direction*velocity) > 0:
                        cellToLeft.tile = cell.tile
                        cellToLeft.hasChanged=True
                        #cell to the right is not a object
                        if cellToRight.type !='object' and cellToRight.type != 'fire':
                            cell.tile=cellToRight.tile
                            cell.hasChanged=True

        if direction > 0:   #blow east
            for col in range(len(grid[row])-1,0,-1):
                cell = grid[row][col]
                try:
                    cellToLeft = grid[row][col-(direction*velocity)]
                    cellToRight = grid[row][col+(direction*velocity)]
                except IndexError:
                    continue
                # Check if there's a rollover problem ahead and kill the flake before it hits the wall
                if col == len(grid[row])-2:
                    cell.tile=bkg
                    cell.hasChanged=True
                    continue

                if cell.type == 'background' and cell.tile == current_flake and cell.frozen == False and cellToRight.frozen == False: #current cell is a flake and not frozen
                    # make sure we dont move a flake into an object or rollover from left to right side of screen(due to list rollover)
                    if cellToRight.type !='object' and cellToRight.type != 'fire' and col+(direction*velocity) > 0:
                        cellToRight.tile = cell.tile
                        cellToRight.hasChanged=True
                        #cell to the right is not a object
                        if cellToLeft.type !='object' and cellToLeft.type !='fire':
                            cell.tile=cellToLeft.tile
                            cell.hasChanged=True

def melt_pillar(pillar_size):
    global DEBUG
    pillar_count=0
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            cell = grid[row][col]
            if cell.frozen:
                #check n cells above the current cell for flakes(n=pillar_size)
                for n in range(pillar_size):
                    cell_above = grid[row-n][col]
                    if cell_above.frozen == True:
                        pillar_count+=1
                #if we find enough frozen tiles above the base then lets
                #melt them, else continue the search for frozen flakes
                if pillar_count < pillar_size-1:
                    pillar_count=0
                    continue

                #ok, we have a large pillar now, lets melt it randomly
                melt=random.randint(0,pillar_size)
                for n in range(melt):
                    cell_to_melt = grid[row-pillar_size+n][col]
                    cell_to_melt.tile=bkg
                    cell_to_melt.frozen=False

def debug_snow():
    #make a debug pillar
    for row in range(1,2):
        cell = grid[row][5]
        cell.tile=flake
        cell.color='#0ffa3f'
        cell.type='background'
        cell.hasChanged=True
    #make a debug pillar
    for row in range(10,20):
        cell = grid[row][12]
        cell.tile=flake
        cell.color='#0ffa3f'
        cell.type='background'
        cell.hasChanged=True

def draw_status():
    global FRAME_RATE, DEBUG
    change_counter=0
    freezecnt=0
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            cell = grid[row][col]
            if cell.frozen: freezecnt+=1
            if cell.hasChanged: change_counter+=1

    moveCursor(len(grid),0)
    print(f"INFO:{DEBUG} Wind: {wind_speed}m/s Gridsize:{size_x}x{size_y} Frozen flakes:{freezecnt} Changed tiles this frame:{change_counter}   ")
    delta = (dt.datetime(2020, 12, 24) - dt.datetime.now()).days +1
    print(f'Today it is {delta} days left until a fat man arrives through the chimney...')

def draw():
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            cell = grid[row][col]
            if cell.hasChanged:
                cell.hasChanged=False
                if cell.color is not None:
                    moveCursor(row,col)
                    print(color(f"{cell.tile}",cell.color))

def animate_candle(candle):
    #Change color of the flame
    #Find the pixels for the flame and set them to hasChanged so that
    #the draw function knows to update the pixels
    for obj in object_list:
        if obj['id']==f'candle{candle}_flame':
            start_x = obj['x']  # x pos of current obj
            start_y = obj['y']  # y pos of current obj
            for y in range(len(obj['rows'])):#for each row of object
                for x in range(len(obj['rows'][y])): #for each col of row
                    cell = grid[start_y+y][start_x+x]
                    if obj['rows'][y][x] != ' ':
                        cell.color = (255,random.randint(100,200),random.randint(0,20))
                        cell.hasChanged = True
                        cell.type='fire'

def weather_control(delay):
    global weather_time,current_flake,current_weather, wind_dir, wind_speed, wind_dir_time, wind_speed_time, wind_speed_inc, wind_dir_inc, DEBUG


    if time.time() - wind_speed_time > 0.5:
        if wind_dir !=0:
            # Let's vary the windspeed up and down...
            if wind_speed <= 1:    wind_speed_inc = 1
            if wind_speed >= 5:   wind_speed_inc = -1
            wind_speed += wind_speed_inc
            wind_speed_time =time.time()


    if time.time() - wind_dir_time > delay/3:

        #set the wind direction in here
        if wind_dir > 0: wind_dir_inc = -1
        if wind_dir < 0: wind_dir_inc = 1
        wind_dir += wind_dir_inc
        wind_speed=0 if wind_dir==0 else 1
        # if wind_dir==0:heavy_rain='|'
        # if wind_dir==1:heavy_rain='\\'
        # if wind_dir==-1:heavy_rain='/'
        wind_dir_time=time.time()


    # Let's handle the weather(flake type)
    if time.time() - weather_time > delay:
        weather_list=[rain,small_flake,flake,small_flake]
        current_flake = weather_list[current_weather]
        if current_weather==len(weather_list)-1:
            current_weather=0
        else:
            current_weather+=1
        weather_time=time.time()

def advent_check():
    if (dt.datetime(2020, 11, 29) - dt.datetime.now()).days < 0:
        animate_candle(1)
    if (dt.datetime(2020, 12, 6) - dt.datetime.now()).days < 0:
        animate_candle(2)
    if (dt.datetime(2020, 12, 13) - dt.datetime.now()).days < 0:
        animate_candle(3)
    if (dt.datetime(2020, 12, 20) - dt.datetime.now()).days < 0:
        animate_candle(4)


def simulate_winter():
    global wind_dir, wind_speed
    update_objects()    #only needed once, and if they change call it again.
    # debug_snow()
    while True:
        draw_status()
        draw()
        weather_control(180)
        generate_flakes(1)
        wind(wind_speed,wind_dir)
        update_snow()
        melt_pillar(10)
        advent_check()

        time.sleep(1/FRAME_RATE)

if __name__ == '__main__':
    simulate_winter()
