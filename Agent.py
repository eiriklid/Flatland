import random
import sys
import math

import Map
import constants as const


class Agent:
    def __init__(self,map):
        self.score = 0
        self.set_new_map(map)
        self.weights = [[random.uniform(0,0.001) for x in range(12*const.SENSOR_RANGE)] for y in range(3)]

    def set_new_map(self,map):
        self.x = random.randint(4, map.mapsize - 5)
        self.y = random.randint(4, map.mapsize - 5)
        self.dir = const.DIR_NORTH
        self.map = map
        self.eat_tile(map.grid[self.x][self.y])
        self.draw_agent()

    def get_neighbours(self):
        return self.get_neighbours_at_tile(self.x,self.y,self.dir)

    def get_neighbours_at_tile(self,x,y,dir):
        ret_list = []
        if dir[0] != 0: #facing east/west
            for step in range(1,const.SENSOR_RANGE+1,1):
                ret_list.append( self.map.grid[x+dir[0]*step][y])  #forward
                ret_list.append( self.map.grid[x][y+dir[0]*step])  #right
                ret_list.append( self.map.grid[x][y-dir[0]*step])  #left

        else: #facing north/south
            for step in range(1,const.SENSOR_RANGE+1,1):
                ret_list.append( self.map.grid[x][y+dir[1]*step])  #forward
                ret_list.append( self.map.grid[x-dir[1]*step][y])  #right
                ret_list.append( self.map.grid[x+dir[1]*step][y])  #left

        return ret_list


    def choose_action(self):
        neighbours = self.get_neighbours()

        food_tiles = [elem for elem in neighbours if elem.type == const.FOOD]
        poison_tiles = [elem for elem in neighbours if elem.type == const.POISON]
        open_tiles = [elem for elem in neighbours if elem.type == const.OPEN]
        wall_tiles = [elem for elem in neighbours if elem.type == const.WALL]



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
        return self.choose_neural_action_at_tile(self.x,self.y,self.dir)

    def choose_neural_action_at_tile(self,x,y,dir):
        neighbours = self.get_neighbours_at_tile(x,y,dir)
        state_input = self.get_neural_input_at_tile(x,y,dir)

        output = self.get_neural_output(state_input)
        max_output_index = output.index(max(output))
        return neighbours[max_output_index]

    def get_neural_input(self):
        return self.get_neural_input_at_tile(self.x,self.y,self.dir)

    def get_neural_input_at_tile(self,x,y,dir):
        neighbours = self.get_neighbours_at_tile(x,y,dir)

        state_input = [0 for x in range(12*const.SENSOR_RANGE)]
        for i, tile in enumerate(neighbours):
            if tile.type == const.OPEN:
                state_input[(i * 4)] = 1

            elif tile.type == const.FOOD:
                state_input[1+(i*4)] = 1

            elif tile.type == const.POISON:
                state_input[2 + (i * 4)] = 1

            elif tile.type == const.WALL:
                state_input[3 + (i * 4)] = 1

        return state_input

    def get_neural_output(self, state):
        output = [0 for y in range(3)]
        for j, x_j in enumerate(state):
            for i, elem in enumerate(output):
                output[i] = elem + self.weights[i][j] * x_j

        return output

    def update_neural_weights(self,rule):
        s = self.get_neural_input()
        output = self.get_neural_output(s)

        # Widrow Hoff
        if(rule == "Supervised"):
            neighbours = self.get_neighbours()
            teacher_tile = self.choose_action()
            correct_choice = [1 if teacher_tile == neighbours[i] else 0 for i in range(3)]

            exp_output = [math.exp(y) for y in output]
            exp_output_sum = sum(exp_output)

            delta = [correct_choice[i] - (exp_output[i] / exp_output_sum) for i in range(len(output))]

        elif(rule == "Reinforced") :
            #Q-learning
            Q_s_a = max(output)
            neighbours = self.get_neighbours()

            B_tile = self.choose_neural_action()
            r = B_tile.val
            B_dir = self.calc_dir(B_tile.x, B_tile.y)
            s_marked = self.get_neural_input_at_tile(B_tile.x, B_tile.y,B_dir)
            Q_s_a_marked = max(self.get_neural_output(s_marked))

            delta = []

            gamma = 0.9
            for i in range(3):
                if (B_tile == neighbours[i]) :
                    delta.append(r + gamma*Q_s_a_marked-Q_s_a)
                else:
                    delta.append(0)
        else:
            print "Not known learning type"
            sys.exit()


        eta = 0.01
        for j, x_j in enumerate(s):
            for i, elem in enumerate(output):

                self.weights[i][j] = self.weights[i][j] + (eta*delta[i]*x_j)


    def move(self,x,y):
        self.dir = self.calc_dir(x,y)
        tile = self.map.grid[x][y]
        self.eat_tile(tile)

        self.map.canvas.delete(self.shape)
        Map.Arrow(self.map.canvas,(self.x,self.y),(x,y))
        self.x = x
        self.y = y
        self.draw_agent()

    def eat_tile(self,tile):
        self.score = self.score + tile.val

        if tile.type == const.FOOD:
            self.map.canvas.itemconfig(tile.shape, fill='#99FF99')
            tile.type = const.OPEN

        elif tile.type == const.POISON:
            self.map.canvas.itemconfig(tile.shape, fill='red')
            tile.type = const.OPEN

        tile.val = 0

    def calc_dir(self,x,y):
        if (abs(self.x - x) == 1 ^ (abs(self.y - y) == 1)):  # xor
            # Get new direction
            if (self.y == y):
                if (self.x < x):
                    return const.DIR_EAST
                else:
                    return const.DIR_WEST
            else:
                if (self.y < y):
                    return const.DIR_SOUTH
                else:
                    return const.DIR_NORTH
        else:
            print "Move Error!",self.x,self.y,x,y
            sys.exit()

    def draw_agent(self):
        self.shape = Map.draw_agent(self.x,self.y,self.dir,self.map)


    def train_agent(self,master,type):
        for i in range(100):
            map = Map.Map(master, 12+2*const.SENSOR_RANGE)
            self.set_new_map(map)

            for j in range(50):
                tile = self.choose_neural_action()
                self.update_neural_weights(type)
                self.move(tile.x,tile.y)
                if tile.type == const.WALL: #Stop simulation if wall is hit
                    break

    def test_agent(self,master):
        self.score = 0


        for i in range(1000):

            map = Map.Map(master,12+2*const.SENSOR_RANGE)
            self.set_new_map(map)
            for j in range(50):
                tile = self.choose_neural_action()
                self.move(tile.x, tile.y)
                if tile.type == const.WALL: #Stop simulation if wall is hit
                    break


        print "score", self.score/1000.0

    def test_baseline_agent(self, master):
        self.score = 0

        for i in range(1000):


            for j in range(50):
                tile = self.choose_action()
                self.move(tile.x, tile.y)
                if tile.type == const.WALL:  # Stop simulation if wall is hit
                    break

            map = Map.Map(master, 12)
            self.set_new_map(map)

        print "score", self.score / 1000.0
