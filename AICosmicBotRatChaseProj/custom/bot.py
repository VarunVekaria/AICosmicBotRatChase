import random


class Bot:
    def __init__(self, environment, knowledge_base):
        self.environment = environment
        self.kbase = knowledge_base
        self.loc = random.choice(list(self.kbase.poss_locs))  #Bot initialised at a random position on our grid.
        print(self.loc)
        self.prev_hist = []  
        self.recent_locs = []  
        self.goal_path = []  
        self.rat_kbase = None 

    def set_goal_path(self, path, rat_kbase):
        #Updating the path the bot will take and then updating the knowledge base too
        self.goal_path = path
        self.rat_kbase = rat_kbase  
        print(f"Bot set to follow path to goal cell: {path}")

    def move_to_goal(self):
        #Moving the bot based on path 
        if self.goal_path and self.goal_path[0] == self.loc:
            self.goal_path.pop(0)

    
        if self.goal_path:
            next_loc = self.goal_path.pop(0)  
            self.loc = next_loc  # Update bot's location
            self.prev_hist.append(self.loc)
            # Update RatKnowledgeBase with the new bots location, considering  only goal cells
            if self.rat_kbase:
                self.rat_kbase.modify_goal_cells(self.loc)
        else:
            print("Target path completed.")
            self.goal_path = None  
            
    def sense_possible_moves(self):
        """Sense which neighboring cells are open in (E, W, N, S) format."""
        r, c = self.loc
        possible_moves = self.kbase.get_open_neighbors(r, c)
        # print(f"Sensed possible_moves at {self.loc}: {possible_moves}")
        return possible_moves

    def move(self):
        probabilities = self.kbase.calc_dir_probabilities()
        if probabilities is None:
            print("No available moves. Stopping.")
            return False  

        
        possible_moves_map = [(0, 1), (0, -1), (-1, 0), (1, 0)]  # E, W, N, S

        # Choose a direction based on the probabilities
        chosen_dir_idx = random.choices(range(4), weights=probabilities, k=1)[0]
        dr, dc = possible_moves_map[chosen_dir_idx]
        new_loc = (self.loc[0] + dr, self.loc[1] + dc)

        
        if (0 <= new_loc[0] < self.environment.size and
            0 <= new_loc[1] < self.environment.size and
            self.environment.matrix[new_loc[0]][new_loc[1]] == 0):
            
            
            self.loc = new_loc
            self.prev_hist.append(self.loc)
            self.modify_recent_locs(new_loc)
            print(f"Bot moved to {self.loc}")

            # Update Knowledge Base locs
            self.kbase.modify_poss_locs(dr, dc)
            return True  # Move successful

        print("Bot could not move in the chosen direction.")
        return False

    def modify_recent_locs(self, new_loc):
        
        self.recent_locs.append(new_loc)
        if len(self.recent_locs) > 2:
            self.recent_locs.pop(0)

        
        if len(self.recent_locs) == 2 and self.recent_locs[0] == self.recent_locs[1]:
            
            self.kbase.enforce_stricter_filtering(self.recent_locs[0])

