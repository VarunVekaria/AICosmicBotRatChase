import math
ALPHA = 0.2

class RatKnowledgeBase:
    def __init__(self, environment, bot_loc):
        self.environment = environment
        self.bot_loc = bot_loc  # Starting with the bot's initial location
        self.rat_detection_probabilities = self.initialize_detection_probabilities()



    def initialize_detection_probabilities(self):
        detection_probs = {}
        for r in range(1, self.environment.size - 1):
            for c in range(1, self.environment.size - 1):
                if self.environment.matrix[r][c] == 0:
                    dist = self.manhattan_dist(self.bot_loc, (r, c))
                    probability = math.exp(-(ALPHA * (dist - 1)))
                    detection_probs[(r, c)] = probability
        print(f"Initial Rat Knowledge Base: {detection_probs}")
        return detection_probs

    def manhattan_dist(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def filter_cells_by_dist(self, dist, greater_than=False):
        #Here we are filtering according to filter distance
        print(f"Filtering cells with {'dist >= ' if greater_than else 'dist <= '}{dist}")
        
        for cell in self.rat_detection_probabilities:
            cell_dist = self.manhattan_dist(self.bot_loc, cell)
            print(f"Cell {cell} with dist {cell_dist}")

        if greater_than:
            
            self.rat_detection_probabilities = {
                cell: prob for cell, prob in self.rat_detection_probabilities.items()
                if self.manhattan_dist(self.bot_loc, cell) >= dist
            }
        else:
            
            self.rat_detection_probabilities = {
                cell: prob for cell, prob in self.rat_detection_probabilities.items()
                if self.manhattan_dist(self.bot_loc, cell) <= dist
            }
        
        
        print(f"Filtered Rat Knowledge Base (dist {'>=' if greater_than else '<='} {dist}): {self.rat_detection_probabilities}")

    def modify_goal_cells(self, new_bot_loc):
        """Update detection probabilities based on a new bot loc."""
        self.bot_loc = new_bot_loc  # Updating bots location
        modifyd_probs = {}
        for cell in self.rat_detection_probabilities:
            dist = self.manhattan_dist(new_bot_loc, cell)
            probability = math.exp(-(ALPHA * (dist - 1)))
            modifyd_probs[cell] = probability
        self.rat_detection_probabilities = modifyd_probs
        print(f"Updated Rat Knowledge Base: {self.rat_detection_probabilities}")

    def highest_probability_ping(self, bot_loc, rat_loc):
        dist = self.manhattan_dist(bot_loc, rat_loc)
        return math.exp(-(ALPHA * (dist - 1)))

