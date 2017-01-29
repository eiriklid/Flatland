from Tkinter import *
from random import *
import sys
import math


#Tile const
OPEN    = 0
FOOD    = 1
POISON  = 2
WALL    = 3

TILESIZE = 50

#Dir const
DIR_EAST    = (1,0)
DIR_SOUTH   = (0,1)
DIR_WEST    = (-1,0)
DIR_NORTH   = (0,-1)

score = 0
root = Tk()
class Map:
    def __init__(self,master,mapsize):
        self.mapsize = mapsize
        self.grid = [[0 for x in range(mapsize)] for y in range(mapsize)]
        self.canvas = Canvas(master, width=TILESIZE*mapsize, height=TILESIZE*mapsize)

        # vertical lines at an interval of "TILESIZE" pixel
        # horizontal lines at an interval of "TILESIZE" pixel
        for x in range(TILESIZE, TILESIZE*mapsize, TILESIZE):
            self.canvas.create_line(x, 0, x, TILESIZE*mapsize, fill="#476042")
        for y in range(TILESIZE, TILESIZE*mapsize, TILESIZE):
            self.canvas.create_line(0, y, TILESIZE*mapsize, y, fill="#476042")

        self.canvas.pack()

        for i in range(mapsize):
            for j in range(mapsize):
                if(i == 0 or j == 0 or i== mapsize-1 or j == mapsize-1):
                    self.grid[i][j] = Tile(self.canvas, WALL, i, j)

                else:
                    self.grid[i][j] = Tile(self.canvas,random_type(),i,j)

def random_type():
    rand_val = randint(0, 1)
    if rand_val == 1:
        return FOOD
    else:
        rand_val = randint(0,1)
        if rand_val == 1:
            return POISON
    return OPEN



class Tile:
    def __init__(self,canvas,type,x,y):
        self.type = type
        self.x = x
        self.y = y
        self.val = 0
        if type == FOOD:
            self.shape = canvas.create_oval(x*TILESIZE, y*TILESIZE,(x+1)*TILESIZE, (y+1)*TILESIZE, fill = "#009900")
            self.val = 1
        elif type == POISON:
            self.shape = canvas.create_oval(x*TILESIZE, y*TILESIZE,(x+1)*TILESIZE, (y+1)*TILESIZE, fill = "orange")
            self.val = -4
        elif type == WALL:
            self.shape = canvas.create_oval(x*TILESIZE, y*TILESIZE,(x+1)*TILESIZE, (y+1)*TILESIZE, fill = "grey")
            self.val = -100



class Arrow:
    def __init__(self,canvas,fromTile,toTile):
        canvas.create_line( fromTile[0]*TILESIZE+TILESIZE/2,
                            fromTile[1]*TILESIZE+TILESIZE/2,
                            toTile[0]*TILESIZE+TILESIZE/2,
                            toTile[1]*TILESIZE+TILESIZE/2,
                            arrow = LAST)

