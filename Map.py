import Tkinter as tk
import random

import constants as const

class Map:
    def __init__(self,master,mapsize):
        self.mapsize = mapsize
        self.grid = [[0 for x in range(mapsize)] for y in range(mapsize)]
        self.canvas = tk.Canvas(master, width=const.TILESIZE*mapsize, height=const.TILESIZE*mapsize)
        # vertical lines at an interval of "const.TILESIZE" pixel
        # horizontal lines at an interval of "const.TILESIZE" pixel
        for x in range(const.TILESIZE, const.TILESIZE*mapsize, const.TILESIZE):
            self.canvas.create_line(x, 0, x, const.TILESIZE*mapsize, fill="#476042")
        for y in range(const.TILESIZE, const.TILESIZE*mapsize, const.TILESIZE):
            self.canvas.create_line(0, y, const.TILESIZE*mapsize, y, fill="#476042")
        self.canvas.pack()

        wallsize =(mapsize-10)/2
        for i in range(mapsize):
            for j in range(mapsize):
                if(i <= wallsize-1 or j <= wallsize-1 or i >= mapsize-wallsize or j >= mapsize-wallsize):
                    self.grid[i][j] = Tile(self.canvas, const.WALL, i, j)

                else:
                    self.grid[i][j] = Tile(self.canvas,random_type(),i,j)

def random_type():
    rand_val = random.randint(0, 1)
    if rand_val == 1:
        return const.FOOD
    else:
        rand_val = random.randint(0,1)
        if rand_val == 1:
            return const.POISON
    return const.OPEN



class Tile:
    def __init__(self,canvas,type,x,y):
        self.type = type
        self.x = x
        self.y = y
        self.val = 0
        if type == const.FOOD:
            self.shape = canvas.create_oval(x*const.TILESIZE, y*const.TILESIZE,(x+1)*const.TILESIZE, (y+1)*const.TILESIZE, fill = "#009900")
            self.val = 1
        elif type == const.POISON:
            self.shape = canvas.create_oval(x*const.TILESIZE, y*const.TILESIZE,(x+1)*const.TILESIZE, (y+1)*const.TILESIZE, fill = "orange")
            self.val = -4
        elif type == const.WALL:
            self.shape = canvas.create_oval(x*const.TILESIZE, y*const.TILESIZE,(x+1)*const.TILESIZE, (y+1)*const.TILESIZE, fill = "grey")
            self.val = -100



class Arrow:
    def __init__(self,canvas,fromTile,toTile):
        canvas.create_line( fromTile[0]*const.TILESIZE+const.TILESIZE/2,
                            fromTile[1]*const.TILESIZE+const.TILESIZE/2,
                            toTile[0]*const.TILESIZE+const.TILESIZE/2,
                            toTile[1]*const.TILESIZE+const.TILESIZE/2,
                            arrow = tk.LAST)


def draw_agent(x,y,dir,map):
    if dir == const.DIR_EAST:
        return map.canvas.create_polygon([x*const.TILESIZE + const.TILESIZE/2,y*const.TILESIZE,
                                               x * const.TILESIZE + const.TILESIZE / 2,(y+1)*const.TILESIZE,
                                               (x+1) * const.TILESIZE ,y*const.TILESIZE + const.TILESIZE/2])

    elif dir == const.DIR_SOUTH:
        return map.canvas.create_polygon([x*const.TILESIZE ,y*const.TILESIZE + const.TILESIZE/2,
                                               x * const.TILESIZE + const.TILESIZE / 2,(y+1)*const.TILESIZE,
                                               (x+1) * const.TILESIZE ,y*const.TILESIZE + const.TILESIZE/2])
    elif dir == const.DIR_WEST:
        return map.canvas.create_polygon([x*const.TILESIZE ,y*const.TILESIZE + const.TILESIZE/2,
                                               x * const.TILESIZE + const.TILESIZE / 2,(y+1)*const.TILESIZE,
                                               x * const.TILESIZE + const.TILESIZE/2,y*const.TILESIZE])
    elif dir == const.DIR_NORTH:
        return map.canvas.create_polygon([x*const.TILESIZE ,y*const.TILESIZE + const.TILESIZE/2,
                                               x * const.TILESIZE + const.TILESIZE / 2,y*const.TILESIZE,
                                               (x+1) * const.TILESIZE ,y*const.TILESIZE+ const.TILESIZE/2])




