import random
# from ship_environment_logic import ShipEnvironment

class Rat:
    def __init__(self, env, bot_position):
        self.env = env
        self.position = self.env.place_random_open_cell(avoid_cells=[bot_position])

    def move(self):
        """Move the rat to a random neighboring open cell."""
        # Get neighboring cells
        neighbors = self.env.get_neighbor_cells(*self.position)
        open_neighbors = [(r, c) for r, c in neighbors if self.env.matrix[r][c] == 0]

        # Move to a random open neighbor, if any exist
        if open_neighbors:
            self.position = random.choice(open_neighbors)
            print(f"Rat moved to {self.position}")