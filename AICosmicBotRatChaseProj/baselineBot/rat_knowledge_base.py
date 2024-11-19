import math
ALPHA = 0.2

class RatKnowledgeBase:
    def __init__(self, env, bot_position):
        self.env = env
        self.bot_position = bot_position  # Start with the bot's initial position
        self.rat_detection_probabilities = self.initialize_detection_probabilities()



    def initialize_detection_probabilities(self):
        detection_probs = {}
        for r in range(1, self.env.size - 1):
            for c in range(1, self.env.size - 1):
                if self.env.matrix[r][c] == 0:
                    distance = self.manhattan_distance(self.bot_position, (r, c))
                    probability = math.exp(-(ALPHA * (distance - 1)))
                    detection_probs[(r, c)] = probability
        print(f"Initial Rat Knowledge Base: {detection_probs}")
        return detection_probs

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def filter_cells_by_distance(self, distance, greater_than=False):
        """Keep only cells that are either within or beyond a specified distance from the bot's current position."""
        print(f"Filtering cells with {'distance >= ' if greater_than else 'distance <= '}{distance}")
        # Display distances for debugging
        for cell in self.rat_detection_probabilities:
            cell_distance = self.manhattan_distance(self.bot_position, cell)
            print(f"Cell {cell} with distance {cell_distance}")

        if greater_than:
            # Retain only cells with distance >= specified distance
            self.rat_detection_probabilities = {
                cell: prob for cell, prob in self.rat_detection_probabilities.items()
                if self.manhattan_distance(self.bot_position, cell) >= distance
            }
        else:
            # Retain only cells with distance <= specified distance
            self.rat_detection_probabilities = {
                cell: prob for cell, prob in self.rat_detection_probabilities.items()
                if self.manhattan_distance(self.bot_position, cell) <= distance
            }
        
        # Log filtered results
        print(f"Filtered Rat Knowledge Base (dist {'>=' if greater_than else '<='} {distance}): {self.rat_detection_probabilities}")

    def update_target_cells(self, new_bot_position):
        """Update detection probabilities based on a new bot position."""
        self.bot_position = new_bot_position  # Set new bot position
        updated_probs = {}
        for cell in self.rat_detection_probabilities:
            distance = self.manhattan_distance(new_bot_position, cell)
            probability = math.exp(-(ALPHA * (distance - 1)))
            updated_probs[cell] = probability
        self.rat_detection_probabilities = updated_probs
        print(f"Updated Rat Knowledge Base: {self.rat_detection_probabilities}")

    def highest_probability_ping(self, bot_position, rat_position):
        distance = self.manhattan_distance(bot_position, rat_position)
        return math.exp(-(ALPHA * (distance - 1)))

