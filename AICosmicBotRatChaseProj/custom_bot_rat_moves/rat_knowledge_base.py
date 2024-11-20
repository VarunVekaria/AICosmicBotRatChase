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
        """Calculate and store the probability of detecting a ping for each open cell."""
        detection_probs = {}
        for r in range(1, self.env.size - 1):
            for c in range(1, self.env.size - 1):
                if self.env.matrix[r][c] == 0:  # Only consider open cells
                    distance = self.manhattan_distance(self.bot_position, (r, c))
                    probability = math.exp(-(self.alpha * (distance - 1)))
                    detection_probs[(r, c)] = probability
                    # print(f"Calculated ping detection probability at {(r, c)}: {probability}")
        return detection_probs
    
    def filter_to_target_cells(self, target_cells):
        """Filter rat detection probabilities to include only the target cells."""
        self.rat_detection_probabilities = {cell: prob for cell, prob in self.rat_detection_probabilities.items() if cell in target_cells}
        print(f"Rat Knowledge Base updated with target cells: {self.rat_detection_probabilities}")

    def update_target_cells(self, new_bot_position):
        """Update detection probabilities for only the target cells based on the bot's new position."""
        updated_probs = {}
        for cell in self.rat_detection_probabilities:
            distance = self.manhattan_distance(new_bot_position, cell)
            probability = math.exp(-(self.alpha * (distance - 1)))
            updated_probs[cell] = probability
            # print(f"Updated ping detection probability at {cell}: {probability}")
        self.rat_detection_probabilities = updated_probs
 