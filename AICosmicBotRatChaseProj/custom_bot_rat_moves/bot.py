import random


class Bot:
    def __init__(self, environment, knowledge_base):
        self.environment = environment
        self.kbase = knowledge_base
        self.loc = random.choice(list(self.kbase.eligible_locs))  # Starting from an unknown open cell
        print(self.loc)
        self.prev_history = []  # Track previously visited cells to refine loc
        self.recent_locs = []  # Track last two locs for loop detection
        self.goal_path = []  # Store the path to the selected goal cell
        self.rat_kbase = None 

    def set_goal_path(self, path, rat_kbase):
        """Set the path the bot will follow to reach the goal cell and assign the RatKnowledgeBase."""
        self.goal_path = path
        self.rat_kbase = rat_kbase  # Store reference to the rat's knowledge base for modifys
        print(f"Bot set to follow path to goal cell: {path}")

    def move_to_goal(self):
        """Move the bot one step along the goal path and modify RatKnowledgeBase."""
        if self.goal_path and self.goal_path[0] == self.loc:
            self.goal_path.pop(0)

    # Now move to the next step in the path, if available
        if self.goal_path:
            next_loc = self.goal_path.pop(0)  # Get the next step in the path
            self.loc = next_loc  # Update bot's loc
            self.prev_history.append(self.loc)
            # Update RatKnowledgeBase with the new loc, only considering goal cells
            if self.rat_kbase:
                self.rat_kbase.modify_goal_cells(self.loc)
        else:
            print("Target path completed.")
            self.goal_path = None  # Clear the path once the bot reaches the goal
            
    def sense_directions(self):
        """Sense which neighboring cells are open in (E, W, N, S) format."""
        r, c = self.loc
        directions = self.kbase.get_open_neighbors(r, c)
        # print(f"Sensed directions at {self.loc}: {directions}")
        return directions

    def move(self):
        probabilities = self.kbase.calculate_dir_probabilities()
        if probabilities is None:
            print("No available moves. Stopping.")
            return False  # No movement eligible

        # Map directions to their respective movement deltas
        directions_map = [(0, 1), (0, -1), (-1, 0), (1, 0)]  # E, W, N, S

        # Choose a direction based on the probabilities
        chosen_dir_index = random.choices(range(4), weights=probabilities, k=1)[0]
        dr, dc = directions_map[chosen_dir_index]
        new_loc = (self.loc[0] + dr, self.loc[1] + dc)

        # Check if the selected direction leads to an open cell
        if (0 <= new_loc[0] < self.environment.size and
            0 <= new_loc[1] < self.environment.size and
            self.environment.matrix[new_loc[0]][new_loc[1]] == 0):
            
            # Move to the new loc
            self.loc = new_loc
            self.prev_history.append(self.loc)
            self.modify_recent_locs(new_loc)
            print(f"Bot moved to {self.loc}")

            # Update Knowledge Base locs
            self.kbase.modify_eligible_locs(dr, dc)
            return True  # Move successful

        print("Bot could not move in the chosen direction.")
        return False

    def modify_recent_locs(self, new_loc):
        """Update recent locs list and check for oscillation."""
        # Maintain only the last two locs
        self.recent_locs.append(new_loc)
        if len(self.recent_locs) > 2:
            self.recent_locs.pop(0)

        # Check if oscillating between two locs
        if len(self.recent_locs) == 2 and self.recent_locs[0] == self.recent_locs[1]:
            # print("Detected oscillation between locs, enforcing stricter filtering.")
            self.kbase.enforce_stricter_filtering(self.recent_locs[0])


