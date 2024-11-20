import random
import pygame

from rat_knowledge_base import RatKnowledgeBase
from rat import Rat
from ship_environment_logic import ShipEnvironment

from collections import deque
class Bot:
    def __init__(self, env, knowledge_base):
        self.env = env
        self.kb = knowledge_base
        self.position = random.choice(list(self.kb.possible_positions))
        self.history = []
        self.recent_positions = deque(maxlen=20)
        self.target_path = []
        self.rat_kb = None

    def set_target_path(self, path, rat_kb):
        self.target_path = path
        self.rat_kb = rat_kb
        print(f"Bot set to follow path to target cell: {path}")

    def move_to_target(self):
        if self.target_path:
            next_position = self.target_path.pop(0)
            self.position = next_position
            self.history.append(self.position)
            self.recent_positions.append(self.position)  # Diff
            print(f"Bot moved to {self.position} along the target path.")
            if self.rat_kb:
                self.rat_kb.update_target_cells(self.position)

    def detect_osc(self):
        # Check if recent positions contain a repeating pattern
        if len(set(self.recent_positions)) <= 4:
            print("oscccccccccc")
            return True
        return False
    
    def force_move_out_of_osc(self, simulation, screen, clock):

        # Get all open cells within the grid
        open_cells = [(r, c) for r in range(1, self.env.size - 1) for c in range(1, self.env.size - 1)
                      if self.env.matrix[r][c] == 0 and (r, c) not in self.recent_positions]

        if open_cells:
            # Choose a cell that's not in recent positions
            chosen_cell = random.choice(open_cells)
            path_to_chosen_cell = simulation.bfs_path(self.position, chosen_cell)
            print(f"printingggg{path_to_chosen_cell}")

            if path_to_chosen_cell:
                # Move several steps along this path to break out of the loop
                steps_to_move = min(3, len(path_to_chosen_cell) - 1)  # Take up to 3 steps or the full path length
                
                for step in range(1, steps_to_move + 1):
                    self.position = path_to_chosen_cell[step]
                    self.history.append(self.position)
                    self.recent_positions.append(self.position)
                    
                    # Update the display after each step
                    simulation.draw_grid(screen)
                    pygame.display.flip()
                    clock.tick(10)  # Adjust speed as needed


    def sense_directions(self):
        r, c = self.position
        return self.kb.get_open_neighbors(r, c)

    def move(self):
        probabilities = self.kb.calculate_direction_probabilities()
        if probabilities is None:
            print("No available moves. Stopping.")
            return False
        directions_map = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        chosen_direction_index = random.choices(range(4), weights=probabilities, k=1)[0]
        dr, dc = directions_map[chosen_direction_index]
        new_position = (self.position[0] + dr, self.position[1] + dc)
        if (0 <= new_position[0] < self.env.size and
            0 <= new_position[1] < self.env.size and
            self.env.matrix[new_position[0]][new_position[1]] == 0):
            self.position = new_position
            self.history.append(self.position)
            print(f"Bot moved to {self.position}")
            self.kb.update_possible_positions(dr, dc)
            return True
        print("Bot could not move in the chosen direction.")
        return False