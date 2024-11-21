import math



class RatKnowledgeBase:
    def __init__(self, environment, bot_loc, alpha=0.5):
        self.environment = environment
        self.bot_loc = bot_loc
        self.alpha = alpha
        self.rat_detection_probabilities = self.calc_detection_probabilities()

    def manhattan_dist(self, pos1, pos2):
        """Calculate the Manhattan dist between two locs."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def calc_detection_probabilities(self):
        """Calculate and store the probability of detecting a ping for each open cell."""
        detection_probs = {}
        for r in range(1, self.environment.size - 1):
            for c in range(1, self.environment.size - 1):
                if self.environment.matrix[r][c] == 0:  
                    dist = self.manhattan_dist(self.bot_loc, (r, c))
                    probability = math.exp(-(self.alpha * (dist - 1)))
                    detection_probs[(r, c)] = probability
                    # print(f"Calculated ping detection probability at {(r, c)}: {probability}")
        return detection_probs
    
    def filter_to_goal_cells(self, goal_cells):
        """Filter rat detection probabilities to include only the goal cells."""
        self.rat_detection_probabilities = {cell: prob for cell, prob in self.rat_detection_probabilities.items() if cell in goal_cells}
        print(f"Rat Knowledge Base modifyd with goal cells: {self.rat_detection_probabilities}")

    def modify_goal_cells(self, new_bot_loc):
        """Update detection probabilities for only the goal cells based on the bot's new loc."""
        modifyd_probs = {}
        for cell in self.rat_detection_probabilities:
            dist = self.manhattan_dist(new_bot_loc, cell)
            probability = math.exp(-(self.alpha * (dist - 1)))
            modifyd_probs[cell] = probability
            # print(f"Updated ping detection probability at {cell}: {probability}")
        self.rat_detection_probabilities = modifyd_probs
 