import math



class RatKnowledgeBase:
    def __init__(self, env, bot_position, alpha=0.5):
        self.env = env
        self.bot_position = bot_position
        self.alpha = alpha
        self.rat_detection_probabilities = self.calculate_detection_probabilities()

    def manhattan_distance(self, pos1, pos2):
        """Calculate the Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def calculate_detection_probabilities(self):
        """Calculate detection probabilities for each target cell and its neighboring open cells."""
        detection_probs = {}
        for r in range(1, self.env.size - 1):
            for c in range(1, self.env.size - 1):
                if self.env.matrix[r][c] == 0:  # Only consider open cells as potential target cells
                    # Calculate detection probability based on distance from the bot
                    distance = self.manhattan_distance(self.bot_position, (r, c))
                    probability = math.exp(-(self.alpha * (distance - 1)))
                    detection_probs[(r, c)] = probability

                    # Include open neighbors of each target cell
                    open_neighbors = self.get_open_neighbors((r, c))
                    for neighbor in open_neighbors:
                        if neighbor not in detection_probs:
                            neighbor_distance = self.manhattan_distance(self.bot_position, neighbor)
                            neighbor_prob = math.exp(-(self.alpha * (neighbor_distance - 1)))
                            detection_probs[neighbor] = neighbor_prob

        return detection_probs

    def get_open_neighbors(self, cell):
        """Retrieve all open neighboring cells for a given cell."""
        neighbors = self.env.get_neighbor_cells(cell[0], cell[1])
        return [(r, c) for r, c in neighbors if self.env.matrix[r][c] == 0]

    def filter_to_target_cells(self, target_cells):
        """Filter rat detection probabilities to include only the target cells and their open neighbors."""
        filtered_probs = {}
        for cell in target_cells:
            filtered_probs[cell] = self.rat_detection_probabilities.get(cell, 0)
            for neighbor in self.get_open_neighbors(cell):
                filtered_probs[neighbor] = self.rat_detection_probabilities.get(neighbor, 0)

        self.rat_detection_probabilities = filtered_probs
        print(f"Rat Knowledge Base updated with target cells and neighbors: {self.rat_detection_probabilities}")

    def update_target_cells(self, new_bot_position):
        """Update detection probabilities based on bot's new position, including target cells and open neighbors."""
        updated_probs = {}
        for cell in self.rat_detection_probabilities:
            distance = self.manhattan_distance(new_bot_position, cell)
            probability = math.exp(-(self.alpha * (distance - 1)))
            updated_probs[cell] = probability
        self.rat_detection_probabilities = updated_probs

    