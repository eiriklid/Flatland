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
