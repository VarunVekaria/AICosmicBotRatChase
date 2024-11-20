class KnowledgeBase:
    def __init__(self, env):
        self.env = env
        # Initialize with all open cells and their open neighbor configurations (E, W, N, S)
        self.open_cells_info = self.initialize_open_cells_info()
        self.possible_positions = set(self.open_cells_info.keys())  # All open cells are initially possible positions

    def initialize_open_cells_info(self):
        """Initialize each open cell with its neighbor open/closed configuration."""
        open_cells_info = {}
        for r in range(1, self.env.size - 1):  # Avoid outer edge
            for c in range(1, self.env.size - 1):
                if self.env.matrix[r][c] == 0:  # Only consider open cells
                    open_cells_info[(r, c)] = self.get_open_neighbors(r, c)
        return open_cells_info

    def get_open_neighbors(self, row, col):
        """Return a tuple representing open neighbors in (E, W, N, S) format."""
        directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]  # East, West, North, South
        neighbors = []
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.env.size and 0 <= nc < self.env.size:
                neighbors.append(1 if self.env.matrix[nr][nc] == 0 else 0)
            else:
                neighbors.append(0)  # Edge is treated as closed
        return tuple(neighbors)  # (E, W, N, S)

    def filter_positions(self, sensed_directions):
        """Filter possible positions based on the current sensed directions (E, W, N, S)."""
        self.possible_positions = {
            pos for pos in self.possible_positions if self.open_cells_info[pos] == sensed_directions
        }
        print(f"Knowledge Base update: Remaining possible positions: {self.possible_positions}")

    def calculate_direction_probabilities(self):
        """Calculate the probability of each direction (E, W, N, S) based on remaining positions."""
        direction_counts = [0, 0, 0, 0]  # E, W, N, S
        for pos in self.possible_positions:
            for i, open_state in enumerate(self.open_cells_info[pos]):
                direction_counts[i] += open_state

        # Normalize to probabilities
        total_open = sum(direction_counts)
        if total_open == 0:  # No direction to move
            return None

        return [count / total_open for count in direction_counts]  # Probabilities for E, W, N, S

    def update_possible_positions(self, dr, dc):
        """Update each cell in possible_positions by attempting to move in the bot's direction."""
        new_possible_positions = set()
        
        for pos in self.possible_positions:
            new_pos = (pos[0] + dr, pos[1] + dc)
            # Check if new position is within bounds and open
            if 0 <= new_pos[0] < self.env.size and 0 <= new_pos[1] < self.env.size:
                if self.env.matrix[new_pos[0]][new_pos[1]] == 0:  # Only retain open cells
                    new_possible_positions.add(new_pos)
        
        self.possible_positions = new_possible_positions
        print(f"Knowledge Base update: Remaining possible positions after bot move: {self.possible_positions}")

    def enforce_stricter_filtering(self, oscillating_position):
        """Apply stricter filtering by removing the oscillating position from possible positions."""
        # Remove the oscillating position to prevent the bot from revisiting it
        if oscillating_position in self.possible_positions:
            self.possible_positions.remove(oscillating_position)
            print(f"Stricter filtering applied. Removed oscillating position: {oscillating_position}")
        print(f"Knowledge Base update after stricter filtering: {self.possible_positions}")


