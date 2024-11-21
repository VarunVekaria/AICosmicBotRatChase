import random
# from ship_environment_logic import ShipEnvironment

class Rat:
    def __init__(self, environment, bot_loc):
        self.environment = environment
        self.loc = self.environment.position_random_open_cell(avoid_cells=[bot_loc])

    def move(self):
        """Move the rat to a random neighboring open cell."""
        # Get neighboring cells
        neighbors = self.environment.get_neighbor_cells(*self.loc)
        open_neighbors = [(r, c) for r, c in neighbors if self.environment.matrix[r][c] == 0]

        # Move to a random open neighbor, if any exist
        if open_neighbors:
            self.loc = random.choice(open_neighbors)
            print(f"Rat moved to {self.loc}")