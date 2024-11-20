import random
class Rat:
    def __init__(self, env, bot_position):
        self.env = env
        self.position = self.env.place_random_open_cell(avoid_cells=[bot_position])

    def move_randomly(self):
        neighbors = self.env.get_neighbor_cells(self.position[0], self.position[1])
        open_neighbors = [cell for cell in neighbors if self.env.matrix[cell[0]][cell[1]] == 0]
        if open_neighbors:
            self.position = random.choice(open_neighbors)