class Agent:
    def __init__(self,map):
        self.set_new_map(map)

        self.weights = [[uniform(0,0.001) for x in range(12)] for y in range(3)]


    def set_new_map(self,map):
        self.x = randint(1, map.mapsize - 2)
        self.y = randint(1, map.mapsize - 2)

        #print "Spawn x",self.x, "y:", self.y
        self.dir = DIR_NORTH
        self.map = map
        self.eat_tile(map.grid[self.x][self.y])
        self.draw_agent()


    def get_neighbours(self):
        ret_list = []
        if self.dir[0] != 0: #facing east/west
            ret_list.append( self.map.grid[self.x+self.dir[0]][self.y])  #forward
            ret_list.append( self.map.grid[self.x][self.y+self.dir[0]])  #right
            ret_list.append( self.map.grid[self.x][self.y-self.dir[0]])  #left


        else: #facing north/south
            ret_list.append( self.map.grid[self.x][self.y+self.dir[1]])  #forward
            ret_list.append( self.map.grid[self.x-self.dir[1]][self.y])  #right
            ret_list.append( self.map.grid[self.x+self.dir[1]][self.y])  #left


        return ret_list


    def choose_action(self):
        neighbours = self.get_neighbours()

        food_tiles = [elem for elem in neighbours if elem.type == FOOD]
        poison_tiles = [elem for elem in neighbours if elem.type == POISON]
        open_tiles = [elem for elem in neighbours if elem.type == OPEN]
        wall_tiles = [elem for elem in neighbours if elem.type == WALL]

        #print "\nFood:",food_tiles
        #print "Poison:",poison_tiles
        #print "Open:",open_tiles
        #print "Wall:",wall_tiles

        if food_tiles != []:
            return food_tiles[0]#choice(food_tiles)
        else:
            if open_tiles != []:
                return open_tiles[0] #choice(open_tiles)
            else:
                if poison_tiles != []:
                    return poison_tiles[0] #choice(poison_tiles)
                else:
                    print "Only walls..."
                    sys.exit() #Terminate if wall tiles is the only pickable

    def choose_neural_action(self):
        neighbours = self.get_neighbours()
        state_input = self.get_neural_input()

        output = self.get_neural_output(state_input)
        max_output_index = output.index(max(output))
        return neighbours[max_output_index]

    def get_neural_input(self):
        neighbours = self.get_neighbours()

        state_input = [0 for x in range(12)]
        for i, tile in enumerate(neighbours):
            if tile.type == OPEN:
                state_input[(i * 4)] = 1

            elif tile.type == FOOD:
                state_input[1+(i*4)] = 1

            elif tile.type == POISON:
                state_input[2 + (i * 4)] = 1

            elif tile.type == WALL:
                state_input[3 + (i * 4)] = 1

        return state_input

    def get_neural_output(self, state):
        output = [0 for y in range(3)]
        for j, x_j in enumerate(state):
            for i in range(len(output)):
                output[i] = output[i]+ (self.weights[i][j] * x_j)

        return output

    def update_neural_weights(self):
        state = self.get_neural_input()
        output = self.get_neural_output(state)

        #print  "output: ", output

        eta = 0.01
        correct_choice = [0 for y in range(3)]
        neighbours = self.get_neighbours()
        teacher_tile = self.choose_action()

        for i,elem in enumerate(neighbours):
            if teacher_tile == elem:
                correct_choice[i] = 1
                break # no need to check the rest

        #print "correct choice: ", correct_choice
        exp_output = [math.exp(y) for y in output]
        exp_output_sum = sum(exp_output)
        #print "exp_output:",exp_output,"exp_output_sum: ",exp_output_sum

        delta = [correct_choice[i]-(exp_output[i]/exp_output_sum) for i in range(len(output))]

        #print "delta: ",delta
        #print ('\n'.join([' '.join(['{:4}'.format(item) for item in row]) for row in agent.weights]))

        for j, x_j in enumerate(state):
            for i, elem in enumerate(output):

                self.weights[i][j] = self.weights[i][j] + (eta*delta[i]*x_j)

        #rint "After"
        #print ('\n'.join([' '.join(['{:4}'.format(item) for item in row]) for row in agent.weights]))

    def move(self,x,y):
        #Should only be able to move to neighbour square
        if( abs(self.x-x)==1 ^ (abs(self.y-y)==1)): #xor
            #Set new direction
            if(self.y == y):
                if(self.x < x):
                    self.dir = DIR_EAST
                else:
                    self.dir = DIR_WEST
            else:
                if(self.y < y):
                    self.dir = DIR_SOUTH
                else:
                    self.dir = DIR_NORTH
        else:
            print "Move Error!"
            return


        tile = self.map.grid[x][y]
        self.eat_tile(tile)

        self.map.canvas.delete(self.shape)
        Arrow(self.map.canvas,(self.x,self.y),(x,y))
        self.x = x
        self.y = y
        #print "x: ",x, "y: ",y
        self.draw_agent()

    def eat_tile(self,tile):

        global score
        score = score + tile.val
        if tile.type == FOOD:
            self.map.canvas.itemconfig(tile.shape, fill='#99FF99')
            tile.type = OPEN

        elif tile.type == POISON:
            self.map.canvas.itemconfig(tile.shape, fill='red')
            tile.type = OPEN

        #elif tile.type == WALL:
            #print "NOOOOO!"

        tile.val = 0

    def draw_agent(self):
        if self.dir == DIR_EAST:
            self.shape = self.map.canvas.create_polygon([self.x*TILESIZE + TILESIZE/2,self.y*TILESIZE,
                                                   self.x * TILESIZE + TILESIZE / 2,(self.y+1)*TILESIZE,
                                                   (self.x+1) * TILESIZE ,self.y*TILESIZE + TILESIZE/2])

        elif self.dir == DIR_SOUTH:
            self.shape = self.map.canvas.create_polygon([self.x*TILESIZE ,self.y*TILESIZE + TILESIZE/2,
                                                   self.x * TILESIZE + TILESIZE / 2,(self.y+1)*TILESIZE,
                                                   (self.x+1) * TILESIZE ,self.y*TILESIZE + TILESIZE/2])
        elif self.dir == DIR_WEST:
            self.shape = self.map.canvas.create_polygon([self.x*TILESIZE ,self.y*TILESIZE + TILESIZE/2,
                                                   self.x * TILESIZE + TILESIZE / 2,(self.y+1)*TILESIZE,
                                                   self.x * TILESIZE + TILESIZE/2,self.y*TILESIZE])
        elif self.dir == DIR_NORTH:
            self.shape = self.map.canvas.create_polygon([self.x*TILESIZE ,self.y*TILESIZE + TILESIZE/2,
                                                   self.x * TILESIZE + TILESIZE / 2,self.y*TILESIZE,
                                                   (self.x+1) * TILESIZE ,self.y*TILESIZE+ TILESIZE/2])


map = Map(root,12)
agent = Agent(map)

def train_agent(agent):
    for i in range(100):
        map = Map(root, 12)
        agent.set_new_map(map)

        for j in range(50):
            tile = agent.choose_neural_action()
            agent.update_neural_weights()
            agent.move(tile.x,tile.y)
            if tile.type ==WALL: #Stop simulation if wall is hit
                break



    #print ('\n'.join([' '.join(['{:4}'.format(item) for item in row]) for row in agent.weights]))


def test_agent(agent):
    global score
    score = 0


    for i in range(1000):

        map = Map(root,12)
        agent.set_new_map(map)
        for j in range(50):
            tile = agent.choose_neural_action()
            agent.move(tile.x, tile.y)
            if tile.type ==WALL: #Stop simulation if wall is hit
                break


    print "score", score/1000.0


for l in range(22):
    train_agent(agent)
    test_agent(agent)

root.mainloop()
