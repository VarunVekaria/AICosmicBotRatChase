import random


class Bot:
    def __init__(self, env, knowledge_base):
        self.env = env
        self.kb = knowledge_base
        self.position = random.choice(list(self.kb.possible_positions))  # Starting from an unknown open cell
        print(self.position)
        self.history = []  # Track previously visited cells to refine position
        self.recent_positions = []  # Track last two positions for loop detection
        self.target_path = []  # Store the path to the selected target cell
        self.rat_kb = None 

    def set_target_path(self, path, rat_kb):
        """Set the path the bot will follow to reach the target cell and assign the RatKnowledgeBase."""
        self.target_path = path
        self.rat_kb = rat_kb  # Store reference to the rat's knowledge base for updates
        print(f"Bot set to follow path to target cell: {path}")

    def move_to_target(self):
        """Move the bot one step along the target path and update RatKnowledgeBase."""
        if self.target_path and self.target_path[0] == self.position:
            self.target_path.pop(0)

    # Now move to the next step in the path, if available
        if self.target_path:
            next_position = self.target_path.pop(0)  # Get the next step in the path
            self.position = next_position  # Update bot's position
            self.history.append(self.position)
            # Update RatKnowledgeBase with the new position, only considering target cells
            if self.rat_kb:
                self.rat_kb.update_target_cells(self.position)
        else:
            print("Target path completed.")
            self.target_path = None  # Clear the path once the bot reaches the target
            
    def sense_directions(self):
        """Sense which neighboring cells are open in (E, W, N, S) format."""
        r, c = self.position
        directions = self.kb.get_open_neighbors(r, c)
        # print(f"Sensed directions at {self.position}: {directions}")
        return directions

    def move(self):
        probabilities = self.kb.calculate_direction_probabilities()
        if probabilities is None:
            print("No available moves. Stopping.")
            return False  # No movement possible

        # Map directions to their respective movement deltas
        directions_map = [(0, 1), (0, -1), (-1, 0), (1, 0)]  # E, W, N, S

        # Choose a direction based on the probabilities
        chosen_direction_index = random.choices(range(4), weights=probabilities, k=1)[0]
        dr, dc = directions_map[chosen_direction_index]
        new_position = (self.position[0] + dr, self.position[1] + dc)

        # Check if the selected direction leads to an open cell
        if (0 <= new_position[0] < self.env.size and
            0 <= new_position[1] < self.env.size and
            self.env.matrix[new_position[0]][new_position[1]] == 0):
            
            # Move to the new position
            self.position = new_position
            self.history.append(self.position)
            self.update_recent_positions(new_position)
            print(f"Bot moved to {self.position}")

            # Update Knowledge Base positions
            self.kb.update_possible_positions(dr, dc)
            return True  # Move successful

        print("Bot could not move in the chosen direction.")
        return False

    def update_recent_positions(self, new_position):
        """Update recent positions list and check for oscillation."""
        # Maintain only the last two positions
        self.recent_positions.append(new_position)
        if len(self.recent_positions) > 2:
            self.recent_positions.pop(0)

        # Check if oscillating between two positions
        if len(self.recent_positions) == 2 and self.recent_positions[0] == self.recent_positions[1]:
            # print("Detected oscillation between positions, enforcing stricter filtering.")
            self.kb.enforce_stricter_filtering(self.recent_positions[0])


