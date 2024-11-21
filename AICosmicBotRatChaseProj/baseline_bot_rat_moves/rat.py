import random
class Rat:
    def __init__(self, environment, bot_loc):
        self.environment = environment
        self.loc = self.environment.position_random_open_cell(avoid_cells=[bot_loc])

    def move_randomly(self):
        neighbors = self.environment.get_neighbor_cells(self.loc[0], self.loc[1])
        open_neighbors = [cell for cell in neighbors if self.environment.matrix[cell[0]][cell[1]] == 0]
        if open_neighbors:
            self.loc = random.choice(open_neighbors)


