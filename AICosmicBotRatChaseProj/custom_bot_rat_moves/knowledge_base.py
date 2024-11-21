class KnowledgeBase:
    def __init__(self, environment):
        self.environment = environment
        # Initialize with all open cells and their open neighbor configurations (E, W, N, S)
        self.open_cells_data = self.initialize_open_cells_data()
        self.eligible_locs = set(self.open_cells_data.keys())  # All open cells are initially eligible locs

    def initialize_open_cells_data(self):
        """Initialize each open cell with its neighbor open/closed configuration."""
        open_cells_data = {}
        for r in range(1, self.environment.size - 1):  # Avoid outer edge
            for c in range(1, self.environment.size - 1):
                if self.environment.matrix[r][c] == 0:  # Only consider open cells
                    open_cells_data[(r, c)] = self.get_open_neighbors(r, c)
        return open_cells_data

    def get_open_neighbors(self, row, col):
        """Return a tuple representing open neighbors in (E, W, N, S) format."""
        directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]  # East, West, North, South
        neighbors = []
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.environment.size and 0 <= nc < self.environment.size:
                neighbors.append(1 if self.environment.matrix[nr][nc] == 0 else 0)
            else:
                neighbors.append(0)  # Edge is treated as closed
        return tuple(neighbors)  # (E, W, N, S)

    def filter_locs(self, sensed_directions):
        """Filter eligible locs based on the current sensed directions (E, W, N, S)."""
        self.eligible_locs = {
            pos for pos in self.eligible_locs if self.open_cells_data[pos] == sensed_directions
        }
        print(f"Knowledge Base modify: Remaining eligible locs: {self.eligible_locs}")

    def calculate_dir_probabilities(self):
        """Calculate the probability of each direction (E, W, N, S) based on remaining locs."""
        dir_counts = [0, 0, 0, 0]  # E, W, N, S
        for pos in self.eligible_locs:
            for i, open_positions in enumerate(self.open_cells_data[pos]):
                dir_counts[i] += open_positions

        # Normalize to probabilities
        total_open = sum(dir_counts)
        if total_open == 0:  # No direction to move
            return None

        return [count / total_open for count in dir_counts]  # Probabilities for E, W, N, S

    def modify_eligible_locs(self, dr, dc):
        """Update each cell in eligible_locs by attempting to move in the bot's direction."""
        new_eligible_locs = set()
        
        for pos in self.eligible_locs:
            new_pos = (pos[0] + dr, pos[1] + dc)
            # Check if new loc is within bounds and open
            if 0 <= new_pos[0] < self.environment.size and 0 <= new_pos[1] < self.environment.size:
                if self.environment.matrix[new_pos[0]][new_pos[1]] == 0:  # Only retain open cells
                    new_eligible_locs.add(new_pos)
        
        self.eligible_locs = new_eligible_locs
        print(f"Knowledge Base modify: Remaining eligible locs after bot move: {self.eligible_locs}")

    def enforce_stricter_filtering(self, oscillating_loc):
        """Apply stricter filtering by removing the oscillating loc from eligible locs."""
        # Remove the oscillating loc to prevent the bot from revisiting it
        if oscillating_loc in self.eligible_locs:
            self.eligible_locs.remove(oscillating_loc)
            print(f"Stricter filtering applied. Removed oscillating loc: {oscillating_loc}")
        print(f"Knowledge Base modify after stricter filtering: {self.eligible_locs}")


