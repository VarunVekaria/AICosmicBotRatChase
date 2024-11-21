import random



class ShipEnvironment:
    def __init__(self, size):
        self.size = size
        self.matrix = self.generate_blocked_cells()
        self.block_outer_edges()  # Block all edges of the matrix initially
        self.open_cells()  # Open cells, excluding outer edge
        self.dead_ends = self.identify_dead_ends()
        self.open_closed_neighbors()

    def generate_blocked_cells(self):
        return [[1 for _ in range(self.size)] for _ in range(self.size)]

    def get_neighbor_cells(self, row, col):
        possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbors = []
        for dr, dc in possible_moves:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                neighbors.append((nr, nc))
        return neighbors

    def open_cells(self):
        row, col = random.randint(1, self.size - 2), random.randint(1, self.size - 2)
        self.matrix[row][col] = 0  # 0 represents open

        while True:
            valid_cells = []
            for r in range(1, self.size - 1):  # excluding outer edge so that infinity loop doesnt exist
                for c in range(1, self.size - 1):
                    if self.matrix[r][c] == 1 and len(
                        [n for n in self.get_neighbor_cells(r, c) if self.matrix[n[0]][n[1]] == 0]
                    ) == 1:
                        valid_cells.append((r, c))

            if not valid_cells:
                break

            r, c = random.choice(valid_cells)
            self.matrix[r][c] = 0

    def identify_dead_ends(self):
     
        dead_ends = []
        for r in range(1, self.size - 1):  # excluding outer edge so that infinity loop doesnt exist
            for c in range(1, self.size - 1):
                if self.matrix[r][c] == 0 and len(
                    [n for n in self.get_neighbor_cells(r, c) if self.matrix[n[0]][n[1]] == 0]
                ) == 1:
                    dead_ends.append((r, c))
        return dead_ends

    def open_closed_neighbors(self):
        for dead_end in self.dead_ends:
            neighbors = self.get_neighbor_cells(dead_end[0], dead_end[1])
            closed_neighbors = [(r, c) for r, c in neighbors if 1 <= r < self.size - 1 and 1 <= c < self.size - 1 and self.matrix[r][c] == 1]

            if closed_neighbors:
                neighbor_to_open = random.choice(closed_neighbors)
                self.matrix[neighbor_to_open[0]][neighbor_to_open[1]] = 0  

    def block_outer_edges(self):
        for i in range(self.size):
            self.matrix[0][i] = 1              # Top edge
            self.matrix[self.size - 1][i] = 1   # Bottom edge
            self.matrix[i][0] = 1              # Left edge
            self.matrix[i][self.size - 1] = 1   # Right edge


    def position_random_open_cell(self, avoid_cells=[]):
        open_cells = [(r, c) for r in range(1, self.size - 1) for c in range(1, self.size - 1)
                      if self.matrix[r][c] == 0 and (r, c) not in avoid_cells]
        if not open_cells:
            return None
        return random.choice(open_cells)

