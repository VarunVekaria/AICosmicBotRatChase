class KnowledgeBase:
    def __init__(self, environment):
        self.environment = environment
        # considering all open cells 
        self.open_cells_data = self.initialize_open_cells_data()
        self.poss_locs = set(self.open_cells_data.keys())  

    def initialize_open_cells_data(self):
        open_cells_data = {}
        for r in range(1, self.environment.size - 1):  # here we try to avoid the outer edge
            for c in range(1, self.environment.size - 1):
                if self.environment.matrix[r][c] == 0:  
                    open_cells_data[(r, c)] = self.get_open_neighbors(r, c)
        return open_cells_data

    def get_open_neighbors(self, row, col):
        
        possible_moves = [(0, 1), (0, -1), (-1, 0), (1, 0)]  # possible moves in East, west, north, South direction
        neighbors = []
        for dr, dc in possible_moves:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.environment.size and 0 <= nc < self.environment.size:
                neighbors.append(1 if self.environment.matrix[nr][nc] == 0 else 0)
            else:
                neighbors.append(0)  # Edge is treated as closed
        return tuple(neighbors)  # (E, W, N, S)

    def filter_locs(self, sensed_possible_moves):
        """Filter poss locs based on the current sensed possible_moves (E, W, N, S)."""
        self.poss_locs = {
            pos for pos in self.poss_locs if self.open_cells_data[pos] == sensed_possible_moves
        }
        print(f"Knowledge Base modify: Remaining poss locs: {self.poss_locs}")

    def calc_dir_probabilities(self):
        """Calculate the probability of each direction (E, W, N, S) based on remaining locs."""
        dir_counts = [0, 0, 0, 0]  # E, W, N, S
        for pos in self.poss_locs:
            for i, open_positions in enumerate(self.open_cells_data[pos]):
                dir_counts[i] += open_positions

        # Normalize to probabilities
        total_open = sum(dir_counts)
        if total_open == 0:  # No direction to move
            return None

        return [count / total_open for count in dir_counts]  # Probabilities for E, W, N, S

    def modify_poss_locs(self, dr, dc):
        """Update each cell in poss_locs by attempting to move in the bot's direction."""
        new_poss_locs = set()
        
        for pos in self.poss_locs:
            new_pos = (pos[0] + dr, pos[1] + dc)
            # Check if new loc is within bounds and open
            if 0 <= new_pos[0] < self.environment.size and 0 <= new_pos[1] < self.environment.size:
                if self.environment.matrix[new_pos[0]][new_pos[1]] == 0:  # Only retain open cells
                    new_poss_locs.add(new_pos)
        
        self.poss_locs = new_poss_locs
        print(f"Knowledge Base modify: Remaining poss locs after bot move: {self.poss_locs}")

    def enforce_stricter_filtering(self, oscillating_loc):
        """Apply stricter filtering by removing the oscillating loc from poss locs."""
        # Remove the oscillating loc to prevent the bot from revisiting it
        if oscillating_loc in self.poss_locs:
            self.poss_locs.remove(oscillating_loc)
            print(f"Stricter filtering applied. Removed oscillating loc: {oscillating_loc}")
        print(f"Knowledge Base modify after stricter filtering: {self.poss_locs}")


