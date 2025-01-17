import math



class RatKnowledgeBase:
    def __init__(self, environment, bot_loc, alpha=0.5):
        self.environment = environment
        self.bot_loc = bot_loc
        self.alpha = alpha
        self.rat_detection_probabilities = self.calc_detection_probabilities()

    def manhattan_dist(self, pos1, pos2):
        #Calculating manhattan distance between two points
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def calc_detection_probabilities(self):
        #Clculating rat detectors proabbaility for possible cells 
        detection_probs = {}
        for r in range(1, self.environment.size - 1):
            for c in range(1, self.environment.size - 1):
                if self.environment.matrix[r][c] == 0:   
                    # Calculate detection probability based on dist from the bot
                    dist = self.manhattan_dist(self.bot_loc, (r, c))
                    probability = math.exp(-(self.alpha * (dist - 1)))
                    detection_probs[(r, c)] = probability

                    
                    open_neighbors = self.get_open_neighbors((r, c))
                    for neighbor in open_neighbors:
                        if neighbor not in detection_probs:
                            neighbor_dist = self.manhattan_dist(self.bot_loc, neighbor)
                            neighbor_prob = math.exp(-(self.alpha * (neighbor_dist - 1)))
                            detection_probs[neighbor] = neighbor_prob

        return detection_probs

    def get_open_neighbors(self, cell):
        #Get all open cells for a given cell.
        neighbors = self.environment.get_neighbor_cells(cell[0], cell[1])
        return [(r, c) for r, c in neighbors if self.environment.matrix[r][c] == 0]

    def filter_to_goal_cells(self, goal_cells):
        #filtering
        filtered_probs = {}
        for cell in goal_cells:
            filtered_probs[cell] = self.rat_detection_probabilities.get(cell, 0)
            for neighbor in self.get_open_neighbors(cell):
                filtered_probs[neighbor] = self.rat_detection_probabilities.get(neighbor, 0)

        self.rat_detection_probabilities = filtered_probs
        print(f"Rat Knowledge Base updated with goal cells and neighbors: {self.rat_detection_probabilities}")

    def modify_goal_cells(self, new_bot_loc):
        #Updating probabilities
        modifyd_probs = {}
        for cell in self.rat_detection_probabilities:
            dist = self.manhattan_dist(new_bot_loc, cell)
            probability = math.exp(-(self.alpha * (dist - 1)))
            modifyd_probs[cell] = probability
        self.rat_detection_probabilities = modifyd_probs

    